from pymongo import MongoClient
from pymongo.errors import AutoReconnect
from socket import gethostname, gethostbyname
from time import sleep
import requests
import os

def get_connection_string_from_file(filename = None):
    '''
    Gets the connection string from a file. 
    Default is connection_string.txt located in the local directory
    Inputs:
        filename: Optional; location to search for connection string
    Returns:
        connection_string: The mongo connection string stored in filename
    '''
    if filename is None:
        filename = "connection_string.txt"
    connection_string = ""
    with open(filename) as connection_string_file:
        for line in connection_string_file: # this will get only the last line
            connection_string = line
    return connection_string

def get_connection_string_from_uri(uri = None):
    '''
    Gets the connection string from github.
    Inputs:
        uri: Optional; URI to search for connection string
    Returns:
        connection_string: The mongo connection string stored in filename
    ******NEEDS TO BE TESTED******
    '''
    if uri is None:
        uri = "https://raw.githubusercontent.com/executivereader/mongo-startup/master/connection_string.txt"
    connection_string = ""
    remote = requests.get(uri)
    for line in remote: # this will get only the last line
        connection_string = line
    return connection_string

def start_mongo_client(filename = None, uri = None):
    '''
    Tries to get a MongoClient
    First tries the connection string in the local file
    Next tries the connection string on github
    Inputs:
        filename: Optional; filename to look for connection string in
        uri: Optional; URI to look for connection string in
    '''
    connection_string = get_connection_string_from_file(filename)
    try:
        client = MongoClient(connection_string)
    except Exception:
        connection_string = get_connection_string_from_uri(uri)
        client = MongoClient(connection_string)
    return client

def member_of_replica_set(client, hostname = None, port = None):
    '''
    Checks if hostname:port is in the replica set connected to from connection_string
    Inputs:
        client: a MongoClient instance
        hostname: Optional; hostname or IP address (default: socket.gethostbyname(socket.gethostname()))
        port: Optional; defaults to 27017
    Returns:
        True if hostname:port is in the replica set
        False otherwise
    '''
    if hostname is None:
        hostname = gethostbyname(gethostname())
    if port is None:
        port = 27017
    replset_config = client.local.system.replset.find_one()
    for replset_member in replset_config['members']:
        if replset_member['host'] ==  gethostbyname(gethostname()) + ':27017':
            return True
    return False

def get_available_host_id(client):
    '''
    Gets an id that is available for adding a member to a replica set.
    Inputs:
        client: a MongoClient instance
    Returns:
        new_member_id: the smallest integer that is an available id
    '''
    replset_config = client.local.system.replset.find_one()
    new_member_id = 1
    id_not_ok = True
    while id_not_ok:
        id_not_ok = False
        for replset_member in replset_config['members']:
            if replset_member['_id'] == new_member_id:
                new_member_id = new_member_id + 1
                id_not_ok = True
    return new_member_id

def add_member_to_replica_set(client, hostname = None, port = None, force = None):
    '''
    Adds a member to the replica set. 
    Will not add if the hostname is already in the replset.
    Inputs: 
        client: a MongoClient instance
        hostname: Optional; hostname or IP address (default socket.gethostbyname(socket.gethostname()))
        port: Optional; defaults to 27017
        force: Optional; defaults to False
    Returns:
        True if hostname:port appears in the replica set configuration after the function runs
        False otherwise
    '''
    if hostname is None:
        hostname = gethostbyname(gethostname())
    if port is None:
        port = 27017
    if force is None:
        force = False
    new_member_hostname = hostname + ':' + str(port)
    if not member_of_replica_set(client,hostname,port):
        replset_config = client.local.system.replset.find_one()
        replset_config['members'].append({u'host': hostname + ':' + str(port), u'_id': get_available_host_id(client)})
        replset_config['version'] = replset_config['version'] + 1
        client.admin.command({'replSetReconfig': replset_config}, force = force)
    return member_of_replica_set(client,hostname,port)

def get_connection_string(client, options = None):
    '''
    Gets a connection string that will work for an existing replica set
    Inputs:
        client: a MongoClient instance
        options: Optional; string to add to the end of the connection string
    '''
    connection_string = "mongodb://"
    replset_status = client.admin.command({'replSetGetStatus': 1})
    num_members = 0
    for replset_member in replset_status['members']:
        if num_members > 0:
            connection_string = connection_string + ","
        connection_string = connection_string + replset_member['name']
        num_members = num_members + 1
    connection_string = connection_string + "/?replicaSet=" + replset_status['set']
    if options is not None:
        connection_string = connection_string + "&" + options
    return connection_string

def remove_unhealthy_member_from_config(client, not_ok = None):
    '''
    Removes the unhealthy member with the smallest id from the replica set config
    Inputs:
        client: a MongoClient instance
        not_ok: Optional; if True, will remove member even if replset is not in an ok status
    Returns:
        replset_config: a replica set configuration modified by removing an unhealthy member
    '''
    replset_status = client.admin.command({'replSetGetStatus': 1})
    replset_config = client.local.system.replset.find_one()
    if replset_status['ok'] == 1.0 or not_ok is True:
        for replset_member in replset_status['members']:
            if replset_member['state'] in [8]:
                for removal_candidate in replset_config['members']:
                    if removal_candidate['_id'] == replset_member['_id']:
                        if removal_candidate['host'] == replset_member['name']:
                            replset_config['members'].remove(removal_candidate)
                            replset_config['version'] = replset_config['version'] + 1
                            return replset_config
    return None

def count_members_in_config(replset_config):
    '''
    Returns the number of members in a replica set config
    Inputs:
        replset_config: The replica set config
    '''
    return len(replset_config['members'])

def update_local_connection_string(connection_string, filename = None):
    '''
    Modifies a local file to put a new connection string in there
    Inputs:
        connection_string: a valid mongo connection string
        filename: Optional; the local filename
    Returns:
        True
    '''
    if filename is None:
        filename =  "connection_string.txt"
    with open(filename, 'r+') as local_connection_string_file:
        local_connection_string_file.seek(0)
        local_connection_string_file.write(connection_string)
        local_connection_string_file.truncate()
    return True

def push_local_connection_string_to_github(client, filename = None):
    '''
    Pushes the local connection string file to github
    '''
    if filename is None:
        filename = "connection_string.txt"
    os.system("git config --global user.name 'executivereader'")
    os.system("git config --global user.email 'executivereader@users.noreply.github.com'")
    os.system("git add " + filename)
    os.system("git commit -m 'AUTO: updated connection string'")
    credentials = client.credentials.github.find_one()
    os.system("git push --repo https://" + 
          credentials['username'] + ":" + credentials['password'] + 
          "@github.com/executivereader/mongo-startup.git")

if __name__ == "__main__":
    # now add self to the replica set
    max_tries = 5
    client = start_mongo_client()
    idx = 0
    self_not_added = True
    while idx < max_tries and self_not_added:
        sleep(5)
        try:
            self_not_added = not add_member_to_replica_set(client)
        except Exception:
            print "Unable to add self to replica set on try " + str(idx + 1)
            sleep(25)
        idx = idx + 1
    if member_of_replica_set(client):
        print "Self is in the replica set as of try " + str(idx)
        # update connection string here
        connection_string = get_connection_string(client)
        print "New connection string is:\n" + connection_string
        sleep(120)
        # now delete any members that are in an unreachable status
        if connection_string is not "":
            print "Reconnecting to " + connection_string
            client = MongoClient(connection_string)
            max_members_to_remove = 1
            min_members_in_replica_set = 3
            members_removed = 0
            new_replset_config = remove_unhealthy_member_from_config(client)
            while new_replset_config is not None and members_removed < max_members_to_remove and count_members_in_config(new_replset_config) >= min_members_in_replica_set:
                try:
                    client.admin.command({'replSetReconfig': new_replset_config}, force = False)
                except AutoReconnect:
                    print "Connection closed; auto-reconnecting"
                print "Removed a member from the replica set"
                members_removed = members_removed + 1
                new_replset_config = remove_unhealthy_member_from_config(client)
                sleep(30)
    else:
        print "Failed to add self to replica set after " + str(idx) + " tries"
    # update with the latest connection string
    connection_string = get_connection_string(client)
    update_local_connection_string(connection_string)
    push_local_connection_string_to_github(client)

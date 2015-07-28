# code here
import xmltodict
import os
from update_replica_set import start_mongo_client
from time import sleep
from pymongo.errors import DuplicateKeyError

def upload_all_documents_to_mongo(path, client):
    """
    Uploads all documents in path to Mongo.
    Inputs:
        path: a string with the path in which to find the XML documents
        client: a pymongo MongoClient (preferably returned by update_replica_set.start_mongo_client())
    Returns:
        None
    """
    filenames = os.listdir(path)
    for filename in filenames:
        if os.path.isfile(path + filename):
            success = False
            with open(path + filename) as infile:
                filedict = xmltodict.parse(infile)
                try:
                    success = client.tr.articles.insert(filedict)
                except DuplicateKeyError as dup:
                    print "Already in database: " + filename
                    os.remove(path + filename)
                except Exception as exc:
                    print exc
                    filenames.remove(filename)
            if success:
                print "Successfully inserted " + filename
                os.remove(path + filename)
            else:
                print "Unable to insert file " + filename

if __name__ == "__main__":
    path = "/home/ubuntu/output/Reuters World Service/"
    client = start_mongo_client()
    while 1:
        sleep(5)
        try:
            upload_all_documents_to_mongo(path, client)
        except Exception as exc:
            print exc

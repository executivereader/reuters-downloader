# code here
import xmltodict
import os
from update_replica_set import start_mongo_client

def upload_all_documents_to_mongo(path, client):
    """
    Uploads all documents in path to Mongo.
    Inputs:
        path: a string with the path in which to find the XML documents
        client: a pymongo MongoClient (preferably returned by update_replica_set.start_mongo_client())
    Returns:
        None
    """
    for filename in os.listdir(path):
        if os.path.isfile(path + filename):
            success = False
            with open(path + filename) as infile:
                filedict = xmltodict.parse(infile)
                success = client.tr.articles.insert(filedict)
            if success:
                print "Successfully inserted " + filename
                os.remove(path + filename)
            else:
                print "Error on file " + filename

if __name__ == "__main__":
    path = "/home/ubuntu/output/Reuters World Service/"
    client = start_mongo_client()
    while 1:
        try:
            upload_all_documents_to_mongo(path, client)
        except Exception as exc:
            print exc

# code here
import xmltodict
import os
from update_replica_set import start_mongo_client

if __name__ == "__main__":
    path = "/home/ubuntu/output/Reuters World Service/"
    client = start_mongo_client()
    for filename in os.listdir(path):
        if os.path.isfile(path + filename):
            with open(path + filename) as infile:
                filedict = xmltodict.parse(infile)
                client.tr.articles.insert(filedict)

# code here
import xmltodict
import os
from update_replica_set import start_mongo_client

if __name__ == "__main__":
    client = start_mongo_client()
    for filename in os.listdir("/home/ubuntu/output/Reuters World Service/"):
        with open("/home/ubuntu/output/Reuters World Service/" + filename) as infile:
            filedict = xmltodict.parse(infile)
            client.tr.articles.insert(filedict)

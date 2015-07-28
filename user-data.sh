#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install -y git
cd /home/ubuntu/
sudo git clone https://github.com/executivereader/mongo-startup.git
sudo git clone https://github.com/executivereader/reuters-downloader.git
cd /home/ubuntu/reuters-downloader
sudo cp /home/ubuntu/mongo-startup/connection_string.txt connection_string.txt
sudo cp /home/ubuntu/mongo-startup/update_replica_set.py update_replica_set.py
sudo apt-get install -y python-dev python-pip
sudo pip install pymongo xmltodict
sudo python initialize_reuters_downloader.py
sudo screen -dm -c "sudo python parse_reuters_articles.py"

#!/usr/bin/env bash
sudo apt-get install -y git
cd /home/ubuntu/
sudo git clone https://github.com/executivereader/reuters-downloader.git
cd /home/ubuntu/reuters-downloader
sudo wget https://raw.githubusercontent.com/executivereader/mongo-startup/master/connection_string.txt
sudo python initialize_reuters_downloader.py
sudo screen -dm -c "sudo python parse_reuters_articles.py"

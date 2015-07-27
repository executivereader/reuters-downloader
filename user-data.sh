#!/usr/bin/env bash
sudo apt-get install -y git
cd /home/ubuntu/
sudo git clone https://github.com/executivereader/mongo-startup.git
sudo git clone https://github.com/executivereader/reuters-downloader.git
cd /home/ubuntu/reuters-downloader
python initialize_reuters_downloader.py
screen -dm -c "python parse_reuters_articles.py"

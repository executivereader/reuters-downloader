# code here
from update_replica_set import start_mongo_client
import os

if __name__ == "__main__":
    client = start_mongo_client()
    tr_credentials = client.credentials.thomsonreuters.find_one()
    # first update whatever's on machine
    os.system("sudo apt-get update")
    # get only dependencies (explained later)
    os.system("sudo apt-get install socat unzip")
    # update again for good measure
    os.system("sudo apt-get update")
    # this is where we'll put the files
    os.system("sudo mkdir /home/ubuntu/output")
    #this is where we'll put the program
    os.system("sudo mkdir /home/ubuntu/TRDownloader")
    # download the downloader to current directory
    os.system("sudo wget " + tr_credentials["download_location"] + " -P /home/ubuntu/TRDownloader/")
    # now unzip downloader
    os.system("sudo unzip /home/ubuntu/TRDownloader/cdt-client-3.9.6-linux_x64.zip -d /home/ubuntu/TRDownloader/")
    # pipe in all required input for downloader prompts
    os.system("printf 'o\n\n\n\n\n\n1\n\n\n/home/ubuntu/output\nn\n' | sudo sh /home/ubuntu/TRDownloader/cdt-client-3.9.6-linux_x64.sh")
    # now pipe in required input for configurator prompts
    # wrinkle here: make_config.sh does not allow pipes
    # so we use socat to trick it into thinking it is in a tty
    os.system("printf 'downloader\n" + tr_credentials["username"] + "\n" + tr_credentials["password"] + "\n\n\n\ntrue\n' | socat - EXEC:'sudo sh /usr/local/Reuters/ContentDownloader3/make_config.sh',pty,setsid,ctty")
    # now run the setup command that also starts service
    os.system("sudo sh /usr/local/Reuters/ContentDownloader3/setupservice.sh")
    # now need to copy around some config files
    os.system("sudo cp /home/ubuntu/reuters-downloader/conf/configuration.xml /usr/local/Reuters/ContentDownloader3/conf/configuration.xml")
    os.system("sudo cp /home/ubuntu/reuters-downloader/conf/server.xml /usr/local/Reuters/ContentDownloader3/conf/server.xml")
    # now replace the username and password
    os.system("sudo sed -i -e s/usernamehere/" + tr_credentials["username"] + "/g /home/ubuntu/reuters-downloader/conf/configuration.xml")
    os.system("sudo sed -i -e s/hashedpasswordhere/" + tr_credentials["hashed_password"] + "/g /home/ubuntu/reuters-downloader/conf/configuration.xml")
    

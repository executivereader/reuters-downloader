# code here
from update_replica_set import start_mongo_client

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
    # download the downloader to current directory
    os.system("sudo wget " + tr_credentials["download_location"])
    # now unzip downloader
    os.system("sudo unzip cdt-client-3.9.6-linux_x64.zip")
    # pipe in all required input for downloader prompts
    os.system("printf 'o\n\n\n\n\n\n1\n\n\n/home/ubuntu/output\nn\n' | sudo sh cdt-client-3.9.6-linux_x64.sh")
    # go to directory where stuff was installed
    os.system("cd /usr/local/Reuters/ContentDownloader3")
    # now pipe in required input for configurator prompts
    # wrinkle here: make_config.sh does not allow pipes
    # so we use socat to trick it into thinking it is in a tty
    os.system("printf 'downloader\n" + tr_credentials["username"] + "\n" + tr_credentials["password"] + "\n\n\n\ntrue\n' | socat - EXEC:'sudo sh make_config.sh',pty,setsid,ctty")
    # now run the setup command that also starts service
    os.system("sudo sh setupservice.sh")

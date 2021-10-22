#!/bin/bash

### This shell script is used to setup initial environment during login. This checks whether a psql database is up or not.
### installed or not. If not, it will start the database or create a new one
### Checks recent python version. If not upgraded, it upgrades it and set it as default alternative
### Install required dependencies from requirements.txt


### Safer bash scripting, see: https://explainshell.com/explain?cmd=set+-euxo+pipefail
set -euxo pipefail


### Update package lists, -qq suppresses output
sudo apt update -y -qq


### Database installation check

if which psql; then
     echo "Database is installed. Checking its status..."
     if sudo service postgresql status; then
        echo "Database is running. No need to start ...."
     else
        echo "Database is not running. Starting the database...."
        if sudo service postgresql start; then
            echo "Database started"
        fi
     fi
else
    echo "Database is not installed. Installing..."
    sudo apt install -y postgresql -qq
fi


### Python installation check

echo "Checking python installation"
if python3 -c 'import sys; exit(sys.version_info.major != 3 or sys.version_info.minor < 9)'; then
    echo "Python 3.9+ already installed."
else
    sudo apt install -y software-properties-common -qq
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt install -y python3-pip python3.9 python3.9-venv -qq
    # update-alternatives makes python3 refer to the right Python version and
    # updates the version of Python that pip3 uses
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
fi


### Create virtual environment, activate it & install required Python packages

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --user

#!/bin/bash

### This shell script is used to setup environment for the system on a machine running Ubuntu. It:
###  1. Installs database (if not already installed)
###  2. Starts the database service (if not already running)
###  3. Installs Python 3.9 (unless Python 3.9+ is already installed)
###  4. Creates a virtual environment in .venv directory
###  5. Installs required Python packages inside that virtual environment

# Safer bash scripting, see: https://explainshell.com/explain?cmd=set+-euxo+pipefail
set -euxo pipefail


### Update package lists, -qq suppresses output
sudo apt update -y -qq


### Database installation

if which psql; then
     echo "Database is already installed."
else
    echo "Database is not installed. Installing..."
    sudo apt install -y postgresql -qq
fi


### Start database service

if sudo service postgresql status; then
   echo "Database service is already running."
else
   echo "Database is not running. Starting..."
   sudo service postgresql start
fi


### Python installation check

echo "Checking python installation..."
if python3 -c 'import sys; exit(sys.version_info.major != 3 or sys.version_info.minor < 9)'; then
    echo "Python 3.9+ already installed."
else
    sudo apt install -y software-properties-common -qq
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt install -y python3-pip python3.9 -qq
    # update-alternatives makes python3 refer to the right Python version and
    # updates the version of Python that pip3 uses
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
    echo "Installed Python 3.9."
fi
py_ver_major=$(python3 -c "import sys; print(sys.version_info.major)")
py_ver_minor=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$py_ver_major" -eq "3" ] && [ "$py_ver_minor" -ge "9" ]; then
        py_ver=$py_ver_major.$py_ver_minor
        echo $py_ver
fi

### Create virtual environment & install required Python packages inside
sudo apt-get install python$py_ver-venv
python3 -m venv env
env/bin/pip install -r requirements.txt

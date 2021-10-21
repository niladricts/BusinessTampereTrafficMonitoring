#!/bin/bash


###This shell script is used to setup initial environment during login. This checks whether a psql database is up or not. Or,
### installed or not. If not, it will start the database or create a new one
### Checks recent python version. If not upgraded, it upgrades it and set it as default alternative
### Install required dependencies from requirements.txt

### Database installation check

db_exist=`which psql | wc -l`
echo $db_exist

if [ $db_exist -eq 1 ]; then
     echo "Database is installed. Checking its status..."
     db_status=$(sudo service postgresql status)
     db_check=$(echo $db_status | grep -i "stopped"|wc -l)
     if [ $db_check -eq 0 ]; then
          echo "Database is running. No need to start ...."
     else
            echo "Database is not running. Starting the database...."
            sudo service postgresql start
            if [ $? -eq 0 ]; then
                 echo "Database started"
            fi
     fi
else
        echo "Database is not installed.Installing it first ..."
        sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
        if [ $? -eq 0 ]; then
                wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

        fi
        if [ $? -eq 0 ]; then
                echo "Key added"
                sudo apt-get update
        fi
        if [ $? -eq 0 ]; then
                echo "Updates of the packages done."
                sudo apt-get install postgresql
        fi
        if [ $? -eq 0 ]; then
                echo "PostGRE installed. Checking version"
                version=`psql --version`
                echo $version
        fi


fi


### Python installation check

echo "Checking python installation"
py_status=$(python3 --version | wc -l)
py_version=$(python3 --version)
py_ver=$(echo $py_version | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
echo $py_ver
if [ $py_status -ge 1 ]; then
        echo "Python is installed and version is $py_version"
        if [ "$py_ver" -ge "39"  ]; then
                echo "Python 3.9+ installed. No further installation needed"
        else
                echo "Python 3.9 is needed"
                sudo apt install -y software-properties-common
                if [ $? -eq 0 ]; then
                        sudo add-apt-repository -y ppa:deadsnakes/ppa
                        if [ $? -eq 0 ];then
                                sudo apt install -y python3.9
                                if [ $? -eq 0 ]; then
                                        py_latest=$(python3 --version)
                                        echo "Latest Installed Python version is $py_latest"
                                        sudo update-alternatives --install /usr/local/bin/python3 python /usr/bin/python3.9 1
                                        if [ $? -eq 0 ]; then
                                                echo "Latest Python version set. It is $(python3 --version)"
                                        fi

                                fi
                        fi

                fi

        fi
fi



### Python packages installation

# Searching requirements.txt in the current path

pip3 install -r requirements.txt --user
if [ $? -eq 0 ]; then
        echo "All dependencies are installed"
else
        echo "Problem in installing dependencies as requirement.txt is missing. Aborting the process..."
fi

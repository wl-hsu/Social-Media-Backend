#!/usr/bin/env bash

echo 'Start!'

sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.6 2

cd /vagrant

sudo apt-get update
sudo apt-get install tree

# install mysql8
if ! [ -e /vagrant/mysql-apt-config_0.8.15-1_all.deb ]; then
	wget -c https://dev.mysql.com/get/mysql-apt-config_0.8.15-1_all.deb
fi

sudo dpkg -i mysql-apt-config_0.8.15-1_all.deb
sudo DEBIAN_FRONTEND=noninteractivate apt-get install -y mysql-server
sudo apt-get install -y libmysqlclient-dev

if [ ! -f "/usr/bin/pip" ]; then
  sudo apt-get install -y python3-pip
  sudo apt-get install -y python-setuptools
  sudo ln -s /usr/bin/pip3 /usr/bin/pip
else
  echo "pip3 已安装"
fi

# Upgrade pip, there are currently problems, read timed out, sometimes it works, but most of the time it doesn’t work
# python -m pip install --upgrade pip
# Change source perfect solution
# Install pip required dependencies
pip install --upgrade setuptools
pip install --ignore-installed wrapt
# Install the latest version of pip
pip install -U pip
# Install pip package according to the records in requirements.txt to ensure compatibility between all versions
pip install -r requirements.txt


# Set the password of the mysql root account to yourpassword
# Create a database named twitter
sudo mysql -u root << EOF
	ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'yourpassword';
	flush privileges;
	show databases;
	CREATE DATABASE IF NOT EXISTS twitter;
EOF
# fi


# If want to go the /vagrant path
# Please enter the vagrant ssh command to enter
# Manual input
# Enter ls -a
# Enter vi .bashrc
# At the bottom, add cd /vagrant

echo 'All Done!'

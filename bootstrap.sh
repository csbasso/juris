#!/usr/bin/env bash

#./scripts/install_linux_pkgs.sh
#sudo apt-get update
#sudo apt-get -y dist-upgrade
#sudo apt-get -y install linux-headers-$(uname -r) virtualbox-guest-utils swig g++ uuid-dev make

#tools
# sudo apt-get -y install vim python2.7-dev python-pip libevent-dev
sudo apt-get install vim
# sudo apt-get install python2.7-dev
sudo apt-get install python-pip
# sudo apt-get install libevent-dev

# web
#sudo apt-get -y install apache2

sudo pip install -r scripts/pip_requirements.txt 
# sudo apt-get -y dist-upgrade
# sudo pip install django=="1.6.1"
# sudo pip install beautifulsoup4=="4.1.3"
#-sudo apt-get -y dist-upgrade

sudo rm -rf /var/www
sudo ln -fs /vagrant /var/www

#-sudo service apache2 restart

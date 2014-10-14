#!/bin/bash

WKDIR=${PWD##*/}
ARCH=`uname -m`

if [ $WKDIR != "STV2" ]; then
	echo "WARN! install.sh must be run from ./codex! Script will exit."
	exit
fi

echo "You must have internet connectivity to install CODEX with this installer."
read -p "Would you like to continue? (y/n): " INTERNET
if [ $INTERNET == "n" ]; then
	exit
fi

echo ""
read -p "Install CODEX on this machine? (y/n): " CODEX
read -p "install DB on this machine? (y/n): " DB

if [ $DB == "y" ]; then
	if [ $ARCH != "x86_64" ]; then
		read -p "DB must be installed on x86_64 architecture. Do you wish to continue the CODEX install?" CONT
		if [ $CONT == "n" ]; then
			exit
		fi
	else
		echo ""
		echo "Installing MongoDB backend..."
		cp ./yum/mongodb.repo /etc/yum.repos.d/mongodb.repo #> /dev/null 2>&1
		yum install -y mongodb-org #> /dev/null 2>&1
	fi
else
	echo "Instructions on how to install MongoDB can be found at mongoDB.org."
	echo ""
fi

if [ $CODEX == "y" ]; then
	echo "Installing Python + pip"
	yum install -y python #> /dev/null 2>&1
	wget https://bootstrap.pypa.io/get-pip.py #> /dev/null 2>&1
	chmod +x get-pip.py #> /dev/null 2>&1
	python ./get-pip.py #> /dev/null 2>&1
	rm -f get-pip.py #> /dev/null 2>&1
	echo "Installing Node.js"
	curl -sL https://rpm.nodesource.com/setup | bash - #> /dev/null 2>&1
	yum groupinstall 'Development Tools' #> /dev/null 2>&1
	echo "Installing NPM modules"
	npm install #> /dev/null 2>&1
	echo "Setting security settings"
	service iptables stop #> /dev/null 2>&1
	service ip6tables stop #> /dev/null 2>&1
	chkconfig iptables off #> /dev/null 2>&1
	chkconfig ip6tables off #> /dev/null 2>&1

echo "Finished up. Exiting."

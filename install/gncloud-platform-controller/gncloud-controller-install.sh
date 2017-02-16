#!/bin/bash

args=$#
if [ $args -lt 2 ]
then
	echo "Docker registry IP & address 를 입력해 주십시오."  
	echo "Usage : ./docker-install.sh 192.168.1.204 5000"
	exit -1
fi 

echo "export PYTHONPATH=/var/lib/gncloud" >> ~/.bash_profile

# ssh 접속을 위한 sshkey generation and key copy
ssh-keygen -f ~/.ssh/id_rsa
#ssh-copy-id ~/.ssh/id_rsa.pub root@[IP]

yum -y install unzip
systemctl disable firewalld
systemctl stop firewalld

sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
#setsebool -P httpd_can_network_connect on

./python-install.sh
./docker-install.sh $1 $2
./uwsgi-install.sh
./source-install.sh




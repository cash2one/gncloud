#!/bin/bash

args=$#
if [ $args -lt 2 ]
then
	echo "Docker registry IP & port를 입력해 주십시오. "  
	echo "Usage : ./docker-install.sh 192.168.1.204 5000"
	exit -1
fi 

> /etc/yum.repos.d/docker.repo
echo '[dockerrepo]' >> /etc/yum.repos.d/docker.repo
echo 'name=Docker Repository' >> /etc/yum.repos.d/docker.repo
echo 'baseurl=https://yum.dockerproject.org/repo/main/centos/7/' >> /etc/yum.repos.d/docker.repo
echo 'enabled=1' >> /etc/yum.repos.d/docker.repo
echo 'gpgcheck=1' >> /etc/yum.repos.d/docker.repo
echo 'gpgkey=https://yum.dockerproject.org/gpg' >> /etc/yum.repos.d/docker.repo

yum -y install docker-engine

sed -i "s/ExecStart=\/usr\/bin\/dockerd/ExecStart=\/usr\/bin\/dockerd -H tcp:\/\/0.0.0.0:2375 -H unix:\/\/\/var\/run\/docker.sock --insecure-registry $1:$2/g" \
/usr/lib/systemd/system/docker.service

systemctl enable docker
systemctl start docker


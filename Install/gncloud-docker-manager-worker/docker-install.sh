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

# docker manager
# docker swarm init --advertise-addr [IP]
# result token : SWMTKN-1-49nj1cmql0jkz5s954yi3oex3nedyz0fb0xx14ie39trti4wxv-8vxv8rssmk743ojnwacrr2e7c
# docker workers
# docker swarm join --token SWMTKN-1-49nj1cmql0jkz5s954yi3oex3nedyz0fb0xx14ie39trti4wxv-8vxv8rssmk743ojnwacrr2e7c [IP]:2377

# 각 docker host에
# vi /etc/hosts => "gncloud platform ip	docker-registry" 추가
# 192.168.1.5	docker-registry

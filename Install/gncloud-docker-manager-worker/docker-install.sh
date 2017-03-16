#!/bin/bash

args=$#
if [ $args -lt 2 ]
then
	echo "지앤클라우드 플랫폼 IP와 docker version을 입력해 주십시오. "
	echo "Usage : ./docker-install.sh 192.168.1.204 12"
	exit -1
fi

docker-registry=$1

if [ "$2" = "13" ]; then
	# docker version 1.13 버전 이상일 경우
	> /etc/yum.repos.d/docker.repo
	echo '[dockerrepo]' >> /etc/yum.repos.d/docker.repo
	echo 'name=Docker Repository' >> /etc/yum.repos.d/docker.repo
	echo 'baseurl=https://yum.dockerproject.org/repo/main/centos/7/' >> /etc/yum.repos.d/docker.repo
	echo 'enabled=1' >> /etc/yum.repos.d/docker.repo
	echo 'gpgcheck=1' >> /etc/yum.repos.d/docker.repo
	echo 'gpgkey=https://yum.dockerproject.org/gpg' >> /etc/yum.repos.d/docker.repo
	yum -y install docker-engine
	sed -i "s/ExecStart=\/usr\/bin\/dockerd/ExecStart=\/usr\/bin\/dockerd -H tcp:\/\/0.0.0.0:2375 -H unix:\/\/\/var\/run\/docker.sock --insecure-registry docker-registry:5000/g" \
	/usr/lib/systemd/system/docker.service
	systemctl enable docker
	systemctl start docker
elif [ "$2" = "12" ]; then
	# docker install 1.12.5
	>/etc/yum.repos.d/docker.repo echo '[dockerrepo]' >> /etc/yum.repos.d/docker.repo
	echo 'name=Docker Repository' >> /etc/yum.repos.d/docker.repo
	echo 'baseurl=https://yum.dockerproject.org/repo/main/centos/7/' >> /etc/yum.repos.d/docker.repo
	echo 'enabled=1' >> /etc/yum.repos.d/docker.repo echo 'gpgcheck=1' >> /etc/yum.repos.d/docker.repo
	echo 'gpgkey=https://yum.dockerproject.org/gpg' >> /etc/yum.repos.d/docker.repo
	# libvirtd와 docker가 서로 상호 동작 하기 위해서 docker 버전을 1.12.5로 맞추어야 한다.
	# 그렇지않으면  DHCP 서버로 부터 KVM 인스턴스가 IP를 얻어오지 못한다.
	yum -y install docker-1.12.5
	sed -i "s/DOCKER_NETWORK_OPTIONS=/DOCKER_NETWORK_OPTIONS=-H tcp:\/\/0.0.0.0:2375 -H unix:\/\/\/var\/run\/docker.sock/g" /etc/sysconfig/docker-network
	sed -i "s/DOCKER_STORAGE_OPTIONS=/DOCKER_STORAGE_OPTIONS=--insecure-registry docker-registry:5000/g" /etc/sysconfig/docker-storage
	sed -i "s/true/false/g" /etc/docker/daemon.json

	systemctl enable docker
	systemctl start docker
else
	echo "docker version은 12, 13을 입력해야 합니다."
	exit -1
fi

echo "docker-registry  $docker-registry" >> /etc/hosts

# docker manager
# docker swarm init --advertise-addr [manager IP]
# result token : SWMTKN-1-49nj1cmql0jkz5s954yi3oex3nedyz0fb0xx14ie39trti4wxv-8vxv8rssmk743ojnwacrr2e7c

# docker workers
# docker swarm join --token SWMTKN-1-49nj1cmql0jkz5s954yi3oex3nedyz0fb0xx14ie39trti4wxv-8vxv8rssmk743ojnwacrr2e7c [manager IP]:2377


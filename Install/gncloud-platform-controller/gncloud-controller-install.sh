#!/bin/bash

args=$#
if [ $args -lt 2 ]
then
	echo "지앤클라우드 플랫폼 IP와 docker version을 입력해 주십시오. "
	echo "Usage : ./docker-install.sh 192.168.1.204 12"
	exit -1
fi

docker-registry=$1

yum -y update

systemctl disable firewalld
systemctl stop firewalld
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config

mkdir -p /var/log/gncloud
mkdir -p /home/data
ln -s /home/data /data
mkdir -p /data/mysql
mkdir -p /data/registry

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

	# docker 디렉토리를 /data로 옮김
    mv /var/lib/docker /data/docker
    ln -s /data/docker docker

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

	# docker 디렉토리를 /data로 옮김
    mv /var/lib/docker /data/docker
    ln -s /data/docker docker

	systemctl enable docker
	systemctl start docker
else
	echo "docker version은 12, 13을 입력해야 합니다."
	exit -1
fi

# /etc/hosts에 docker registry IP 등록
echo "docker-registry  $docker-registry" >> /etc/hosts

# ssh key 생성 및 내부 컨테이너 접근이 가능하도록 키 복사
ssh-keygen -f ~/.ssh/id_rsa
cp ~/.ssh/id_rsa.pub authorized_keys

# docker-compose install
curl -L "https://github.com/docker/compose/releases/download/1.11.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# git 설치, docker-compose.yml 다운로드 및 실행
yum -y install epel-release
yum -y install git
mkdir /data/git
cd /data/git
git clone https://github.com/gncloud/gncloud-all-in-one.git

cp /data/git/gncloud-all-in-one/docker-compose.yml ~/.
cd ~
docker-compose up -d


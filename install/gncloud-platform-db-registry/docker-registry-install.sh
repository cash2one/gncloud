#!/bin/bash
args=$#
if [ $args -lt 1 ]
then
	echo "please input Docker registry PATH"
	echo "Usage : ./docker-registry /data/docker-registry"
	exit -1
fi 
yum -y install docker-registry
mkdir -p $1
path=$(echo $1 | sed 's/\//\\\//g')
if [ -e /etc/docker-registry.yml.org ]
then
	cp /etc/docker-registry.yml.org /etc/docker-registry.yml
else
	cp /etc/docker-registry.yml /etc/docker-registry.yml.org
fi
sed -i "s/starch_backend: _env:SEARCH_BACKEND/search_backend: _env:SEARCH_BACKEND:sqlalchemy/g" /etc/docker-registry.yml
sed -i "s/sqlite:\/\/\/\/tmp\/docker-registry.db/sqlite:\/\/\/$path\/docker-registry.db/g" /etc/docker-registry.yml
sed -i "s/\/var\/lib\/docker-registry/$path/g" /etc/docker-registry.yml
mkdir /srv/docker-registry
systemctl enable docker-registry
systemctl start docker-registry


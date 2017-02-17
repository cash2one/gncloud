#!/bin/bash

args=$#
if [ $args -lt 1 ]
then
	echo "Docker registry PATH를 입력해 주십시오."  
	echo "Usage : ./gncloud-platform-install.sh /data/docker-registry"
	exit -1
fi 

registry_path=$1

./docker-registry-install.sh $registry_path
./mariadb-install.sh


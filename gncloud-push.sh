#!/bin/bash

args=$#
if [ $args -lt 1 ]
then
	echo "지앤클라우드 플랫폼을 도커 공식 레지스트리에 푸시하는 기능입니다. 버전을 입력해야 합니다."
	echo "Usage : ./gncloud-push.sh 1.0"
	exit -1
fi

docker tag gncloud/gncloud-web          gncloud/gncloud-web:$1
docker tag gncloud/gncloud-scheduler    gncloud/gncloud-scheduler:$1
docker tag gncloud/gncloud-manager      gncloud/gncloud-manager:$1
docker tag gncloud/gncloud-docker       gncloud/gncloud-docker:$1
docker tag gncloud/gncloud-hyperv       gncloud/gncloud-hyperv:$1
docker tag gncloud/gncloud-kvm          gncloud/gncloud-kvm:$1
docker tag gncloud/gncloud-mysql        gncloud/gncloud-mysql:$1
docker tag gncloud/gncloud-registry     gncloud/gncloud-registry:$1

docker push gncloud/gncloud-web
docker push gncloud/gncloud-scheduler
docker push gncloud/gncloud-manager
docker push gncloud/gncloud-docker
docker push gncloud/gncloud-hyperv
docker push gncloud/gncloud-kvm
docker push gncloud/gncloud-mysql
docker push gncloud/gncloud-registry

docker push gncloud/gncloud-web:$1
docker push gncloud/gncloud-scheduler:$1
docker push gncloud/gncloud-manager:$1
docker push gncloud/gncloud-docker:$1
docker push gncloud/gncloud-hyperv:$1
docker push gncloud/gncloud-kvm :$1
docker push gncloud/gncloud-mysql:$1
docker push gncloud/gncloud-registry:$1

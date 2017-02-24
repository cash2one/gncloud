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

# version 2
#./docker-install.sh
#docker login gncloud
#docker pull gncloud/gncloud-registry:latest

# 밑에 보이는것 무시
#mkdir auth
#docker pull registry
#docker tag registry gncloud/gncloud-registry
#docker run --entrypoint htpasswd gncloud/gncloud-registry -Bbn gncloud gncloud > auth/htpasswd
#docker stop registry && docker rm -v registry

#mkdir certs
#cd certs

#generate key
#openssl genrsa 1024 > domain.key

#generate cert
# input country, locality, organization, unit, name, email etc
#openssl req -new -x509 -nodes -sha1 -days 365 -key domain.key -out domain.cert

#openssl x509 -inform PER -in domain.cert -out domain.crt

#cd ..
#docker run -d -p 5000:5000 --restart=always --name registry \
#  -v `pwd`/auth:/auth \
#  -e "REGISTRY_AUTH=htpasswd" \
#  -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" \
#  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
#  -v `pwd`/certs:/certs \
#  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
#  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
#  registry:2



#docker run -d -p 5000:5000 --restart=always --name gncloud-registry  -v `pwd`/auth:/auth   -e "REGISTRY_AUTH=htpasswd"   -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm"  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd -v `pwd`/certs:/certs -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key  gncloud/gncloud-registry
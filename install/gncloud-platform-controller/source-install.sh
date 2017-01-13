#!/bin/bash

# source 내려 받기
mkdir -p /usr/local/source
cd /usr/local/source; git clone https://github.com/gncloud/gncloud.git

# configuration file 복사
mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.org
cp /usr/local/source/gncloud/sites-available/nginx.conf /etc/nginx/.

#nginx restart
systemctl restart nginx

# controller 들 start
#cd /usr/local/source/gncloud; nohup uwsgi --http-socket :8080 --plugin python --wsgi-file ./Manager/__init__.py --logto  ./Manager/manager.log --callable app &
#cd /usr/local/source/gncloud; nohup uwsgi --http-socket :8083 --plugin python --wsgi-file ./Docker/__init__.py --logto  ./Docker/docker.log --callable app &
#cd /usr/local/source/gncloud; nohup uwsgi --http-socket :8081 --plugin python --wsgi-file ./kvm/__init__.py --logto  ./kvm/kvm.log --callable app &
#cd /usr/local/source/gncloud; nohup uwsgi --http-socket :8082 --plugin python --wsgi-file ./HyperV/__init__.py --logto  ./HyperV/hyperv.log --callable app &

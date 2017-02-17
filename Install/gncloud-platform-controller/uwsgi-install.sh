#!/bin/bash

#컴파일러 설치 uwsgi를 설치하기 위해 컴파일러가 먼저 설치 되어 있어야 한다.
yum -y group install "Development Tools"
# uwsgi 설치
pip install uwsgi
#uwsgi --http-socket :8080 --plugin python --wsgi-file __init__.py --callable app

# libvirt 설치
yum -y install qemu-kvm libvirt virt-install bridge-utils

# nginx 설치
yum -y install nginx
systemctl enable nginx
systemctl start nginx



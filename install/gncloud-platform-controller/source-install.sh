#!/bin/bash

# source 내려 받기
cd /var/lib/; git clone https://github.com/gncloud/gncloud.git

# configuration file 복사
mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.org
cp /var/lib/gncloud/sites-available/nginx.conf /etc/nginx/.

#nginx restart
systemctl restart nginx

mkdir -p /var/log/gncloud
export PYTHONPATH=/var/lib/gncloud
# controller 들 start
nohup uwsgi --http-socket :8080 --plugin python --wsgi-file /var/lib/gncloud/Manager/__init__.py --logto  /var/log/gncloud/manager_controller.log --processes 4 --threads 2 --callable app &
nohup uwsgi --http-socket :8081 --plugin python --wsgi-file /var/lib/gncloud/kvm/__init__.py --logto /var/log/gncloud/kvm_controller.log  --processes 4 --threads 2 --callable app &
nohup uwsgi --http-socket :8082 --plugin python --wsgi-file /var/lib/gncloud/HyperV/__init__.py --logto /var/log/gncloud/hyperv_controller.log  --processes 4 --threads 2 --callable app &
nohup uwsgi --http-socket :8083 --plugin python --wsgi-file /var/lib/gncloud/Docker/__init__.py --logto /var/log/gncloud/docker_controller.log  --processes 4 --threads 2 --callable app &
nohup uwsgi --http-socket :8084 --plugin python --wsgi-file /var/lib/gncloud/scheduler/__init__.py --logto /var/log/scheduler.log --callable app --enable-threads &
#!/bin/bash
nohup uwsgi --http-socket :8083 --plugin python --wsgi-file /var/lib/gncloud/Docker/__init__.py --logto /var/log/gncloud/docker.log --processes 4 --threads 2 --callable app &
# uwsgi --http-socket :80 --plugin python --wsgi-file /var/lib/gncloud/Docker/__init__.py --logto /var/log/gncloud/docker.log --processes 4 --threads 2 --callable app
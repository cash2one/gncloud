#!/bin/bash
uwsgi --http-
nohup socket :8080 --plugin python --wsgi-file /var/lib/gncloud/Manager/__init__.py --logto /var/log/gncloud/manager.log --processes 4 --threads 2 --callable app &


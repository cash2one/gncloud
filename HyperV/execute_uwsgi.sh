#!/bin/bash
nohup uwsgi --http-socket :8082 --plugin python --wsgi-file /var/lib/gncloud/HyperV/__init__.py --logto /var/log/gncloud/hyperv.log --processes 4 --threads 2 --callable app &
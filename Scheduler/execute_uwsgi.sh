#!/bin/bash
nohup uwsgi --http-socket :8084 --plugin python --wsgi-file /var/lib/gncloud/Scheduler/__init__.py --logto /var/log/gncloud/scheduler.log --callable app &
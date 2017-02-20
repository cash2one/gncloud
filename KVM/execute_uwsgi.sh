#!/bin/bash
nohup uwsgi --http-socket :8081 --plugin python --wsgi-file /var/lib/gncloud/KVM/__init__.py --logto /var/log/gncloud/kvm.log --processes 4 --threads 2 --callable app &
# uwsgi --http-socket :80 --plugin python --wsgi-file /var/lib/gncloud/KVM/__init__.py --logto /var/log/gncloud/kvm.log --processes 4 --threads 2 --callable app
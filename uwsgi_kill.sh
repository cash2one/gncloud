#!/usr/bin/bash
sudo git pull
kill -9 $(ps aux | grep uwsgi |awk '/manager/ {print $2}')
kill -9 $(ps aux | grep uwsgi |awk '/kvm/ {print $2}')
kill -9 $(ps aux | grep uwsgi |awk '/hyperv/ {print $2}')
kill -9 $(ps aux | grep uwsgi |awk '/docker/ {print $2}')


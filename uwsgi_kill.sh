#!/usr/bin/bash
sudo git pull
kill -9 $(ps aux | grep uwsgi | grep python | awk '/manager/ {print $2}')
kill -9 $(ps aux | grep uwsgi | grep python | awk '/kvm/ {print $2}')
kill -9 $(ps aux | grep uwsgi | grep python | awk '/hyperv/ {print $2}')
kill -9 $(ps aux | grep uwsgi | grep python | awk '/docker/ {print $2}')
kill -9 $(ps aux | grep uwsgi | grep python | awk '/scheduler/ {print $2}')


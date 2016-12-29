#!/usr/bin/bash
sudo git pull
kill -9 $(ps aux |awk '/manager/ {print $2}')
kill -9 $(ps aux |awk '/kvm/ {print $2}')
kill -9 $(ps aux |awk '/hyperv/ {print $2}')
kill -9 $(ps aux |awk '/docker/ {print $2}')


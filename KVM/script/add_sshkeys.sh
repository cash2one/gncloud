#!/usr/bin/bash
path=$1
ip=$2
id=$3
ssh-keygen -R $ip
ssh-copy-id -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ${path}.pub ${id}@${ip}
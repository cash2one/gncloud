#!/usr/bin/bash
sshkey=$1
ip=$2
ssh-copy-id -i /root/libvirt/sshkey.pub centos@${ip}
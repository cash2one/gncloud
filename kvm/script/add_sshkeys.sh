#!/usr/bin/bash
sshkey=$1
ip=$2
ssh-keygen -R $ip
echo $sshkey > /root/libvirt/sshkey.pub
ssh-copy-id -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i /root/libvirt/sshkey.pub centos@${ip}
#!/bin/bash
ip=$1

echo -e 'DEVICE="eth0"\nBOOTPROTO="static"\nONBOOT="yes"\nTYPE="Ethernet"\nUSERCTL="yes"\nBROADCAST=192.168.0.255\nIPADDR='${ip}'\nNETMASK=255.255.255.0' > /mnt/libvirt/ifcfg-eth0

scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /mnt/libvirt/ifcfg-eth0  centos@${ip}:ifcfg-eth0

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t centos@${ip} sudo cp /home/centos/ifcfg-eth0 /etc/sysconfig/network-scripts/ifcfg-eth0

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t centos@${ip} sudo service network restart 
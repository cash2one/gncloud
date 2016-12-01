#!/bin/bash
ip=$1

echo -e 'DEVICE="eth0"\nBOOTPROTO="static"\nONBOOT="yes"\nTYPE="Ethernet"\nUSERCTL="yes"\nBROADCAST=192.168.0.255\nIPADDR=${ip}\nNETMASK=255.255.255.0' > ifcfg-eth0

ssh -t -i /var/lib/libvirt/sshkeys/default centos@${ip} sudo cp /home/centos/ifcfg-eth0 /etc/sysconfig/network-scripts/ifcfg-eth0

ssh -t -i /var/lib/libvirt/sshkeys/default centos@${ip} sudo service network restart
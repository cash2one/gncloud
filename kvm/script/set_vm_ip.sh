#!/bin/bash
ip=$1
ssh_id=$2
if [ $ssh_id = "centos" ]; then
echo -e 'DEVICE="eth0"\nBOOTPROTO="static"\nONBOOT="yes"\nTYPE="Ethernet"\nUSERCTL="yes"\nBROADCAST=192.168.0.255\nGATEWAY=192.168.0.1\nIPADDR='${ip}'\nNETMASK=255.255.255.0' > /mnt/libvirt/ifcfg-eth0
scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /mnt/libvirt/ifcfg-eth0 centos@${ip}:ifcfg-eth0
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t centos@${ip} sudo cp /home/centos/ifcfg-eth0 /etc/sysconfig/network-scripts/ifcfg-eth0
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t centos@${ip} sudo service network restart 
elif [ $ssh_id = "ubuntu" ]; then  
echo -e "auto eth0\niface eth0 inet static\naddress ${ip}\nnetmask 255.255.255.0\nnetwork 192.168.0.0\nbroadcast 192.168.10.255\ngateway 192.168.0.1\ndns-nameservers 8.8.8.8" > /mnt/libvirt/eth0.cfg
scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /mnt/libvirt/eth0.cfg ubuntu@${ip}:eth0.cfg
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t ubuntu@${ip} sudo cp /home/ubuntu/eth0.cfg /etc/network/interfaces.d/eth0.cfg
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t ubuntu@${ip} sudo reboot
fi
#!/bin/bash

# libvirt 설치
yum -y install qemu-kvm libvirt virt-install bridge-utils

systemctl enable libvirtd
systemctl start libvirtd

# python 설치
./python-install.sh

# host 서버 ssh 키 생성
ssh-keygen -f /root/id_rsa
mkdir -p /var/lib/libvirt/initcloud
cp config.iso /var/lib/libvirt/initcloud/.
cp meta-data /var/lib/libvirt/initcloud/.
cp sshkey_copy.sh /var/lib/libvirt/initcloud/.

> /var/lib/libvirt/initcloud/user-data
echo "#cloud-config" >> /var/lib/libvirt/initcloud/user-data
echo "password: fastcat=1151" >> /var/lib/libvirt/initcloud/user-data
echo "chpasswd: {expire: False}" >> /var/lib/libvirt/initcloud/user-data
echo "ssh_pwauth: true" >> /var/lib/libvirt/initcloud/user-data
echo "ssh_authorized_keys:" >> /var/lib/libvirt/initcloud/user-data
cat /root/id_rsa.pub >> /var/lib/libvirt/initcloud/user-data

# 버추얼 네트워크 이름 'default'를 destroy 시킴
virsh net-destroy default
virsh net-undefine default
systemctl restart libvirtd

#ifcfg-br0 설정
> /etc/sysconfig/network-script/ifcfg-br0
echo "DEVICE=br0" >> /etc/sysconfig/network-script/ifcfg-br0
echo "TYPE=Bridge" >> /etc/sysconfig/network-script/ifcfg-br0
echo "BOOTPROTO=dhcp" >> /etc/sysconfig/network-script/ifcfg-br0
echo "ONBOOT=yes" >> /etc/sysconfig/network-script/ifcfg-br0
echo "DELAY=0" >> /etc/sysconfig/network-script/ifcfg-br0

#ifcfg-eth? 또는 ifcfg-enp???
if [ -e /etc/sysconfig/network-scripts/ifcfg-eth0 ]
then
	sed -i "s/^/#/g" /etc/sysconfig/network-scripts/ifcfg-eth0
	sed -i "s/#UUID/UUID/g" /etc/sysconfig/network-scripts/ifcfg-eth0
	echo "DEVICE=eth0" >> /etc/sysconfig/network-scripts/ifcfg-eth0
	echo "ONBOOT=yes" >> /etc/sysconfig/network-scripts/ifcfg-eth0
	echo "BRIDGE=br0" >> /etc/sysconfig/network-scripts/ifcfg-eth0
	echo "NM_CONTROLLED=no" >> /etc/sysconfig/network-scripts/ifcfg-eth0
elif [ -e /etc/sysconfig/network-scripts/ifcfg-enp3s0 ]
	sed -i "s/^/#/g" /etc/sysconfig/network-scripts/ifcfg-enp3s0
	sed -i "s/#UUID/UUID/g" /etc/sysconfig/network-scripts/ifcfg-enp3s0
	echo "DEVICE=eth0" >> /etc/sysconfig/network-scripts/ifcfg-enp3s0
	echo "ONBOOT=yes" >> /etc/sysconfig/network-scripts/ifcfg-enp3s0
	echo "BRIDGE=br0" >> /etc/sysconfig/network-scripts/ifcfg-enp3s0
	echo "NM_CONTROLLED=no" >> /etc/sysconfig/network-scripts/ifcfg-enp3s0
fi

systemctl disable NetworkManager
systemctl stop NetworkManager
systemctl restart network

yum -y install arp-scan




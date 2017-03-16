#!/bin/bash

yum -y update

systemctl disable firewalld
systemctl stop firewalld
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config

# pool 디렉토리 생성
mkdir -p /data/local/images/kvm/instance

# SAN (NAS) 등 저장장치가 따로 있을 경우 /data/nas 에 마운트
mkdir -p /data/nas/images/kvm/base
mkdir -p /data/nas/images/kvm/snapshot
mkdir -p /data/nas/images/kvm/backup

# 실행에 필요한 스크립트를 다운로드
yum -y install epel-release
yum -y install git
mkdir -p /data/git
cd git
git clone https://github.com/gncloud/gncloud-all-in-one.git
mkdir -p /var/lib/gncloud/KVM/script/initcloud
cp -R /data/git/gncloud-all-in-one/KVM/script/* /var/lib/gncloud/KVM/script/initcloud/.
chmod 777 /var/lib/gncloud/KVM/script/initcloud/*sh

# user-data 생성 및 key 다운로드 - 지앤클라우드플랫폼에서 생성된 키를 복사
scp root@[지앤클라우드플랫폼IP]:/root/.ssh/id_rsa.pub ~/platform_key # 패스워드 입력 필요

> /var/lib/gncloud/KVM/script/initcloud/user-data
echo "#cloud-config" >> /var/lib/gncloud/KVM/script/initcloud/user-data
echo "password: fastcat=1151" >> /var/lib/gncloud/KVM/script/initcloud/user-data
echo "chpasswd: {expire: False}" >> /var/lib/gncloud/KVM/script/initcloud/user-data
echo "ssh_pwauth: true" >> /var/lib/gncloud/KVM/script/initcloud/user-data
echo "runcmd:" >> /var/lib/gncloud/KVM/script/initcloud/user-data
echo " - [ sh, -c, echo \" `cat ~/platform_key`\" >> ~/.ssh/authorized_keys ] " >> \
	/var/lib/gncloud/KVM/script/initcloud/user-data


# kvm libvirt 를 위한 네트워크 세팅
# IPADDR, GATEWAY, NETMASK 는 직접 수정 하여야 한다
> /etc/sysconfig/network-scripts/ifcfg-br0
echo “DEVICE=br0>> /etc/sysconfig/network-scripts/ifcfg-br0
echo “TYPE=Bridge>> /etc/sysconfig/network-scripts/ifcfg-br0
echo “BOOTPROTO=static>> /etc/sysconfig/network-scripts/ifcfg-br0
echo “ONBOOT=yes>> /etc/sysconfig/network-scripts/ifcfg-br0
echo “DELAY=0>> /etc/sysconfig/network-scripts/ifcfg-br0
echo “IPADDR=192.168.1.22>> /etc/sysconfig/network-scripts/ifcfg-br0
echo “NETMASK=255.255.255.0>> /etc/sysconfig/network-scripts/ifcfg-br0
echo “GATEWAY=192.168.1.1>> /etc/sysconfig/network-scripts/ifcfg-br0
echo “DNS1=168.126.63.1>> /etc/sysconfig/network-scripts/ifcfg-br0

#
>/etc/sysconfig/network-scripts/ifcfg-enp2s0
echo “TYPE=Ethernet” >>/etc/sysconfig/network-scripts/ifcfg-enp2s0
echo “BOOTPROTO=static” >>/etc/sysconfig/network-scripts/ifcfg-enp2s0
echo “NAME=enp2s0” >>/etc/sysconfig/network-scripts/ifcfg-enp2s0
echo “DEVICE=enp2s0” >>/etc/sysconfig/network-scripts/ifcfg-enp2s0
echo “ONBOOT=yes” >>/etc/sysconfig/network-scripts/ifcfg-enp2s0
echo “BRIDGE=br0 ” >>/etc/sysconfig/network-scripts/ifcfg-enp2s0

systemctl disable NetworkManager
systemctl restart network
systemctl stop NetworkManager
chkconfig network on

# libvirt 설치
yum -y install qemu-kvm libvirt virt-install bridge-utils install arp-scan genisoimage

systemctl enable libvirtd
systemctl start libvirtd

# 기본  가상 네트워크 삭제
virsh net-destroy default


# libvirt pool 생성
cd ~
# pool.xml 파일
> pool.xml
echo "<pool type='dir'>" >> pool.xml
echo "   <name>gnpool</name>" >> pool.xml
echo "   <capacity unit='bytes'>375809638400</capacity>" >> pool.xml
echo "   <allocation unit='bytes'>19379785728</allocation>" >> pool.xml
echo "   <available unit='bytes'>356429852672</available>" >> pool.xml
echo "   <source>" >> pool.xml
echo "   </source>" >> pool.xml
echo "   <target>" >> pool.xml
echo "     <path>/data/local/images/kvm/instance</path>" >> pool.xml
echo "     <permissions>" >> pool.xml
echo "       <mode>0755</mode>" >> pool.xml
echo "       <owner>0</owner>" >> pool.xml
echo "       <group>0</group>" >> pool.xml
echo "     </permissions>" >> pool.xml
echo "   </target>" >> pool.xml
echo " </pool>" >> pool.xml

virsh pool-define pool.xml
virsh pool-autostart default
virsh pool-autostart gnpool



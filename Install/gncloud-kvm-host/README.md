# Gncloud private kvm HOST install

1. 설치 절차
2. gncloud-kvm-host-install.sh 실행
3. shell 내용

<span></span>
1. 설치 절차
------------

- 공통 
    - root 권한획득
    - gncloud-install.tgz를 설치할 HOST (H/W)에 복사
    - tar xvzf gncloud-install.tgz

<span></span>
2. gncloud-kvm-host-install.sh 실행
--------------------------------------

- kvm host에 설치
    ```
    $ cd ./gncloud-install/gncloud-kvm-host
    $ chmod +x *.sh
    $ ./gncloud-kvm-host-install.sh
    ```

<span></span>
3. shell 내용
-------------

- libvirt 설치  

    ```
    rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    yum -y update
    yum -y install python-pip
    pip install --upgrade pip
    yum -y install python-devel
    yum -y install MySQL-python
    pip install flask
    pip install sqlalchemy
    pip install pexpect
    pip install ConfigParser
    pip install apscheduler
    pip install humanfriendly
    pip install logger
    yum -y install uwsgi-plugin-python
    pip install --upgrade Flask-SQLAlchemy
    ```

- HOST 서버 ssh 키 생성 및 설정

    ```
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
    ```

- 버추얼 네트워크 이름 'default'를 destroy 시킴

    ```
    virsh net-destroy default
    virsh net-undefine default
    systemctl restart libvirtd
    ```

- network 설정

    ```
    * ifcfg-br0 설정
    > /etc/sysconfig/network-script/ifcfg-br0
    echo "DEVICE=br0" >> /etc/sysconfig/network-scripts/ifcfg-br0
    echo "TYPE=Bridge" >> /etc/sysconfig/network-scripts/ifcfg-br0
    echo "BOOTPROTO=dhcp" >> /etc/sysconfig/network-scripts/ifcfg-br0
    echo "ONBOOT=yes" >> /etc/sysconfig/network-scripts/ifcfg-br0
    echo "DELAY=0" >> /etc/sysconfig/network-scripts/ifcfg-br0

    * ifcfg-eth? 또는 ifcfg-enp???
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
    ```


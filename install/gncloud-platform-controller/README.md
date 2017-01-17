# gncloud private platform 중 controller HOST에 설치
# Gncloud private platform Controller Install

1. 설치 절차
2. gncloud-platform-controller.sh 실행
3. shell 내용

<span></span>
1. 설치 절차
------------

- 공통 
    - root 권한획득
    - gncloud-install.tgz를 설치할 HOST (H/W)에 복사
    - tar xvzf gncloud-install.tgz

<span></span>
2. gncloud-platform-controller.sh 실행
--------------------------------------

- 압축이 풀린 폴더 중 gncloud platform controller를 설치하기 위해 

    ```
    $ cd ./gncloud-install/gncloud-platform-controller
    $ chmod +x *.sh
    $ ./gncloud-platform-controller.sh ip port
        * setting for docker registry ip & port
       (예: ./gncloud-platform-controller.sh 192.168.1.204 5000)
    ```

<span></span>
3. shell 내용
-------------

- 방화벽 내림 
    ```
    systemctl stop firewalld; 
    systemctl disable firewalld;
    ```

- selinux 내림   
    ```
    sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/sysconfig/selinux
    ```

- python 설치
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
    pip install apscheduler==2.1.2
    pip install humanfriendly
    pip install logger
    yum -y install uwsgi-plugin-python
    pip install --upgrade Flask-SQLAlchemy
    ```

- docker 설치
    ```
    > /etc/yum.repos.d/docker.repo
    echo '[dockerrepo]' >> /etc/yum.repos.d/docker.repo
    echo 'name=Docker Repository' >> /etc/yum.repos.d/docker.repo
    echo 'baseurl=https://yum.dockerproject.org/repo/main/centos/7/' >> /etc/yum.repos.d/docker.repo
    echo 'enabled=1' >> /etc/yum.repos.d/docker.repo
    echo 'gpgcheck=1' >> /etc/yum.repos.d/docker.repo
    echo 'gpgkey=https://yum.dockerproject.org/gpg' >> /etc/yum.repos.d/docker.repo

    yum -y install docker-engine

    sed -i "s/ExecStart=\/usr\/bin\/dockerd/ExecStart=\/usr\/bin\/dockerd -H tcp:\/\/0.0.0.0:2375 -H unix:\/\/\/var\/run\/docker.sock --insecure-registry $1:$2/g" \
    /usr/lib/systemd/system/docker.service

    systemctl enable docker
    systemctl start docker
    ```

- nginx, uwsgi 및 libvirt 설치
    ```
    yum -y group install "Development Tools"
    pip install uwsgi

    # libvirt 설치
    yum -y install qemu-kvm libvirt virt-install bridge-utils

    # nginx 설치
    yum -y install nginx
    systemctl enable nginx
    systemctl start nginx
    ```

- source 설치    
    ```
    mkdir -p /usr/local/source
    cd /usr/local/source; git clone https://github.com/gncloud/gncloud.git
    mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.org
    cp /usr/local/source/gncloud/sites-available/nginx.conf /etc/nginx/.
    systemctl restart nginx
    ```

- start uwsgi
    * gncloud 폴더에서 실행 시
    ```
    cd /usr/local/source/gncloud; 
    nohup uwsgi --http-socket :8080 --plugin python --wsgi-file ./Manager/__init__.py --logto  ./Manager/manager.log --callable app &
    cd /usr/local/source/gncloud; 
    nohup uwsgi --http-socket :8083 --plugin python --wsgi-file ./Docker/__init__.py --logto  ./Docker/docker.log --callable app &
    cd /usr/local/source/gncloud; 
    nohup uwsgi --http-socket :8081 --plugin python --wsgi-file ./kvm/__init__.py --logto  ./kvm/kvm.log --callable app &
    cd /usr/local/source/gncloud; 
    nohup uwsgi --http-socket :8082 --plugin python --wsgi-file ./HyperV/__init__.py --logto  ./HyperV/hyperv.log --callable app &
    ```

    * 각 컴포넌트 폴더에서 실행 시
    ```
    cd /usr/local/source/gncloud/Manager; 
    nohup uwsgi --http-socket :8080 --plugin python --wsgi-file __init__.py --logto  manager.log --callable app &
    cd /usr/local/source/gncloud/Docker; 
    nohup uwsgi --http-socket :8083 --plugin python --wsgi-file __init__.py --logto  docker.log --callable app &
    cd /usr/local/source/gncloud/kvm; 
    nohup uwsgi --http-socket :8081 --plugin python --wsgi-file __init__.py --logto  kvm.log --callable app &
    cd /usr/local/source/gncloud/HyperV; 
    nohup uwsgi --http-socket :8082 --plugin python --wsgi-file __init__.py --logto  hyperv.log --callable app &
    ```
    

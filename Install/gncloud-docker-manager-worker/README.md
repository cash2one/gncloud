# 이 설치는 docker 가 설치되어야 하는 호스트에서 실행 한다.
# gncloud platform controller, docker workers
# docker engine install


1. 공통
2. docker 설치
3. swarm init & join

<span></span>
1. 공통
------------

- yum -y update

- systemctl disable firewalld
- systemctl stop firewalld
- sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config

<span></span>
2. docker 설치
------------

    ```
	# docker version 1.13 버전 이상일 경우
	> /etc/yum.repos.d/docker.repo
	echo '[dockerrepo]' >> /etc/yum.repos.d/docker.repo
	echo 'name=Docker Repository' >> /etc/yum.repos.d/docker.repo
	echo 'baseurl=https://yum.dockerproject.org/repo/main/centos/7/' >> /etc/yum.repos.d/docker.repo
	echo 'enabled=1' >> /etc/yum.repos.d/docker.repo
	echo 'gpgcheck=1' >> /etc/yum.repos.d/docker.repo
	echo 'gpgkey=https://yum.dockerproject.org/gpg' >> /etc/yum.repos.d/docker.repo
	yum -y install docker-engine
	sed -i "s/ExecStart=\/usr\/bin\/dockerd/ExecStart=\/usr\/bin\/dockerd -H tcp:\/\/0.0.0.0:2375 -H unix:\/\/\/var\/run\/docker.sock --insecure-registry docker-registry:5000/g" \
	/usr/lib/systemd/system/docker.service
	systemctl enable docker
	systemctl start docker
    ```

    ```
    # docker install 1.12.5
    >/etc/yum.repos.d/docker.repo echo '[dockerrepo]' >> /etc/yum.repos.d/docker.repo
    echo 'name=Docker Repository' >> /etc/yum.repos.d/docker.repo
    echo 'baseurl=https://yum.dockerproject.org/repo/main/centos/7/' >> /etc/yum.repos.d/docker.repo
    echo 'enabled=1' >> /etc/yum.repos.d/docker.repo echo 'gpgcheck=1' >> /etc/yum.repos.d/docker.repo
    echo 'gpgkey=https://yum.dockerproject.org/gpg' >> /etc/yum.repos.d/docker.repo
    # libvirtd와 docker가 서로 상호 동작 하기 위해서 docker 버전을 1.12.5로 맞추어야 한다.
    # 그렇지않으면  DHCP 서버로 부터 KVM 인스턴스가 IP를 얻어오지 못한다.
    yum -y install docker-1.12.5
    sed -i "s/DOCKER_NETWORK_OPTIONS=/DOCKER_NETWORK_OPTIONS=-H tcp:\/\/0.0.0.0:2375 -H unix:\/\/\/var\/run\/docker.sock/g" /etc/sysconfig/docker-network
    sed -i "s/DOCKER_STORAGE_OPTIONS=/DOCKER_STORAGE_OPTIONS=--insecure-registry docker-registry:5000/g" /etc/sysconfig/docker-storage
    sed -i "s/true/false/g" /etc/docker/daemon.json

    systemctl enable docker
    systemctl start docker
    ```

    ```
    # docker registry는 지앤클라우드 플랫폼 IP와 같음
    echo "docker-registry  $docker-registry" >> /etc/hosts
    ```
<span></span>
3. swarm init & join
--------------------

- swarm init
    ```
    docker swarm init --advertise-addr [manager-ip]
    # result has token
    ```
- swarm join
    ```
    # all docker worker
    docker swarm join --token [TOKEN] [IP]:2377
    ```
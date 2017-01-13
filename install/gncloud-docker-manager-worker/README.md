# 이 설치는 docker 가 설치되어야 하는 호스트에서 실행 한다.
# gncloud platform controller, docker workers
# docker engine install


1. 설치 절차
2. docker-install.sh 실행

<span></span>
1. 설치 절차
------------

- 공통 
    - root 권한획득
    - gncloud-install.tgz를 설치할 HOST (H/W)에 복사
    - tar xvzf gncloud-install.tgz

<span></span>
2. docker-install.sh 실행
-------------------------

- 압축이 풀린 폴더 중 gncloud docker를 설치하기 위해

    ```
    $ cd ./gncloud-install/gncloud-docker-manager-worker
    $ chmod +x *.sh
    $ ./docker-install.sh ip port 
	(예:./docker-install.sh 192.168.1.204 5000)
    ```

<span></span>
3. shell 내용
------------
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

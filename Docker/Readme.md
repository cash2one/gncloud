# Container Controller 환경구성

1. 공통
2. controller
3. manager
4. worker
5. registry
6. example shell


<span></span>
1. 공통
-------------

- docker 설치

    - docker 1.12 버전 이상 설치
        
        /etc/yum.repos.d/docker.repo 편집
    ```
        [dockerrepo]
        name=Docker Repository
        baseurl=https://yum.dockerproject.org/repo/main/centos/7/
        enabled=1
        gpgcheck=1
        gpgkey=https://yum.dockerproject.org/gpg
    ```
    
    - yum install docker-engine
    - systemctl enable docker.service
    - systemctl start docker.service 
<span></span>
2. controller
-------------

- python 설치

	- 2.7.12 버전 설치

- pip 설치

    - EPEL (Extra Packages for Enterprise Linux) : Fedora Project 에서 제공하는 저장소
    
    CentOS 7

    ```
    $ rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    ```

    ```
    $ yum install python-pip
    ```

- python package

    -  flask
    ```
    $ pip install flask
    ```

    -  sqlalchemy
    ```
    $ pip install sqlalchemy
    ```

    -  pexpect
    ```
    $ pip install pexpect
    ```

    -  ConfigParser
    ```
    $ pip install ConfigParser
    ```

    -  mysqldb
    ```
    $ pip install mysqldb
    ```

<span></span>
3. manager
-------------

- Docker configuration 수정

	* /usr/lib/systemd/system/docker.service 수정
	```
	ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 \
              -H unix:///var/run/docker.sock \
              --insecure-registry [IP:PORT]
	```

<span></span>
4. worker
-------------

- Docker configuration 수정

	* /usr/lib/systemd/system/docker.service 수정
	```
	ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 \
              -H unix:///var/run/docker.sock \
              --insecure-registry [IP:PORT]
	```

<span></span>
5. registry
-------------

- Docker registry 세팅 - 131(emma)

    - Docker Registry 설치
    ```
    $ yum -y install docker-registry
    ```

    - /etc/docker-registry.yml 편집

    	* line 19 docker registry가 사용할 DB에 sqlalchemy를 통해 접근
        ```
        search_backend: _env:SEARCH_BACKEND:sqlalchemy
        ```

    	* line 21 sqlalchemy (sqlite) 에서 사용할 index 저장소 정의
		```
    	sqlalchemy_index_database: _env:SQLALCHEMY_INDEX_DATABASE:
    	sqlite:////home/fastcat/docker-registry/docker-registry.db
        ```

        * line 74 local에 이미지를 저장할 폴더 지정
        ```
        storage_path: _env:STORAGE_PATH:/home/fastcat/docker-registry
        ```

    - 폴더 생성
    ```
    mkdir /home/fastcat/docker-registry
	```

    - /etc/sysconfig/docker-registry 편집

    	* line 11 docker registry 포트 지정
        ```
        REGISTRY_PORT=5555
        ```
    - systemctl enable docker-registry
    - systemctl start docker-registry

<span></span>
6. example shell
-------------
- docker-install.sh
    ```
    #!/bin/bash
    > /etc/yum.repos.d/docker.repo
    echo '[dockerrepo]' >> docker.repo
    echo 'name=Docker Repository' >> docker.repo
    echo 'baseurl=https://yum.dockerproject.org/repo/main/centos/7/' >> docker.repo
    echo 'enabled=1' >> docker.repo
    echo 'gpgcheck=1' >> docker.repo
    echo 'gpgkey=https://yum.dockerproject.org/gpg' >> docker.repo

    yum -y install docker-engine

    sed -i 's/ExecStart=\/usr\/bin\/dockerd/ExecStart=\/usr\/bin\/dockerd \
            -H tcp:\/\/0.0.0.0:2375 -H unix:\/\/\/var\/run\/docker.sock \
            --insecure-registry 192.168.0.20:5000/g' \
            /usr/lib/systemd/system/docker.service

    systemctl enable docker
    systemctl start docker
    ```

- python-install.sh
    ```
    #!/bin/bash
    rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    yum -y update
    yum -y install python-pip
    pip install flask
    pip install sqlalchemy
    pip install pexpect
    pip install ConfigParser
    pip install mysqldb
    ```

- docker-registry-install.sh
    ```
    yum -y install docker-registry
    sed -i 's/starch_backend: _env:SEARCH_BACKEND/search_backend: _env:SEARCH_BACKEND:sqlalchemy/g' \
            /etc/docker-registry.yml
    sed -i 's/sqlite:\/\/\/\/tmp\/docker-registry.db/sqlite:\/\/\/\/home\/gncloud\/docker-registry\/docker-registry.db/g' \
            /etc/docker-registry.yml
    sed -i 's/\/var\/lib\/docker-registry/\/home\/gncloud\/docker-registry/g' \
            /etc/docker-registry.yml

    > /home/gncloud/docker-registry
    systemctl enable docker-registry
    systemctl start docker-registry
    ```
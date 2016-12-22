# Container Controller 환경구성

1. 공통
2. controller
3. manager
4. worker
5. registry


<span></span>
1. 공통
-------------

- docker 설치

	- 1.12.4 버전


<span></span>
2. controller
-------------

- python 설치

	- 2.7.12 버전 설치

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

    	* line 19
        ```
        search_backend: _env:SEARCH_BACKEND:sqlalchemy
        ```

    	* line 21
		```
    	sqlalchemy_index_database: _env:SQLALCHEMY_INDEX_DATABASE:
    	sqlite:////home/fastcat/docker-registry/docker-registry.db
        ```

    - 폴더 생성
    ```
    mkdir /home/fastcat/docker-registry
	```

    - /etc/sysconfig/docker-registry 편집

    	* line 11
        ```
        REGISTRY_PORT=5555
        ```
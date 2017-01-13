# Gncloud private platform Database, docker registry install

1. 설치 절차
2. gncloud-registry-install.sh 실행
3. shell 내용

<span></span>
1. 설치 절차
------------

- 공통 
    - root 권한획득
    - gncloud-install.tgz를 설치할 HOST (H/W)에 복사
    - tar xvzf gncloud-install.tgz

<span></span>
2. gncloud-registry-install.sh 실행
--------------------------------------

- 압축이 풀린 폴더 중 gncloud platform mariadb, docker-registry를 설치하기 위해 
    ```
    $ cd ./gncloud-install/gncloud-platform-db-registry
    $ chmod +x *.sh
    $ ./gncloud-platform-install.sh /data/docker-registry 
       (파라미터는 docker-registry image 저장소 위치 지정)
    ```

<span></span>
3. shell 내용
-------------

- docker registry install 

    ```
    yum -y install docker-registry
    mkdir -p $1
    path=$(echo $1 | sed 's/\//\\\//g')
    if [ -e /etc/docker-registry.yml.org ]
    then
    	cp /etc/docker-registry.yml.org /etc/docker-registry.yml
    else
	    cp /etc/docker-registry.yml /etc/docker-registry.yml.org
    fi
    sed -i "s/starch_backend: _env:SEARCH_BACKEND/search_backend: _env:SEARCH_BACKEND:sqlalchemy/g" /etc/docker-registry.yml
    sed -i "s/sqlite:\/\/\/\/tmp\/docker-registry.db/sqlite:\/\/\/$path\/docker-registry.db/g" /etc/docker-registry.yml
    sed -i "s/\/var\/lib\/docker-registry/$path/g" /etc/docker-registry.yml
    mkdir /srv/docker-registry
    systemctl enable docker-registry
    systemctl start docker-registry
    ```

- mariadb install
    ```
    if [ -e /etc/yum.repos.d/mariadb.repo ]
    then
        echo "기존의 mariadb yum file을 사용하여 mariadb를 인스톨 합니다."
    else
        > /etc/yum.repos.d/mariadb.repo
        echo "[mariadb]" >> /etc/yum.repos.d/mariadb.repo
        echo "name=MariaDB" >> /etc/yum.repos.d/mariadb.repo
        echo "baseurl = http://yum.mariadb.org/10.1/centos6-amd64" >> /etc/yum.repos.d/mariadb.repo
        echo "gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB" >> /etc/yum.repos.d/mariadb.repo
        echo "gpgcheck=1" >> /etc/yum.repos.d/mariadb.repo
    fi

    yum -y install mariadb-server

    sed -i "/\[mysqld\]/ a bind-address=0.0.0.0" /etc/my.cnf
    sed -i "/\[mysqld\]/ a collation-server=utf8_general_ci" /etc/my.cnf
    sed -i "/\[mysqld\]/ a character-set-server=utf8" /etc/my.cnf
    sed -i "/\[mysqld\]/ a lower_case_table_names = 1" /etc/my.cnf

    systemctl enable mariadb
    systemctl start mariadb

    mysql -u root << EOF
    connect mysql;
    update user set password = password('gncloud') where user = 'root';
    create database gncloud;
    CREATE USER 'gncloud'@'localhost' IDENTIFIED BY 'gncloud';
    CREATE USER 'gncloud'@'%' IDENTIFIED BY 'gncloud';
    grant all privileges on gncloud.* to 'gncloud' identified by 'gncloud';
    flush privileges;
    quit
    EOF

    mysql -ugncloud -pgncloud < GNCLOUD_create_table.sql
    mysql -ugncloud -pgncloud < GN_USERS_superuser.sql
    mysql -ugncloud -pgncloud < GN_USER_TEAMS_superuser.sql
    ```


#!/bin/bash

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




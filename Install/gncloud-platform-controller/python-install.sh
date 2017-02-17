#!/bin/bash

# python 설치
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
yum -y install python-dateutil


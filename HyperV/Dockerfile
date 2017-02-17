FROM python:2.7

# install python
RUN apt-get update && \
        apt-get install -y python python-dev python-distribute python-pip && \
        apt-get install -y libcurl4-openssl-dev libxml2-dev libxslt1-dev python-lxml python-mysqldb libpq-dev

# install requirements
RUN pip install -U pip setuptools  && \
        pip install flask && \
        pip install sqlalchemy && \
        pip install pexpect && \
        pip install ConfigParser && \
        pip install apscheduler && \
        pip install humanfriendly && \
        pip install logger && \
        pip install python-dateutil && \
        pip install requests && \
        apt-get install uwsgi

RUN mkdir -p /var/lib/gncloud/HyperV
COPY HyperV /var/lib/gncloud/.
RUN export PYTHONPATH=/var/lib/gncloud

EXPOSE 80

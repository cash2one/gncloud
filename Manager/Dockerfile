FROM python:2.7
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/var/lib/gncloud

# install python
RUN apt-get update && \
        apt-get install -y apt-utils && \
        apt-get install -y python python-dev python-distribute python-pip && \
        apt-get install -y libcurl4-openssl-dev libxml2-dev libxslt1-dev python-lxml python-mysqldb libpq-dev && \
        pip install -U pip setuptools  && \
        pip install flask && \
        pip install sqlalchemy && \
        pip install pexpect && \
        pip install ConfigParser && \
        pip install apscheduler && \
        pip install humanfriendly && \
        pip install logger && \
        pip install python-dateutil && \
        pip install requests && \
        pip install datetime && \
        pip install MySQL-python && \
        apt-get -y install uwsgi&& \
        apt-get install -y uwsgi-plugin-python

RUN mkdir -p /var/lib/gncloud/HyperV

RUN mkdir -p /var/log/gncloud

COPY conf        /var/lib/gncloud/Manager/conf
COPY db          /var/lib/gncloud/Manager/db
COPY service     /var/lib/gncloud/Manager/service
COPY util        /var/lib/gncloud/Manager/util
COPY templates   /var/lib/gncloud/Manager/templates
COPY __init__.py /var/lib/gncloud/Manager/__init__.py
COPY execute_uwsgi.sh  /
RUN chmod +x execute_uwsgi.sh

RUN ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/
RUN cp -R /usr/local/lib/python2.7/* /usr/lib/python2.7/.

EXPOSE 80

CMD ["/execute_uwsgi.sh","80"]
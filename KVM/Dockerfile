FROM fedora/systemd-systemd
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/var/lib/gncloud:/usr/local/lib/python2.7:/usr/lib/python2.7

# install python
RUN     rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
        yum -y update && \
        yum -y install python-pip && \
        yum -y install uwsgi && \
        yum -y install uwsgi-plugin-python && \
        yum -y install python-devel && \
        yum -y install MySQL-python && \
        pip install --upgrade pip && \
        pip install flask && \
        pip install sqlalchemy && \
        pip install pexpect && \
        pip install ConfigParser && \
        pip install apscheduler && \
        pip install humanfriendly && \
        pip install logger && \
        pip install --upgrade Flask-SQLAlchemy && \
        pip install python-dateutil && \
        pip install requests && \
        pip install datetime && \
        pip install MySQL-python

RUN mkdir -p /var/lib/gncloud/KVM

RUN mkdir -p /var/log/gncloud

COPY conf        /var/lib/gncloud/KVM/conf
COPY db          /var/lib/gncloud/KVM/db
COPY service     /var/lib/gncloud/KVM/service
COPY util        /var/lib/gncloud/KVM/util
COPY templates   /var/lib/gncloud/KVM/templates
COPY __init__.py /var/lib/gncloud/KVM/__init__.py
COPY execute_uwsgi.sh  /
RUN chmod +x execute_uwsgi.sh

RUN ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/

EXPOSE 80

CMD ["/execute_uwsgi.sh","80"]

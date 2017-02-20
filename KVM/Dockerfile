FROM fedora/systemd-systemd
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/var/lib/gncloud:/usr/local/lib/python2.7:/usr/lib/python2.7

# install python
RUN     dnf -y update && \
        dnf -y install python-pip && \
        dnf -y install python-devel && \
        dnf -y install uwsgi-plugin-python && \
        dnf -y install python-devel && \
        dnf -y install MySQL-python && \
        dnf -y groupinstall "Development Tools" && \
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
        pip install uwsgi

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

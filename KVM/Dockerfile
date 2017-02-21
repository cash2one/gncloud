FROM centos
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/var/lib/gncloud

# install python
RUN     rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN        yum -y update
RUN        yum -y install qemu-kvm libvirt virt-install bridge-utils
RUN        yum -y install python-pip
RUN        yum -y install python-devel
RUN        yum -y install uwsgi-plugin-python
RUN        yum -y install MySQL-python
RUN        yum -y groupinstall "Development Tools"
RUN        yum -y install uwsgi
RUN        pip install --upgrade pip
RUN        pip install flask
RUN        pip install sqlalchemy
RUN        pip install pexpect
RUN        pip install ConfigParser
RUN        pip install apscheduler
RUN        pip install humanfriendly
RUN        pip install logger
RUN        pip install --upgrade Flask-SQLAlchemy
RUN        pip install python-dateutil
RUN        pip install requests
RUN        pip install datetime

RUN mkdir -p /var/lib/gncloud/KVM

RUN mkdir -p /var/log/gncloud

COPY conf        /var/lib/gncloud/KVM/conf
COPY db          /var/lib/gncloud/KVM/db
COPY service     /var/lib/gncloud/KVM/service
COPY util        /var/lib/gncloud/KVM/util
COPY templates   /var/lib/gncloud/KVM/templates
COPY __init__.py /var/lib/gncloud/KVM/__init__.py

RUN echo "#!/bin/bash" > /execute_uwsgi.sh
RUN echo "uwsgi --http-socket :80 --plugin python --wsgi-file /var/lib/gncloud/KVM/__init__.py --logto /var/log/gncloud/kvm.log --processes 4 --threads 2 --callable app" >> /execute_uwsgi.sh
RUN chmod +x /execute_uwsgi.sh

EXPOSE 80

CMD ["/execute_uwsgi.sh","80"]

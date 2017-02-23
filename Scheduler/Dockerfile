FROM centos
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/var/lib/gncloud

# install python
RUN rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum -y update && \
    yum -y groupinstall "Development Tools" && \
    yum -y install \
        python-pip \
        python-devel \
        uwsgi-plugin-python \
        MySQL-python \
        supervisor \
        uwsgi

COPY requirements.txt /var/lib/gncloud/Scheduler/
RUN pip install --upgrade pip
RUN pip install -r /var/lib/gncloud/Scheduler/requirements.txt

RUN mkdir -p /var/log/gncloud
COPY supervisor-app.ini /etc/supervisord.d/

COPY controller  /var/lib/gncloud/Scheduler/controller
COPY db          /var/lib/gncloud/Scheduler/db
COPY service     /var/lib/gncloud/Scheduler/service
COPY util        /var/lib/gncloud/Scheduler/util
COPY __init__.py /var/lib/gncloud/Scheduler/__init__.py

EXPOSE 80

CMD ["supervisord", "-n", "-c", "/etc/supervisord.conf"]
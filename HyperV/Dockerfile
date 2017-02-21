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

COPY requirements.txt /var/lib/gncloud/HyperV/
RUN pip install --upgrade pip
RUN pip install -r /var/lib/gncloud/HyperV/requirements.txt

RUN mkdir -p /var/log/gncloud
COPY supervisor-app.ini /etc/supervisord.d/

COPY conf        /var/lib/gncloud/HyperV/conf
COPY controller  /var/lib/gncloud/HyperV/controller
COPY db          /var/lib/gncloud/HyperV/db
COPY service     /var/lib/gncloud/HyperV/service
COPY util        /var/lib/gncloud/HyperV/util
COPY __init__.py /var/lib/gncloud/HyperV/__init__.py

EXPOSE 80

CMD ["supervisord", "-n", "-c", "/etc/supervisord.conf"]
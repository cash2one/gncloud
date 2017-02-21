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

COPY requirements.txt /var/lib/gncloud/Manager/
RUN pip install --upgrade pip
RUN pip install -r /var/lib/gncloud/Manager/requirements.txt

RUN mkdir -p /var/log/gncloud
COPY supervisor-app.ini /etc/supervisord.d/

COPY conf        /var/lib/gncloud/Manager/conf
COPY db          /var/lib/gncloud/Manager/db
COPY service     /var/lib/gncloud/Manager/service
COPY util        /var/lib/gncloud/Manager/util
COPY templates   /var/lib/gncloud/Manager/templates
COPY __init__.py /var/lib/gncloud/Manager/__init__.py

EXPOSE 80

CMD ["supervisord", "-n", "-c", "/etc/supervisord.conf"]
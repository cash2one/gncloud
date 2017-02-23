FROM centos7
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/var/lib/gncloud

# install python
RUN rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

RUN >/etc/yum.repos.d/docker.repo
RUN echo '[dockerrepo]' >> /etc/yum.repos.d/docker.repo
RUN echo 'name=Docker Repository' >> /etc/yum.repos.d/docker.repo
RUN echo 'baseurl=https://yum.dockerproject.org/repo/main/centos/7/' >> /etc/yum.repos.d/docker.repo
RUN echo 'enabled=1' >> /etc/yum.repos.d/docker.repo
RUN echo 'gpgcheck=1' >> /etc/yum.repos.d/docker.repo
RUN echo 'gpgkey=https://yum.dockerproject.org/gpg' >> /etc/yum.repos.d/docker.repo

RUN yum history sync

RUN yum -y update && \
    yum -y groupinstall "Development Tools" && \
    yum -y install \
        python-pip \
        python-devel \
        uwsgi-plugin-python \
        MySQL-python \
        supervisor \
        uwsgi \
        docker-engine

RUN systemctl enable docker

COPY requirements.txt /var/lib/gncloud/Docker/
RUN pip install --upgrade pip
RUN pip install -r /var/lib/gncloud/Docker/requirements.txt

RUN mkdir -p /var/log/gncloud
COPY supervisor-app.ini /etc/supervisord.d/

COPY controller  /var/lib/gncloud/Docker/controller
COPY db          /var/lib/gncloud/Docker/db
COPY service     /var/lib/gncloud/Docker/service
COPY util        /var/lib/gncloud/Docker/util
COPY __init__.py /var/lib/gncloud/Docker/

EXPOSE 80

CMD ["supervisord", "-n", "-c", "/etc/supervisord.conf"]


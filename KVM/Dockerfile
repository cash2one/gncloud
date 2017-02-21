FROM centos
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/var/lib/gncloud

# install python
RUN rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum -y update && \
    yum -y groupinstall "Development Tools" && \
    yum -y install qemu-kvm \
        libvirt \
        virt-install \
        bridge-utils \
        python-pip \
        python-devel \
        uwsgi-plugin-python \
        MySQL-python \
        supervisor \
        uwsgi

COPY requirements.txt /var/lib/gncloud/KVM/
RUN pip install --upgrade pip
RUN pip install -r /var/lib/gncloud/KVM/requirements.txt

RUN mkdir -p /var/log/gncloud
RUN mkdir -p /data/kvm/sshkeys # TODO /var/lib/gncloud/KVM/sshkeys
COPY supervisor-app.ini /etc/supervisord.d/

COPY conf        /var/lib/gncloud/KVM/conf
COPY db          /var/lib/gncloud/KVM/db
COPY service     /var/lib/gncloud/KVM/service
COPY util        /var/lib/gncloud/KVM/util
COPY templates   /var/lib/gncloud/KVM/templates
COPY __init__.py /var/lib/gncloud/KVM/__init__.py

EXPOSE 80

CMD ["supervisord", "-n", "-c", "/etc/supervisord.conf"]

# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from fabric.api import run
from fabric.context_managers import env


def docker_info():
    run("docker info")


def docker_manager():
    env.user = 'docker'
    # list of server setting
    # env.hosts = ['192.168.0.20', '192.168.0.25', '192.168.0.33']
    env.hosts = ['192.168.0.20']
    # Password
    env.password = 'docker'
    # pem file
    # env.key_filename = '~/pem/pemfile.pem'


def docker_service_create(name, connect_port, in_port, image, environmant=""):
    command = "docker service create"
    command += " --name %s" % name
    command += " -p %s:%s" % (connect_port, in_port)
    if len(environmant) != 0:
        command += " -e %s" % environmant
    command += " %s" % image
    return run(command)


def run_command(command):
    run(command)

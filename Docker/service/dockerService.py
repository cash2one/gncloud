# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from docker import Client


class DockerService(object):

    def __init__(self, docker_url):
        self.cli = Client(base_url=docker_url)

    def get_container_list(self):
        return self.cli.containers()

    def new_image(self):
        return self.new_img

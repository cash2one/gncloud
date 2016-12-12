# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

# import os
# import docker
from docker import Client


# cli = Client(base_url='tcp://192.168.0.131:2375', version='1.12')
cli = Client(base_url='tcp://192.168.0.131:8888', version='1.12')
# docker daemon -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock &
image_list = cli.images()
print image_list

''' 이미지 가져오기 '''
# image = cli.pull("ubuntu:latest")
# print image

container = cli.create_container(image="ubuntu:latest", name="jhjeon_test", detach=True)
cli.start(container["Id"])

# response = cli.start(container=container.get('Id'))
# print response

''' docker remove '''
# print cli.remove_container("f28a377eaa567738358ca92462bde137402dfc02567b6027f94a24b3cb50a56a")

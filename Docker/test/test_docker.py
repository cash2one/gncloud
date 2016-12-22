# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

# from service.dockerService import DockerService

# import docker
# from docker import Client
#
#
# # cli = Client(base_url='tcp://192.168.0.131:2375', version='1.12')
# cli = Client(base_url='tcp://192.168.0.22:8888', version='1.12')
# # docker daemon -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock &
# images = cli.images()
# for image in images:
#     print image["RepoTags"]
#
# ''' 이미지 가져오기 '''
# # image = cli.pull("ubuntu:latest")
# # print image
#
# # container = cli.create_container(image="ubuntu:latest", name="jhjeon_test", detach=True)
# # cli.start(container["Id"])
#
# # response = cli.start(container=container.get('Id'))
# # print response
#
# ''' docker remove '''
# # print cli.remove_container("f28a377eaa567738358ca92462bde137402dfc02567b6027f94a24b3cb50a56a")

# result = ''
# result = subprocess.check_output(["fab", "-H", "docker@192.168.0.20", "docker_ps:--help,-a"])
# result = subprocess.check_output(["fab", "-H", "docker@192.168.0.20", "docker_node_ls"])
# result = subprocess.check_output(["fab", "-H", "docker@192.168.0.20", "docker_service_create:'--name test','-p 13306:3306','-e MYSQL_ROOT_PASSWORD\=fastcat1151','mariadb:latest'"])
# result = subprocess.check_output([
#     "fab",
#     "-H",
#     "docker@192.168.0.20",
#     "run_command:command=docker info"
# ])
#
# print docker_info()
# print docker_service_create(name="jhjeon_mysql", connect_port="13222", in_port="22", image="mariadb", environmant="MYSQL_ROOT_PASSWORD='jun24677'")
# print docker_service_ps("jhjeon_mysql")

# ds = DockerService("192.168.0.20", "docker", "docker")
# # print ds.docker_service_rm("test")
# # print ds.docker_service_create(name="test", connect_port="2222", in_port="22", image="mariadb", environmant="MYSQL_ROOT_PASSWORD=fastcat1151")
# print ds.docker_service_ps("test")

# import docker
# from docker import client
#
#
# client = docker.from_env()
#
# services = client.services.list()
# print services
''' 서비스 내 container id 및 container가 위치한 node 가져오기 '''
# from pexpect import pxssh
# from util.config import config
#
# container_list = []
#
# cmd = pxssh.pxssh()
# login_check = cmd.login(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
# cmd.sendline("docker service ps 4si28t2tmzkc")
# cmd.prompt()
#
# command_result = cmd.before.split("\r\n")
#
# for line in command_result:
#     container_info = line.split()
#     if len(container_info) == 0:
#         pass
#     elif container_info[0] == "docker" or container_info[0] == "ID":
#         pass
#     else:
#         container = {}
#         container['internal_id'] = container_info[0]
#         container['internal_name'] = container_info[1]
#         container['host_name'] = container_info[3]
#         container_list.append(container)
# print container_list
import json
from pexpect import pxssh
from util.config import config

container_list = []

cmd = pxssh.pxssh()
login_check = cmd.login(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
cmd.sendline("docker service inspect 4si28t2tmzkc")
cmd.prompt()

result = cmd.before.split("\r\n", 1)[1]
result_json = json.loads(result.replace("\r\n", ""))
print result_json[0]['Spec']['TaskTemplate']['ContainerSpec']['Mounts']

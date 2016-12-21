# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import json
import requests
from pexpect import pxssh
from db.models import GnDockerServices, GnDockerImage, GnDockerImageDetail
from util.config import config


class DockerService(object):

    def __init__(self, addr, id, passwd):
        self.cmd = pxssh.pxssh()
        login_check = self.cmd.login(addr, id, passwd)
        if not login_check:
            # throw exception
            print "SSH 로그인 에러"
            pass

    # Docker 서비스를 생성한다.
    def docker_service_create(self, replicas, image, cpu, memory):
        dockerimage = GnDockerImage.query.filter_by(name=image).first()
        image_detail = GnDockerImageDetail.query.filter_by(id=dockerimage.id).all()
        command = "docker service create"
        # command += " --name %s" % name
        command += " --limit-cpu %s --reserve-cpu %s" % (cpu, cpu)
        command += " --limit-memory %s --reserve-memory %s" % (memory, memory)
        # command += " --replicas %s" % config.REPLICAS
        command += " --replicas %s" % replicas
        command += " --constraint 'node.role != manager'"
        command += " --restart-max-attempts %s" % config.RESTART_MAX_ATTEMPTS
        # type=volume,source=jhjeon_mytomcat,destination=/usr/local/tomcat
        # command += " --mount type=volume,source=%s,destination%s" % config.RESTART_MAX_ATTEMPTS
        for detail in image_detail:
            command += " %s" % detail.argument
        command += " %s" % dockerimage.name
        service_id = self.send_command(command)
        if service_id[:5] == "Error":
            return service_id
        else:
            return self.docker_service_ps(service_id)

    # Docker 서비스 정보를 가지고 온다.
    def docker_service_ps(self, id):
        command = "docker service inspect %s" % id
        return self.send_command_return_json(command)

    # Docker 서비스를 삭제한다.
    def docker_service_rm(self, id):
        command = "docker service rm %s" % id
        return self.send_command(command)

    # Docker 서비스의 컨테이너를 가져온다.
    def get_service_containers(self, id):
        container_list = []
        service = GnDockerServices.query.filter_by(id=id).first()
        if service is None:
            return None
        else:
            command = "docker service ps %s", service.internal_id
            result = self.send_command_return_all_line(command)

            for line in result:
                container_info = line.split()
                if len(container_info) == 0:
                    pass
                elif container_info[0] == "docker" or container_info[0] == "ID":
                    pass
                else:
                    container = {}
                    container['internal_id'] = container_info[0]
                    container['internal_name'] = container_info[1]
                    container['host_name'] = container_info[3]
                    container_list.append(container)
            return container_list

    # Docker 서비스의 볼륨 정보를 가져온다.
    def get_service_volumes(self, id):
        volume_list = []
        service = GnDockerServices.query.filter_by(id=id).first()
        if service is None:
            return None
        else:
            command = "docker service inspect %s" % service.internal_id
            result = self.send_command_return_json(command)
            return result[0]['Spec']['TaskTemplate']['ContainerSpec']['Mounts']

    #
    def send_command(self, command):
        self.cmd.sendline(command)
        self.cmd.prompt()
        result = self.cmd.before.split("\r\n", 1)[1]
        return result.replace("\r\n", "")

    #
    def send_command_return_all_line(self, command):
        self.cmd.sendline(command)
        self.cmd.prompt()
        return self.cmd.before.split("\r\n")

    def send_command_return_json(self, command):
        self.cmd.sendline(command)
        self.cmd.prompt()
        result = self.cmd.before.split("\r\n", 1)[1]
        return json.loads(result.replace("\r\n", ""))

    #
    def send(self, address, port, method, uri, data={}):
        url = "http://" + address
        url += ":"
        url += port
        url += uri
        if method == "GET":
            response = requests.get(url, data=json.dumps(data))
        elif method == "POST":
            response = requests.post(url, data=json.dumps(data))
        elif method == "PUT":
            response = requests.put(url, data=json.dumps(data))
        elif method == "DELETE":
            response = requests.delete(url, data=json.dumps(data))
        # response = requests.delete(url, data=json.dumps(data), timeout=1000 * 60 * 20)
        return json.loads(response.json())

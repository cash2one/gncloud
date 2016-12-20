# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import json
import requests
from pexpect import pxssh
from db.models import GnDockerImage, GnDockerImageDetail
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
    def docker_service_create(self, image, cpu, memory):
        dockerimage = GnDockerImage.query.filter_by(name=image).first()
        image_detail = GnDockerImageDetail.query.filter_by(id=dockerimage.id).all()
        command = "docker service create"
        # command += " --name %s" % name
        command += " --limit-cpu %s --reserve-cpu %s" % (cpu, cpu)
        command += " --limit-memory %s --reserve-memory %s" % (memory, memory)
        command += " --replicas %s" % config.REPLICAS
        command += " --restart-max-attempts %s" % config.RESTART_MAX_ATTEMPTS
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

    def send_command(self, command):
        self.cmd.sendline(command)
        self.cmd.prompt()
        result = self.cmd.before.split("\r\n", 1)[1]
        return result.replace("\r\n", "")

    def send_command_return_json(self, command):
        self.cmd.sendline(command)
        self.cmd.prompt()
        result = self.cmd.before.split("\r\n", 1)[1]
        return json.loads(result.replace("\r\n", ""))

    #
    def send(self, method, script, data={}):
        address = "192.168.22.23"
        port = "5000"
        url = "http://" + address
        url += ":"
        url += port
        url += script
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

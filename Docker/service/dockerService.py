# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import json
from pexpect import pxssh


class DockerService(object):

    def __init__(self, addr, id, passwd):
        self.cmd = pxssh.pxssh()
        login_check = self.cmd.login(addr, id, passwd)
        if not login_check:
            # throw exception
            pass

    # Docker 서비스를 생성한다.
    def docker_service_create(self, name, cpu, memory, connect_port, in_port, image, environmant=""):
        command = "docker service create"
        command += " --name %s" % name
        command += " --limit-cpu %s --reserve-cpu %s" % (cpu, cpu)
        command += " --limit-memory %s --reserve-memory %s" % (memory, memory)
        command += " --replicas 1"
        command += " --restart-max-attempts 3"
        command += " -p %s:%s" % (connect_port, in_port)
        if len(environmant) != 0:
            command += " -e %s" % environmant
        command += " %s" % image
        service_id = self.send_command(command)
        return self.docker_service_ps(service_id)

    def docker_service_ps(self, id):
        command = "docker service inspect %s" % id
        return self.send_command_return_json(command)

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

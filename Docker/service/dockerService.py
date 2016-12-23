# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import json
import requests
from pexpect import pxssh
from db.models import GnDockerServices, GnDockerImage, GnDockerImageDetail, GnHostDocker
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
    def docker_service_create(self, id, replicas, image, cpu, memory):
        dockerimage = GnDockerImage.query.filter_by(name=image).first()
        if dockerimage is None:
            return None
        image_detail = GnDockerImageDetail.query.filter_by(id=dockerimage.id).all()
        command = "docker service create"
        # command += " --name %s" % name
        command += " --limit-cpu %s" % cpu
        command += " --limit-memory %s" % memory
        # command += " --replicas %s" % config.REPLICAS
        command += " --replicas %s" % replicas
        command += " --constraint 'node.hostname != manager'"
        command += " --restart-max-attempts %s" % config.RESTART_MAX_ATTEMPTS
        # type=volume,source=jhjeon_mytomcat,destination=/usr/local/tomcat
        # command += " --mount type=volume,source=%s,destination%s" % config.RESTART_MAX_ATTEMPTS
        for detail in image_detail:
            if detail.arg_type == "mount":
                command += " " + (detail.argument % id)
            else:
                command += " %s" % detail.argument
        command += " %s" % dockerimage.name
        service_id = self.send_command(command)
        if service_id[:5] == "Error":
            return service_id
        else:
            return self.docker_service_ps(service_id)

    # Docker 서비스 정보를 가지고 온다.
    def docker_service_ps(self, internal_id):
        command = "docker service inspect %s" % internal_id
        return self.send_command_return_json(command)

    # Docker 서비스를 삭제한다.
    def docker_service_rm(self, internal_id):
        command = "docker service rm %s" % internal_id
        return self.send_command(command)

    # Docker 볼륨을 삭제한다.
    def docker_volume_rm(self, host_id, internal_id):
        node = GnHostDocker.query.filter_by(id=host_id).first()
        command = "docker -H %s:2375 volume rm %s" % (node.ip, internal_id)
        return self.send_command(command)

    # Docker 서비스의 컨테이너를 가져온다.
    def get_service_containers(self, internal_id):
        container_list = []
        command = "docker service ps %s" % internal_id
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
    # 매개변수의 internal_id는
    def get_service_volumes(self, internal_id):
        command = "docker service inspect %s" % internal_id
        result = self.send_command_return_json(command)
        return result[0]['Spec']['TaskTemplate']['ContainerSpec']['Mounts']

    # Docker Service의 Containers Commit
    # 매개변수의 id는 서비스 DB id
    # commit된 이미지의 이름은 서비스 DB id, tag는 backup으로 하자.
    def commit_containers(self, id):
        # Service internal id 가지고 오기
        service = GnDockerServices.query.filter_by(id=id).first()
        # 서비스의 Container 목록 가지고 오기
        containers = self.get_service_containers(service.internal_id)
        # 각 컨테이너를 commit하기
        # docker -H {ip}:2375 commit
        # $(docker -H {ip}:2375 ps --filter label=com.docker.swarm.service.name={internal_name} -q)
        # {id}:stop
        result_list = []
        for container in containers:
            node = GnHostDocker.query.filter_by(id=container.host_id).first()
            ip = node.ip
            name = container.name
            command = "docker -H %s:2375 commit " \
                      "$(docker -H %s:2375 ps --filter label=com.docker.swarm.service.name=%s -q) " \
                      "%s:backup" % (ip, ip, name, id)
            result = self.send_command(command)
            result_list.append(result)
        return result_list

    # command 전달 후 결과값 상단 한줄 받아오기
    def send_command(self, command):
        self.cmd.sendline(command)
        self.cmd.prompt()
        result = self.cmd.before.split("\r\n", 1)[1]
        return result.replace("\r\n", "")

    # command 전달 후 결과값을 Line 기준 List로 받아오기
    def send_command_return_all_line(self, command):
        self.cmd.sendline(command)
        self.cmd.prompt()
        return self.cmd.before.split("\r\n")

    # command 전달 후 결과값을 json 객체로 받아오기
    def send_command_return_json(self, command):
        self.cmd.sendline(command)
        self.cmd.prompt()
        result = self.cmd.before.split("\r\n", 1)[1]
        return json.loads(result.replace("\r\n", ""))

    # 내부에서 REST API 호출용 함수
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

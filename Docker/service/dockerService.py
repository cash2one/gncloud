# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import json
import requests
import time
from pexpect import pxssh
from datetime import datetime
from Docker.db.models import GnDockerContainers, GnDockerImages, GnDockerImageDetail, GnHostMachines, GnVmMachines, GnDockerVolumes
from Docker.util.config import config
from Docker.util.logger import logger


class DockerService(object):

    def __init__(self, addr, id, passwd):
        self.cmd = pxssh.pxssh()
        self.login_check = self.cmd.login(addr, id, passwd)
        if not self.login_check:
            logger.error("SSH 로그인 에러")

    # Docker 서비스를 생성한다.
    def docker_service_create(self, id, image_id, cpu, memory):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        dockerimage = GnDockerImages.query.filter_by(id=image_id).first()
        if dockerimage is None:
            return None
        image_detail = GnDockerImageDetail.query.filter_by(image_id=dockerimage.id).all()
        # --- Docker Service 생성 커맨드 작성 ---
        command = "docker service create"
        command += " --limit-cpu %s" % cpu
        command += " --limit-memory %s" % memory
        command += " --replicas %s" % config.REPLICAS
        command += " --constraint 'node.hostname != manager'"
        command += " --restart-max-attempts %s" % config.RESTART_MAX_ATTEMPTS
        for detail in image_detail:
            if detail.arg_type == "mount":
                command += " " + (detail.argument % id)
            else:
                command += " %s" % detail.argument
        command += " %s" % dockerimage.name
        logger.debug("Docker Service Created: %s", command)
        # --- //Docker Service 생성 커맨드 작성 ---
        service_id = self.send_command(command)
        if service_id[:5] == "Error":
            return service_id
        else:
            return self.docker_service_ps(service_id)

    # Docker 서비스 다시 시작 (실제로는 commit된 이미지로 서비스 생성)
    def docker_service_start(self, id, image, backup_image, cpu, memory):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        dockerimage = GnDockerImages.query.filter_by(name=image).first()
        if dockerimage is None:
            return None
        image_detail = GnDockerImageDetail.query.filter_by(image_id=dockerimage.id).all()
        # --- Docker Service 생성 커맨드 작성 ---
        command = "docker service create"
        command += " --limit-cpu %s" % cpu
        command += " --limit-memory %s" % memory
        command += " --replicas %s" % config.REPLICAS
        command += " --constraint 'node.hostname != manager'"
        command += " --restart-max-attempts %s" % config.RESTART_MAX_ATTEMPTS
        for detail in image_detail:
            if detail.arg_type == "mount":
                command += " " + (detail.argument % id)
            else:
                command += " %s" % detail.argument
        command += " %s" % backup_image
        service_id = self.send_command(command)
        # --- //Docker Service 생성 커맨드 작성 ---
        if service_id[:5] == "Error":
            return service_id
        else:
            return self.docker_service_ps(service_id)

    # 서비스 정지 (라 해 놓고 서비스 내 컨테이너 백업 후 서비스 삭제)
    def docker_service_stop(self, service):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        # 컨테이너를 commit하여 저장
        # commit_result = ds.commit_containers(id)
        self.commit_containers(service.id)
        # 서비스 삭제
        # service_delete_result = ds.docker_service_rm(service.internal_id)
        self.docker_service_rm(service.internal_id)

    # Docker 서비스 정보를 가지고 온다.
    def docker_service_ps(self, internal_id):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        command = "docker service inspect %s" % internal_id
        return self.send_command_return_json(command)

    # Docker 서비스를 삭제한다.
    def docker_service_rm(self, internal_id):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        command = "docker service rm %s" % internal_id
        return self.send_command(command)

    # Docker 볼륨을 삭제한다.
    def docker_volume_rm(self, host_id, volumes):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        node = GnHostMachines.query.filter_by(id=host_id).first()
        volume_list = ""
        for volume in volumes:
            volume_list += "%s " % volume.name
        command = "docker -H %s:2375 volume rm %s" % (node.ip, volume_list)
        return self.send_command(command)

    # Docker 서비스의 컨테이너를 가져온다.
    def get_service_containers(self, internal_id):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        container_list = []
        command = "docker service ps %s" % internal_id
        result = self.send_command_return_all_line(command)
        for line in result:
            logger.debug("get_service_containers result line: %s" % line)
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
                # 호스트 네임이 DB에 존재하지 않는 값이 나온다면 None을 리턴, 컨트롤러에서는 이 함수를 다시 호출하게 한다.
                node = GnHostMachines.query.filter_by(name=container['host_name']).one_or_none()
                if node is None:
                    return None
                container_list.append(container)
        return container_list

    # Docker 서비스의 볼륨 정보를 가져온다.
    # 매개변수의 internal_id는
    def get_service_volumes(self, internal_id):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        command = "docker service inspect %s" % internal_id
        # 서비스 내의 Mounts 정보 가져오기
        service = self.send_command_return_json(command)
        mounts = service[0]['Spec']['TaskTemplate']['ContainerSpec']['Mounts']
        # 볼륨의 목적지를 확인한다. 모든 노드의 볼륨이 동일하다는 전제 하에 첫 번째 worker 노드에서 볼륨 값을 가져온다.
        host = GnHostMachines.query.filter_by(type="docker_w").first()
        for mount in mounts:
            command = "docker -H %s:2375 volume inspect %s" % (host.ip, mount["Source"])
            volume = ""
            while type(volume) is not list:
                volume = self.send_command_return_json(command)
            mount['Mountpoint'] = volume[0]['Mountpoint']
        return mounts

    # Docker Service의 Containers Commit
    # 매개변수의 id는 서비스 DB id
    # commit된 이미지의 이름은 서비스 DB id, tag는 backup으로 하자.
    def commit_containers(self, id):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        # Service internal id 가지고 오기
        service = GnVmMachines.query.filter_by(id=id).first()
        service_internal_name = service.internal_name
        # 서비스의 Container 목록 가지고 오기
        # containers = self.get_service_containers(service.internal_id)
        containers = GnDockerContainers.query.filter_by(service_id=service.id).all()
        # 각 컨테이너를 commit하기
        # docker -H {ip}:2375 commit
        # $(docker -H {ip}:2375 ps --filter label=com.docker.swarm.service.name={internal_name} -q)
        # {id}:stop
        result_list = []
        for container in containers:
            node = GnHostMachines.query.filter_by(id=container.host_id).first()
            ip = node.ip
            command = "docker -H %s:2375 commit " \
                      "$(docker -H %s:2375 ps --filter label=com.docker.swarm.service.name=%s -q) " \
                      "%s:backup" % (ip, ip, service_internal_name, id)
            result = self.send_command(command)
            result_list.append(result)
        return result_list

    # Docker Service의 Containers Commit (다만 스냅샷이므로 커밋하는 이미지는 하나만으로)
    # 매개변수의 id는 서비스 DB id
    # commit된 이미지의 이름은 서비스 DB id, tag는 backup으로 하자.
    def snap_containers(self, id):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        sub_type = "snap"
        # Service internal id 가지고 오기
        service = GnVmMachines.query.filter_by(id=id, type="docker").first()
        service_internal_name = service.internal_name
        # 서비스의 Container 목록 가지고 오기
        # containers = self.get_service_containers(service.internal_id)
        container = GnDockerContainers.query.filter_by(service_id=service.id).first()
        # 각 컨테이너를 commit하기
        # docker -H {ip}:2375 commit
        # $(docker -H {ip}:2375 ps --filter label=com.docker.swarm.service.name={internal_name} -q)
        # {id}:stop
        first_worker = GnHostMachines.query.filter_by(id=container.host_id).first()
        registry = GnHostMachines.query.filter_by(type="docker_r").first()
        # 스냅샷 이미지 이름에 넣기 위한 현재 시각 저장
        snaptime = datetime.now().strftime('%Y%m%d%H%M%S')
        # 스냅샷 이미지 이름 정의
        snap_image_name = "%s:5000/%s_%s:%s" % (registry.ip, service.name, snaptime, sub_type)
        # 스냅샷 이미지 커밋
        commit_command = "docker -H %s:2375 commit " \
                  "$(docker -H %s:2375 ps --filter label=com.docker.swarm.service.name=%s -q) " \
                  "%s" % (first_worker.ip, first_worker.ip, service_internal_name, snap_image_name)
        commit_result = self.send_command_return_all_line(commit_command)
        # 스냅샷 이미지 레지스트리에 저장
        push_command = "docker -H %s:2375 push %s" % (first_worker.ip, snap_image_name)
        push_result = self.send_command_return_all_line(push_command)
        return {
            "status": True,
            "commit_result": commit_result,
            "push_result": push_result,
            "name": snap_image_name,
            "sub_type": sub_type
        }

    # --- 여기서부터는 Docker 커맨드 실행 && Docker REST API 사용 관련 함수 ---

    # command 전달 후 결과값 상단 한줄 받아오기
    def send_command(self, command):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        self.cmd.sendline(command)
        self.cmd.prompt()
        result = self.cmd.before.split("\r\n", 1)[1]
        return result.replace("\r\n", "")

    # command 전달 후 결과값을 Line 기준 List로 받아오기
    def send_command_return_all_line(self, command):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        self.cmd.sendline(command)
        self.cmd.prompt()
        return self.cmd.before.split("\r\n")

    # command 전달 후 결과값을 json 객체로 받아오기
    def send_command_return_json(self, command):
        if not self.login_check:
            logger.error("SSH 로그인 에러")
            return "SSH 로그인 에러"
        try:
            self.cmd.sendline(command)
            self.cmd.prompt()
            result = self.cmd.before.split("\r\n", 1)[1]
            result = json.loads(result.replace("\r\n", ""))
        except ValueError as e:
            return "ValueError %s" % e
        return result

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

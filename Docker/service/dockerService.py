# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import json
import time
from datetime import datetime

import requests
from pexpect import pxssh
from sqlalchemy import and_

from Docker.db.models import GnDockerContainers, GnDockerImages, GnDockerImageDetail, GnHostMachines, GnVmMachines
from Docker.util.config import config
from Docker.util.logger import logger

class DockerService(object):

    def __init__(self, addr, id, sql_session):
        self.addr = addr
        self.id = id
        self.sql_session = sql_session

    # Docker 서비스를 생성한다.
    #def docker_service_create(self, id, image_id, cpu, memory):
    def docker_service_create(self, docker_info):
        sql_session = self.sql_session
        id = docker_info.id
        image_id = docker_info.image_id
        cpu = docker_info.cpu
        memory = docker_info.memory

        dockerimage = sql_session.query(GnDockerImages).filter(GnDockerImages.id == image_id).first()
        #dockerimage = GnDockerImages.query.filter_by(id=image_id).first()
        if dockerimage is None:
            return None

        real_image_id = None
        if dockerimage.sub_type == 'snap':
            real_image_id = dockerimage.base_image
        else:
            real_image_id = dockerimage.id

        #image_detail = GnDockerImageDetail.query.filter_by(image_id=real_image_id).all()
        image_detail = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.image_id == real_image_id).all()
        # --- Docker Service 생성 커맨드 작성 ---
        command = "docker service create"
        command += " --limit-cpu %s" % cpu
        command += " --limit-memory %s" % memory
        command += " --replicas %s" % config.REPLICAS
        command += " --constraint 'node.hostname != manager'"
        command += " --restart-max-attempts %s" % config.RESTART_MAX_ATTEMPTS
        command = '%s --name="%s"' % (command, docker_info.name)
        mount_count = 1;
        for detail in image_detail:
            if detail.arg_type == "mount":
                # command += " " + (detail.argument % id)
                split_data = detail.argument.split(':')
                mount_type = split_data[0]
                dest_path=''
                if len(split_data) > 1:
                    dest_path = split_data[1]

                if mount_type == 'LOG' or mount_type == 'DATA':
                    command = '%s --mount type=volume,source=%s_%s_%d_%s,destination=%s' % (command, dockerimage.name, id, mount_type, mount_type, dest_path)
                    mount_count += 1
                '''
                else:
                    option = detail.argument % id
                    command = '%s %s' % (command, option)
                '''
            else:
                command = '%s %s' % (command, detail.argument)
        command += " %s" % dockerimage.view_name
        logger.debug("Docker Service Created: %s", command)
        sql_session.commit()
        # --- //Docker Service 생성 커맨드 작성 ---
        service_id = self.send_command(command, 1)
        if service_id[:5] == "Error":
            return service_id
        else:
            return self.docker_service_ps(service_id)

    # Docker 서비스 다시 시작 (실제로는 commit된 이미지로 서비스 생성)
    def docker_service_start(self, id, image, backup_image, cpu, memory):
        sql_session = self.sql_session
        #dockerimage = GnDockerImages.query.filter_by(view_name=image).first()
        dockerimage = sql_session.query(GnDockerImages).filter(GnDockerImages.view_name==image).first()
        if dockerimage is None:
            return None

        #image_detail = GnDockerImageDetail.query.filter_by(image_id=dockerimage.id).all()
        image_detail = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.image_id == dockerimage.id).all()
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

        sql_session.commit()
        service_id = self.send_command(command, 1)
        # --- //Docker Service 생성 커맨드 작성 ---
        if service_id[:5] == "Error":
            return service_id
        else:
            time.sleep(2)
            return self.docker_service_ps(service_id)

    # 서비스 정지 (라 해 놓고 서비스 내 컨테이너 백업 후 서비스 삭제)
    def docker_service_stop(self, service):
        # 컨테이너를 commit하여 저장
        # commit_result = ds.commit_containers(id)
        self.commit_containers(service.id)
        # 서비스 삭제
        # service_delete_result = ds.docker_service_rm(service.internal_id)
        self.docker_service_rm(service.internal_id)

    # Docker 서비스 정보를 가지고 온다.
    def docker_service_ps(self, internal_id):
        result=''
        command = "docker service inspect %s" % internal_id
        try:
            # docker swarm manager need a second for assigning to service port
            time.sleep(3)
            result = self.send_command(command, 3)
        except Exception as e:
            logger.error(e)

        return result

    # Docker 서비스를 삭제한다.
    def docker_service_rm(self, internal_id):
        command = "docker service rm %s" % internal_id
        return self.send_command(command, 1)

    # Docker 볼륨을 삭제한다.
    def docker_volume_rm(self, ip, volumes):
        command = "docker -H %s:2375 volume rm %s" % (ip, volumes)
        logger.debug(command)
        return self.send_command(command, 1)

    # Docker 서비스의 컨테이너를 가져온다.
    def get_service_containers(self, internal_id):
        container_list = []
        command = "docker service ps %s" % internal_id
        result = self.send_command(command, 2)

        for line in result:
            logger.debug("get_service_containers result line: %s" % line)
            container_info = line.split()
            if len(container_info) == 0:
                pass
            elif container_info[0] == "docker" or container_info[0] == "ID":
                pass
            else:
                if container_info[0] is None:
                    return None
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
    def get_service_volumes(self, internal_id, host_ip):
        command = "docker service inspect %s" % internal_id
        # 서비스 내의 Mounts 정보 가져오기
        service = self.send_command(command, 3)
        container_spec_list = service[0]['Spec']['TaskTemplate']['ContainerSpec']
        ok_volume = False
        for isExist in container_spec_list:
            if isExist == 'Mounts':
                ok_volume = True
                break

        if ok_volume:
            mounts = service[0]['Spec']['TaskTemplate']['ContainerSpec']['Mounts']
        else:
            return None

        for mount in mounts:
            command = "docker -H %s:2375 volume inspect %s" % (host_ip, mount["Source"])
            volume = ""
            while type(volume) is not list:
                volume = self.send_command(command, 3)
            mount['Mountpoint'] = volume[0]['Mountpoint']
        return mounts

    # Docker Service의 Containers Commit
    # 매개변수의 id는 서비스 DB id
    # commit된 이미지의 이름은 서비스 DB id, tag는 backup으로 하자.
    def commit_containers(self, id):
        sql_session = self.sql_session
        # Service internal id 가지고 오기
        #service = GnVmMachines.query.filter_by(id=id).first()
        service = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()
        service_internal_name = service.internal_name
        # 서비스의 Container 목록 가지고 오기
        # containers = self.get_service_containers(service.internal_id)
        # containers = GnDockerContainers.query.filter_by(service_id=service.id).all()
        containers = sql_session.query(GnDockerContainers).filter(GnDockerContainers.service_id==service.id).all()
        # 각 컨테이너를 commit하기
        # docker -H {ip}:2375 commit
        # $(docker -H {ip}:2375 ps --filter label=com.docker.swarm.service.name={internal_name} -q)
        # {id}:stop
        result_list = []
        for container in containers:
            #node = GnHostMachines.query.filter_by(id=container.host_id).first()
            node = sql_session.query(GnHostMachines).filter(GnHostMachines.id==container.host_id).first()
            ip = node.ip
            command = "docker -H %s:2375 commit " \
                      "$(docker -H %s:2375 ps --filter label=com.docker.swarm.service.name=%s -q) " \
                      "%s:backup" % (ip, ip, service_internal_name, id)
            result = self.send_command(command, 1)
            result_list.append(result)
        sql_session.commit()
        return result_list

    # Docker Service의 Containers Commit (다만 스냅샷이므로 커밋하는 이미지는 하나만으로)
    # 매개변수의 id는 서비스 DB id
    # commit된 이미지의 이름은 서비스 DB id, tag는 backup으로 하자.
    def snap_containers(self, id):
        sql_session = self.sql_session
        sub_type = "snap"
        # Service internal id 가지고 오기
        #service = GnVmMachines.query.filter_by(id=id, type="docker").first()
        service = sql_session.query(GnVmMachines).filter(and_(GnVmMachines.id==id,GnVmMachines.type=='docker')).first()
        service_internal_name = service.internal_name
        # 서비스의 Container 목록 가지고 오기
        # containers = self.get_service_containers(service.internal_id)
        # container = GnDockerContainers.query.filter_by(service_id=service.id).first()
        container = sql_session.query(GnDockerContainers).filter(GnDockerContainers.service_id==service.id).first()
        # 각 컨테이너를 commit하기
        # docker -H {ip}:2375 commit
        # $(docker -H {ip}:2375 ps --filter label=com.docker.swarm.service.name={internal_name} -q)
        # {id}:stop
        #first_worker = GnHostMachines.query.filter_by(id=container.host_id).first()
        first_worker = sql_session.query(GnHostMachines).filter(GnHostMachines.id==container.host_id).first()
        #registry = GnHostMachines.query.filter_by(type="docker_r").first()
        #registry = GnHostMachines.query.filter(GnHostMachines.type=='docker').filter(GnHostMachines.name=='registry').first()
        registry = sql_session.query(GnHostMachines).filter(and_(GnHostMachines.type=='docker',
                                                                 GnHostMachines.name=='registry')).first()
        # 스냅샷 이미지 이름에 넣기 위한 현재 시각 저장
        snaptime = datetime.now().strftime('%Y%m%d%H%M%S')
        # 스냅샷 이미지 이름 정의
        snap_image_name = "%s:5000/%s_%s:%s" % (registry.ip, service.name, snaptime, sub_type)
        # 스냅샷 이미지 커밋
        commit_command = "docker -H %s:2375 commit " \
                  "$(docker -H %s:2375 ps --filter label=com.docker.swarm.service.name=%s -q) " \
                  "%s" % (first_worker.ip, first_worker.ip, service_internal_name, snap_image_name)

        sql_session.commit()
        commit_result = self.send_command(commit_command, 2)
        # 스냅샷 이미지 레지스트리에 저장
        push_command = "docker -H %s:2375 push %s" % (first_worker.ip, snap_image_name)
        push_result = self.send_command(push_command, 2)
        return {
            "status": True,
            "commit_result": commit_result,
            "push_result": push_result,
            "name": snap_image_name,
            "sub_type": sub_type
        }


    # --- 여기서부터는 Docker 커맨드 실행 && Docker REST API 사용 관련 함수 ---
    def send_command(self, command, lines):
        login_count = 0

        ssh = pxssh.pxssh()
        login_result = ssh.login(self.addr, self.id)
        while not login_result:
            if login_count > 5:
                logger.debug('login error')
                break
            time.sleep(5)
            login_result = ssh.login(self.addr, self.id)
            login_count += 1

        ssh.sendline(command)
        ssh.prompt()
        if lines == 1:
            # command 전달 후 결과값 상단 한줄 받아오기
            result = ssh.before.split("\r\n", 1)[1]
            result = result.replace("\r\n", "")
        elif lines == 2:
            # command 전달 후 결과값을 Line 기준 List로 받아오기
            result = ssh.before.split("\r\n")
        elif lines == 3:
            # command 전달 후 결과값을 json 객체로 받아오기
            result = ssh.before.split("\r\n", 1)[1]
            result = json.loads(result.replace("\r\n", ""))
        else:
            result = 'Error'

        ssh.logout()
        ssh.close()
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

    def get_filelist(self, host_ip, path):
        command ="cd %s; ls -l | awk '{print $5, $9}'" % path

        login_count = 0
        ssh = pxssh.pxssh()
        login_result = ssh.login(host_ip, self.id)
        while not login_result:
            if login_count > 5:
                logger.debug('login error')
                break
            time.sleep(2)
            login_result = ssh.login(host_ip, self.id)
            login_count += 1

        ssh.sendline(command)
        ssh.prompt()
        result = ssh.before

        ssh.logout()
        ssh.close()
        return result

    def get_filecontents(self, host_ip, volume_source_path, filename):
        command = 'tail -n 1000 %s/%s' % (volume_source_path, filename)

        login_count = 0
        ssh = pxssh.pxssh()
        login_result = ssh.login(host_ip, self.id)
        while not login_result:
            if login_count > 5:
                logger.debug('login error')
                break
            time.sleep(2)
            login_result = ssh.login(host_ip, self.id)
            login_count += 1

        ssh.sendline(command)
        ssh.prompt()
        result = ssh.before

        ssh.logout()
        ssh.close()
        return result


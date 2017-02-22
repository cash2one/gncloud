# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import json
import time
import subprocess
from datetime import datetime
import requests
from pexpect import pxssh

from Docker.util.config import Config
from Docker.util.logger import logger

class DockerService(object):
    def __init__(self, ip, port):
        self.ip=ip
        self.port=port

    # Docker 서비스를 생성한다.
    def docker_service_create(self, container_info, image_info, image_detail, ip, port):
        try:
            real_image_id = None
            if image_info.sub_type == 'snap':
                real_image_id = image_info.base_image
            else:
                real_image_id = image_info.id

            # --- Docker Service 생성 커맨드 작성 ---
            command = "docker -H %s:%s service create" % (ip, port)
            command += " --limit-cpu %s" % container_info.cpu
            command += " --limit-memory %s" % container_info.memory
            command += " --replicas %s" % Config.REPLICAS
            #command += " --constraint 'node.hostname != manager'"
            command += " --restart-max-attempts %s" % Config.RESTART_MAX_ATTEMPTS
            postfix=''
            data_path=''
            mount_count = 1
            for detail in image_detail:
                if detail.arg_type == "mount":
                    # command += " " + (detail.argument % id)
                    split_data = detail.argument.split(':')
                    mount_type = split_data[0]
                    dest_path=''
                    if len(split_data) > 1:
                        dest_path = split_data[1]

                    if mount_type == 'LOG' or mount_type == 'DATA':
                        command = '%s --mount type=volume,source=%s_%s_%d_%s,destination=%s' % \
                                  (command, image_info.name, id, mount_count, mount_type, dest_path)
                        mount_count += 1
                        if mount_type == 'DATA':
                            data_path = '%s_%s_%d_%s/_data' % (image_info.name, container_info.id, mount_count, mount_count)
                elif detail.arg_type == 'log_vol' or detail.arg_type == 'data_vol':
                    mount_type = ''
                    if detail.arg_type == 'log_vol':
                        mount_type = 'LOG'
                    else:
                        mount_type = 'DATA'
                    command = '%s --mount type=volume,source=%s_%s_%d_%s,destination=%s' % \
                              (command, image_info.name, container_info.id, mount_count, mount_type, detail.argument)
                else:
                    if detail.argument.find('--command') >= 0:
                        postfix = '%s %s' % (postfix, detail.argument.split('=')[1])
                    else:
                        command = '%s %s' % (command, detail.argument)
            command = '%s %s' % (command, image_info.view_name)
            command = '%s %s' % (command, postfix)
            logger.debug("Docker Service Created: %s", command)
            # --- //Docker Service 생성 커맨드 작성 ---
            service_id = subprocess.check_call(command, shell=True)
            print 'service id = %s' % service_id
        except Exception as e:
            logger.error('service create error:%s' % e.message)
            return 'Error service create error:%s' % e.message

        if service_id[:5] == "Error":
            logger.error('service create error:%s' % service_id)
            return service_id
        else:

            return self.docker_service_ps(service_id, ip, port)

    # Docker 서비스 다시 시작 (실제로는 commit된 이미지로 서비스 생성)
    def docker_service_start(self, container_info, image_info, image_detail, ip, port):
        try:
            backup_image = '%s:backup' % container_info.id
            # --- Docker Service 생성 커맨드 작성 ---
            command = "docker -H %s:%s service create" % (ip, port)
            command += " --limit-cpu %s" % container_info.cpu
            command += " --limit-memory %s" % container_info.memory
            command += " --replicas %s" % Config.REPLICAS
            #command += " --constraint 'node.hostname != manager'"
            command += " --restart-max-attempts %s" % Config.RESTART_MAX_ATTEMPTS
            mount_count = 1
            postfix=''
            for detail in image_detail:
                if detail.arg_type == "mount":
                    # command += " " + (detail.argument % id)
                    split_data = detail.argument.split(':')
                    mount_type = split_data[0]
                    dest_path=''
                    if len(split_data) > 1:
                        dest_path = split_data[1]

                    if mount_type == 'LOG' or mount_type == 'DATA':
                        command = '%s --mount type=volume,source=%s_%s_%d_%s,destination=%s' % \
                                  (command, image_info.name, container_info.id, mount_count, mount_type, dest_path)
                        mount_count += 1
                        if mount_type == 'DATA':
                            data_path = '%s_%s_%d_%s/_data' % (image_info.name, id, mount_count, mount_count)
                elif detail.arg_type == 'log_vol' or detail.arg_type == 'data_vol':
                    mount_type = ''
                    if detail.arg_type == 'log_vol':
                        mount_type = 'LOG'
                    else:
                        mount_type = 'DATA'
                    command = '%s --mount type=volume,source=%s_%s_%d_%s,destination=%s' % \
                              (command, image_info.name, container_info.id, mount_count, mount_type, detail.argument)
                else:
                    if detail.argument.find('--command') >= 0:
                        postfix = '%s %s' % (postfix, detail.argument.split('=')[1])
                    else:
                        command = '%s %s' % (command, detail.argument)
            command = '%s %s' % (command, backup_image)
            command = '%s %s' % (command, postfix)

            service_id = subprocess.check_output(command, shell=True)
        except Exception as e:
            logger.error('service create error:%s' % e.message)
            return 'Error service create error:%s' % e.message

        if service_id[:5] == "Error":
            logger.error('service create error:%s' % service_id)
            return service_id
        else:
            return self.docker_service_ps(service_id, ip, port)

    # Docker 서비스 정보를 가지고 온다.
    def docker_service_ps(self, internal_id, ip, port):
        result=''
        command = "docker -H %s:%s service inspect %s" % (ip, port, internal_id)
        try:
            # docker swarm manager need a second for assigning to service port
            time.sleep(3)
            result = subprocess.check_output(command, shell=True)
        except Exception as e:
            logger.error(e)

        return result

    # Docker 서비스를 삭제한다.
    def docker_service_rm(self, internal_id, ip, port):
        command = "docker -H %s:%s service rm %s" % (ip, port, internal_id)
        return subprocess.check_output(command, shell=True)

    # Docker 볼륨을 삭제한다.
    def docker_volume_rm(self, volumes, ip, port):
        command = "docker -H %s:%s volume rm %s" % (ip, port, volumes)
        logger.debug(command)
        return subprocess.check_output(command, shell=True)

    # Docker 서비스의 컨테이너를 가져온다.
    def get_service_containers(self, internal_id, ip, port):
        container_list = []
        command = "docker -H %s:%s service ps %s" % (ip, port, internal_id)
        result = subprocess.check_output(command, shell=True)
        result = result.split("\r\n", 1)[1]
        result = json.loads(result.replace("\r\n", ""))
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
                container_list.append(container)
        return container_list

    # Docker 서비스의 볼륨 정보를 가져온다.
    # 매개변수의 internal_id는
    def get_service_volumes(self, internal_id, ip, port):
        mounts = ''
        try:
            command = "docker -H %s:%s service inspect %s" % (ip, port, internal_id)
            # 서비스 내의 Mounts 정보 가져오기
            service = subprocess.check_output(command, shell=True)
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
                command = "docker -H %s:%s volume inspect %s" % (ip, port, mount["Source"])
                volume = ""
                while type(volume) is not list:
                    volume = subprocess.check_output(command, shell=True)
                    volume = volume.split("\r\n", 1)[1]
                    volume = json.loads(volume.replace("\r\n", ""))
                mount['Mountpoint'] = volume[0]['Mountpoint']
            return mounts
        except Exception as e:
            logger.debug('get_service_volumes error = %s' % e)
            logger.debug('mounts = %s' % mounts)
            return None

    # 내부에서 REST API 호출용 함수
    def send(self, address, port, method, uri, data={}):
        response=None
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
        login_result = ssh.login(host_ip, 'root')
        while not login_result:
            if login_count > 5:
                logger.debug('login error')
                break
            time.sleep(2)
            login_result = ssh.login(host_ip, 'root')
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
        login_result = ssh.login(host_ip, 'root')
        while not login_result:
            if login_count > 5:
                logger.debug('login error')
                break
            time.sleep(2)
            login_result = ssh.login(host_ip, 'root')
            login_count += 1

        ssh.sendline(command)
        ssh.prompt()
        result = ssh.before

        ssh.logout()
        ssh.close()
        return result


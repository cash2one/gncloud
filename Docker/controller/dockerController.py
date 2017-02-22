# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import time
import humanfriendly

from flask import jsonify, request, session
from sqlalchemy import and_

from Docker.db.database import db_session
from Docker.db.models import *
from Docker.service.dockerService import DockerService
from Docker.util.config import Config
from Docker.util.hash import random_string
from Docker.util.logger import logger

# init value
DockerService = DockerService('127.0.0.1', '2375')

# Docker Service 생성 및 실행
# 서비스 생성 시에는 실행은 자동이다.
def doc_create(id,sql_session):
    team_name = None
    user_name = None
    container_info = None
    try:
        #로직 변경
        logger.debug("get id"+id)
        container_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()

        swarm_manager = sql_session.query(GnHostMachines).filter(and_(GnHostMachines.type=='docker',
                                                                       GnHostMachines.name=='manager')).first()
        docker_ip = swarm_manager.ip
        docker_port = ''
        if swarm_manager.host_agent_port is None:
            docker_port = '2375'
        else:
            docker_port = str(swarm_manager.host_agent_port)

        if docker_ip.find(':') >=0:
            docker_ip = docker_ip.split(':')[0]
            docker_port = docker_ip.split(':')[1]

        image_info = sql_session.query(GnDockerImages).filter(GnDockerImages.id == container_info.image_id).first()
        image_detail = sql_session.query(GnDockerImageDetail).\
            filter(GnDockerImageDetail.image_id == container_info.image_id).all()

        logger.debug(container_info.id+":request ok")
        docker_service = DockerService.docker_service_create(container_info, image_info, image_detail,
                                                             docker_ip, docker_port)
        logger.debug(container_info.id+":end create")

        # 데이터베이스에 없는 도커 이미지로 컨테이너를 생성할 경우
        if docker_service[:5] == 'Error' or docker_service is None or docker_service == '':
            container_info.status = "Error"
            error_hist = GnErrorHist(type=container_info.type,action="Create",team_code=container_info.team_code,
                                     author_id=container_info.author_id, vm_id=container_info.id,
                                     vm_name=container_info.name, cause=docker_service)
            sql_session.add(error_hist)
            sql_session.commit()
            return jsonify(status=False, message="failure service create.")

        elif type(docker_service) is not list:
            container_info.status = "Error"
            error_hist = GnErrorHist(type=container_info.type,action="Create",team_code=container_info.team_code,
                                     author_id=container_info.author_id, vm_id=container_info.id,
                                     vm_name=container_info.name, cause=docker_service)
            sql_session.add(error_hist)

            sql_session.commit()
            return jsonify(status=False, message=docker_service)
        else:
            image = GnDockerImages.query.filter_by(id=container_info.image_id).one()

            # Service 정보를 DB에 저장한다.
            service_image = GnDockerServices(service_id=id, image=image.view_name)
            sql_session.add(service_image)

            # os=image.os,
            # os_ver=image.os_ver,
            # 생성된 Service의 Container 정보를 DB에 저장한다.
            service_container_count = 0
            service_container_list = DockerService.get_service_containers(docker_service[0]['ID'],
                                                                          docker_ip, docker_port)
            while service_container_list is None or len(service_container_list) == 0:
                if service_container_count > 5:
                    sql_session.rollback()
                    container_info.status = "Error"

                    error_hist = GnErrorHist(type=container_info.type,action="Create",team_code=container_info.team_code,
                                             author_id=container_info.author_id, vm_id=container_info.id, vm_name=container_info.name,
                                             cause=service_container_list)
                    sql_session.add(error_hist)

                    sql_session.commit()
                    DockerService.docker_service_rm(docker_service[0]['ID'], docker_ip, docker_port)
                    return jsonify(status=False, message="서비스 생성 실패: %s" % service_container_list )
                time.sleep(3)
                service_container_list = DockerService.get_service_containers(docker_service[0]['ID'])
                service_container_count += 1
            logger.debug("service_container_list: %s" % service_container_list)
            host_ip_list = []
            for service_container in service_container_list:
                worker = GnHostMachines.query.filter_by(name=service_container['host_name']).one()
                logger.debug("container node: %s" % worker)
                container = GnDockerContainers(
                    service_id=id,
                    internal_id=service_container['internal_id'],
                    internal_name=service_container['internal_name'],
                    host_id=worker.id
                )
                host_ip_list.append(worker.id)
                logger.debug("container: %s" % container)
                sql_session.add(container)
            # 생성된 volume 정보를 DB에 저장한다.

            #service_volume_list = ds.get_service_volumes(docker_service[0]['ID'])
            worker_ip = db_session.query(GnHostMachines).filter(GnHostMachines.id == host_ip_list[0]).first().ip
            service_volume_count=0
            service_volume_list = DockerService.get_service_volumes(docker_service[0]['ID'], docker_ip, worker_ip, docker_port)
            while service_volume_list is None:
                if service_volume_count > 5:
                    break
                time.sleep(3)
                service_volume_list = DockerService.get_service_volumes(docker_service[0]['ID'], docker_ip, worker_ip, docker_port)
                service_container_count += 1

            logger.debug("service_volume_list: %s" % service_volume_list)
            if service_volume_list is not None:
                for service_volume in service_volume_list:
                    volume = GnDockerVolumes(
                        service_id=id,
                        name=service_volume['Source'],
                        source_path=service_volume['Mountpoint'],
                        destination_path=service_volume['Target']
                    )
                    sql_session.add(volume)
            # 생성된 접속 포트 정보를 DB에 저장한다.
            ports = docker_service[0]['Endpoint']['Ports']
            logger.debug("ports: %s" % ports)
            for port in ports:
                set_port = GnDockerPorts(service_id=id, protocol=port['Protocol'], target_port=port['TargetPort'],
                                         published_port=port['PublishedPort'])
                sql_session.add(set_port)

            #sql_session.add(service)
            # 데이터베이스 업데이트
            container_info.ip = swarm_manager.ip + ":%s" % ports[0]['PublishedPort']
            container_info.host_id = swarm_manager.id
            container_info.status = "Running"
            container_info.internal_id = docker_service[0]['ID']
            container_info.internal_name = docker_service[0]['Spec']['Name']
            #docker_info.create_time = datetime.strptime(docker_service[0]['CreatedAt'][:-2], '%Y-%m-%dT%H:%M:%S.%f')
            now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            container_info.create_time = now_time
            container_info.os = "docker"
            container_info.os_ver = image.os
            container_info.os_sub_ver = image.os_ver

            # for insert of GN_INSTANCE_STATUS table
            vm_size = sql_session.query(GnVmSize).filter(GnVmSize.id == container_info.size_id).first()
            instance_status_price = None
            system_setting = sql_session.query(GnSystemSetting).first()
            if system_setting.billing_type == 'D':
                instance_status_price = vm_size.day_price
            elif system_setting.billing_type == 'H':
                instance_status_price = vm_size.hour_price
            else:
                logger.error('invalid price_type : system_setting.billing_type %s' % system_setting.billing_type)

            team_info = sql_session.query(GnTeam).filter(GnTeam.team_code == container_info.team_code).first()
            user_info = sql_session.query(GnUsers).filter(GnUsers.user_id == container_info.author_id).first()
            insert_instance_status = GnInstanceStatus(vm_id=container_info.id,vm_name=container_info.name, create_time=now_time
                              , delete_time=None, author_id=container_info.author_id, author_name=user_info.user_name
                              , team_code=container_info.team_code, team_name=team_info.team_name
                              , price=instance_status_price,price_type=system_setting.billing_type
                              , cpu=container_info.cpu, memory=container_info.memory,disk=container_info.disk)
            sql_session.add(insert_instance_status)

            sql_session.commit()
            return jsonify(status=True, message="서비스를 생성하였습니다.", result=container_info.to_json())
    except Exception as e:
        print(e.message)
        sql_session.rollback()
        error_hist = GnErrorHist(type=container_info.type,action="Create",team_code=container_info.team_code,
                                 author_id=container_info.author_id, vm_id=container_info.id, vm_name=container_info.name,
                                 cause=e.message)
        sql_session.add(error_hist)
        container_info.status = "Error"
        sql_session.commit()
        logger.error(e)
        return jsonify(status=False, message="서비스 생성 실패: %s" % e)


# Docker 서비스 삭제
def doc_delete(id,sql_session):
    # 지정된 Docker 서비스를 삭제한다.
    service=''
    result=''
    logger.debug('delete docker start ~~~')
    try:
        service = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()

        logger.debug('delete docker %s' % service.internal_name)
        # 서비스 삭제 (서비스 및 컨테이너가 삭제된다)
        swarm_manager = sql_session.query(GnHostMachines).filter(and_(GnHostMachines.type=='docker',
                                                                      GnHostMachines.name=='manager')).first()
        docker_ip = swarm_manager.ip
        docker_port = ''
        if swarm_manager.host_agent_port is None:
            docker_port = '2375'
        else:
            docker_port = str(swarm_manager.host_agent_port)

        if docker_ip.find(':') >=0:
            docker_ip = docker_ip.split(':')[0]
            docker_port = docker_ip.split(':')[1]

        result = DockerService.docker_service_rm(service.internal_id, docker_ip, docker_port)
        #wait for remove service complete
        # time.sleep(5)

        logger.debug('after docker_service_rm')

        container_list = sql_session.query(GnDockerContainers).filter(GnDockerContainers.service_id == id).all()
        for container in container_list:
            worker = sql_session.query(GnHostMachines).filter(GnHostMachines.id == container.host_id).first()
            worker_ip = worker.ip
            worker_port = ''
            if worker.host_agent_port is None:
                worker_port = '2375'
            else:
                worker_port = str(worker.host_agent_port)

            if worker_ip.find(':') >=0:
                worker_ip = worker_ip.split(':')[0]
                worker_port = worker_ip.split(':')[1]

            vo_list=''
            volume_list = sql_session.query(GnDockerVolumes).filter(GnDockerVolumes.service_id == id).all()
            for vo in volume_list:
                vo_list = '%s %s' % (vo_list, vo.name)
            result2 = DockerService.docker_volume_rm(vo_list, worker_ip, worker_port)
            rm_count = 0
            check_v_rm = result2.split(' ')[0]
            while check_v_rm == 'Error':
                if rm_count > 5:
                    error_hist = GnErrorHist(type=service.type,action='Delete',team_code=service.team_code,author_id=service.author_id,
                                             vm_id=service.id, vm_name=service.name, cause=check_v_rm)
                    sql_session.add(error_hist)
                    sql_session.commit()
                    return jsonify(status=False, message=check_v_rm)
                time.sleep(5)
                result2 = DockerService.docker_volume_rm(vo_list, worker_ip, worker_port)
                logger.debug('docker_volume_rm %d result = %s' % (rm_count+1, result2))
                check_v_rm = result2.split(' ')[0]
                rm_count += 1

        # DB에 삭제된 내용을 업데이트한다.
        if service is not None:
            # 서비스 상태 수정
            #service.status = "Removed"
            sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).delete()

            # 컨테이너 상태 수정
            sql_session.query(GnDockerContainers).filter(GnDockerContainers.service_id == id).delete()

            # 볼륨 상태 수정
            sql_session.query(GnDockerVolumes).filter(GnDockerVolumes.service_id == id).delete()
            sql_session.query(GnDockerServices).filter(GnDockerServices.service_id == id).delete()

            update_instance_status = db_session.query(GnInstanceStatus).filter(GnInstanceStatus.vm_id == service.id) \
                .update({"delete_time": datetime.datetime.now().strftime('%Y%m%d%H%M%S')})

            sql_session.commit()
    except Exception as err:
        logger.error(err)
        sql_session.rollback()
        error_hist = GnErrorHist(type=service.type,action="Delete",team_code=service.team_code,
                                 author_id=service.author_id, vm_id=service.id, vm_name=service.name,
                                 cause=err.message)
        sql_session.add(error_hist)
        sql_session.commit()

    if result == service.internal_id:
        return jsonify(status=True, message="서비스가 삭제되었습니다.")
    else:
        error_hist = GnErrorHist(type=service.type,action="Delete",team_code=service.team_code,
                                 author_id=service.author_id, vm_id=service.id, vm_name=service.name,
                                 cause=result)
        sql_session.add(error_hist)
        sql_session.commit()
        return jsonify(status=False, message=result)


# Docker Service 정보
def doc_vm(id):
    sql_session = db_session
    user_id = request.args.get("user_id")
    team_code = request.args.get("team_code")
    if team_code is None:
        service = sql_session.query(GnVmMachines).filter(
            GnVmMachines.author_id == user_id, GnVmMachines.id == id, GnVmMachines.status != "Removed"
        ).one()
    else:
        service = sql_session.query(GnVmMachines).filter(
            GnVmMachines.team_code == team_code, GnVmMachines.id == id, GnVmMachines.status != "Removed"
        ).one()
        service = GnVmMachines.query.filter_by(team_code=team_code, id=id).one()
    if service is None:
        logger.debug('cannot get information about service, vm id = %s' % id)
        return jsonify(status=False, message="서비스 정보를 가져올 수 없습니다.")
    else:
        return jsonify(status=True, message="서비스 정보를 가져왔습니다.", result=service.to_json())


# Docker Service 리스트
def doc_vm_list():
    sql_session = db_session
    type = request.args["type"]
    if "team_code" in request.args:
        team_code = request.args["team_code"]
    else:
        team_code = None
    if team_code == "" or team_code is None:
        services = sql_session.query(GnVmMachines).filter(
            GnVmMachines.type == type, GnVmMachines.status != "Removed"
        ).all()
    else:
        services = sql_session.query(GnVmMachines).filter(
            GnVmMachines.team_code == team_code, GnVmMachines.status != "Removed"
        ).all()
    if services is None:
        return jsonify(status=False, message="서비스 정보를 가져올 수 없습니다.")
    else:
        result = []
        for service in services:
            result.append(service.to_json())
        return jsonify(status=True, message="서비스 정보를 가져왔습니다.", result=result)

# Container 이미지 리스트
def doc_image_list():
    imagelist = GnDockerImages.query.all()
    result = []
    for image in imagelist:
        result.append(image.to_json())
    return jsonify(status=True, message="컨테이너 이미지 리스트 호출 완료.", result=result)


# get Container logfiles
def get_container_logfiles(id):
    sql_session = db_session
    try:
        volume_list = sql_session.query(GnDockerVolumes).filter(GnDockerVolumes.service_id == id).all()
        container_list = sql_session.query(GnDockerContainers).filter(GnDockerContainers.service_id == id).all()
        result = '#'

        for container in container_list:
            host = sql_session.query(GnHostMachines).filter(GnHostMachines.id == container.host_id).first()
            host_ip = host.ip
            result = '%s%s' % (result, host.name)
            for volume in volume_list:
                if volume.source_path.find('LOG') >= 0:
                    file_list = DockerService.get_filelist(host_ip, volume.source_path)
                    result = '%s\r\n%s' % (result, file_list)
            result = '%s#' % result

        sql_session.commit()

        result_list=result.split('#')

        all_result =[]
        host_count = 0
        hostname = ''
        for log_unit in result_list:
            if log_unit != '' and log_unit != ' ':
                log_files = log_unit.split('\r\n')
                ff_list = []
                ls_count = 0
                for some_file in log_files:
                    if ls_count == 0:
                        hostname = some_file
                    elif ls_count > 2 and some_file != '':
                        sep = some_file.split(' ')
                        human_size = humanfriendly.format_size(int(sep[0]),binary=True).replace("i","")
                        ff_list.append({"filename":sep[1], "filesize":human_size})
                    ls_count += 1
                all_result.append({"hostname":hostname, "filelist":ff_list})
                #all_result.append(ff_list)
                host_count += 1
        print (all_result)
        return jsonify(status=True, message="success filelist", list=all_result)
    except Exception as msg:
        sql_session.rollback()
        logger.debug('filelist error %s' % msg.message)
        return jsonify(status=False, message="failure filelist", result=msg.message)


#get logfile's contents
def get_contents(id, filename, worker_name):
    sql_session = db_session
    f_contents=''
    try:
        log_host = sql_session.query(GnHostMachines).filter(GnHostMachines.name == worker_name).first()
        volumes = sql_session.query(GnDockerVolumes).filter(GnDockerVolumes.service_id == id).all()
        for log_volume in volumes:
            if log_volume.source_path.find('LOG') >= 0:
                f_contents = DockerService.get_filecontents(log_host.ip, log_volume.source_path, filename)
                break

        #f_contents = f_contents.split('\r\n')[1:]
        if len(f_contents) > 0:
            pos = f_contents.find('\r\n')
            if pos >= 0:
                f_contents = f_contents[pos+2:]

        sql_session.commit()
        return jsonify(status=True, message="success filecontents", list=f_contents)
    except Exception as msg:
        sql_session.rollback()
        logger.debug('filecontents error %s' % msg.message)
        return jsonify(status=False, message="failure filecontents", list=msg.message)



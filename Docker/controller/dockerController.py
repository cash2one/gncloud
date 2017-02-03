# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import time
from datetime import datetime

from flask import jsonify, request, session

from Docker.db.database import db_session
from Docker.db.models import *
from Docker.service.dockerService import DockerService
from Docker.util.config import config
from Docker.util.hash import random_string
from Docker.util.logger import logger


# Docker Service 생성 및 실행
# 서비스 생성 시에는 실행은 자동이다.
def doc_create(id,sql_session):
    team_name = None
    user_name = None
    #로직 변경
    print("get id"+id)
    docker_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    if docker_info is not None:
        team_name = sql_session.query(GnTeam).filter(GnTeam.team_code == docker_info.team_code).one()
        user_name = sql_session.query(GnUsers).filter(GnUsers.user_id == docker_info.author_id).one()

    ds = None
    try:
        image_id = docker_info.image_id
        name = docker_info.name
        cpu = docker_info.cpu
        disk = docker_info.disk
        memory = "%sB" % docker_info.memory
        tag = docker_info.tag
        print(docker_info.id+":request ok")

        print("id: %s, image_id: %s, name: %s, tag: %s, cpu: %s, disk: %s, memory: %s" %
              (id, image_id, name, tag, cpu, disk, memory))
        # --- //파라미터 정리 ---
        # --- Docker Service (밖에서 보기엔 컨테이너 생성) 생성 ---
        ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
        login_check = ds.docker_login()
        login_count = 0
        while not login_check:
            if login_count > 5:
                docker_info.status = 'Error'
                sql_session.commit()
                return jsonify(status=False, message="login failure")
            time.sleep(10)
            login_check = ds.docker_login()
            login_count += 1

        print(docker_info.id+":get class ok")

        # Docker Swarm manager 값을 가져온다.
        dsmanager = GnHostMachines.query.filter_by(type='docker_m').one()
        # Docker Swarm Service를 생성한다.
        # docker_service_create: Docker Service 생성
        print(docker_info.id+":start create")
        docker_service = ds.docker_service_create(id=id, image_id=image_id, cpu=cpu, memory=memory)
        print(docker_info.id+":end create")
        # 데이터베이스에 없는 도커 이미지로 컨테이너를 생성할 경우
        if docker_service is None:
            ds.logout()
            return jsonify(status=False, message="존재하지 않는 도커 이미지입니다.")
        if type(docker_service) is not list:
            ds.logout()
            return jsonify(status=False, message=docker_service)
        else:
            image = GnDockerImages.query.filter_by(id=image_id).one()

            # Service 정보를 DB에 저장한다.
            service_image = GnDockerServices(service_id=id, image=image.name)
            sql_session.add(service_image)

            # os=image.os,
            # os_ver=image.os_ver,
            # 생성된 Service의 Container 정보를 DB에 저장한다.
            service_container_list = ds.get_service_containers(docker_service[0]['ID'])
            while service_container_list is None:
                time.sleep(3)
                service_container_list = ds.get_service_containers(docker_service[0]['ID'])
            logger.debug("service_container_list: %s" % service_container_list)
            for service_container in service_container_list:
                node = GnHostMachines.query.filter_by(name=service_container['host_name']).one()
                logger.debug("container node: %s" % node)
                container = GnDockerContainers(
                    service_id=id,
                    internal_id=service_container['internal_id'],
                    internal_name=service_container['internal_name'],
                    host_id=node.id
                )
                logger.debug("container: %s" % container)
                sql_session.add(container)
            # 생성된 volume 정보를 DB에 저장한다.
            service_volume_list = ds.get_service_volumes(docker_service[0]['ID'])
            logger.debug("service_volume_list: %s" % service_volume_list)
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
                set_port = GnDockerPorts(service_id=id, protocol=port['Protocol'], target_port=port['TargetPort'], published_port=port['PublishedPort'])
                sql_session.add(set_port)

            #sql_session.add(service)
            # 데이터베이스 업데이트
            docker_info.ip = dsmanager.ip + ":%s" % ports[0]['PublishedPort']
            docker_info.host_id = dsmanager.id
            docker_info.status = "Running"
            docker_info.internal_id = docker_service[0]['ID']
            docker_info.internal_name = docker_service[0]['Spec']['Name']
            #docker_info.create_time = datetime.strptime(docker_service[0]['CreatedAt'][:-2], '%Y-%m-%dT%H:%M:%S.%f')
            now_time = datetime.now().strftime('%Y%m%d%H%M%S')
            docker_info.create_time = now_time
            docker_info.os = "docker"
            docker_info.os_ver = image.os
            docker_info.os_sub_ver = image.os_ver

            # for insert of GN_INSTANCE_STATUS table
            vm_size = sql_session.query(GnVmSize).filter(GnVmSize.id == docker_info.size_id).first()
            instance_status_price = None
            system_setting = sql_session.query(GnSystemSetting).first()
            if system_setting.billing_type == 'D':
                instance_status_price = vm_size.day_price
            elif system_setting.billing_type == 'H':
                instance_status_price = vm_size.hour_price
            else:
                logger.error('invalid price_type : system_setting.billing_type %s' % system_setting.billing_type)

            insert_instance_status = GnInstanceStatus(vm_id=docker_info.id,vm_name=docker_info.name, create_time=now_time
                                                      , delete_time=None, author_id=docker_info.author_id, author_name=user_name.user_name
                                                      , team_code=docker_info.team_code, team_name=team_name.team_name
                                                      , price=instance_status_price,price_type=system_setting.billing_type
                                                      , cpu=docker_info.cpu, memory=docker_info.memory,disk=docker_info.disk)
            sql_session.add(insert_instance_status)

            sql_session.commit()
            ds.logout()
            return jsonify(status=True, message="서비스를 생성하였습니다.", result=docker_info.to_json())
    except Exception as e:
        sql_session.rollback()
        error_hist = GnErrorHist(type=docker_info.type,action="Create",team_code=docker_info.team_code,author_id=docker_info.author_id, vm_id=docker_info.id, vm_name=docker_info.name)
        sql_session.add(error_hist)
        docker_info.status = "Error"
        sql_session.commit()
        logger.error(e)
        if ds is not None :
            ds.logout()
        return jsonify(status=False, message="서비스 생성 실패: %s" % e)


# Docker Service 상태변경
# {name: '시작', type: 'resume'},
# {name: '정지', type: 'suspend'},
# {name: '재시작', type: 'reboot'}
def doc_state(id):
    sql_session = db_session
    #print db_session
    type = request.json["type"]
    # if 'userName' in request.json:
    #     author_id = request.json['userName']
    # else:
    #     author_id = session['userName']
    # if 'teamCode' in request.json:
    #     team_code = request.json['teamCode']
    # else:
    #     team_code = session['teamCode']
    # count = request.json["count"] # 쓸 일 없을 듯...
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    login_check = ds.docker_login()
    login_count = 0
    while not login_check:
        if login_count > 5:
            docker_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
            docker_info.status = 'Error'
            sql_session.commit()
            return jsonify(status=False, message="login failure")
        time.sleep(10)
        login_check = ds.docker_login()
        login_count += 1
    # 서비스 DB 데이터 가져오기
    service = GnVmMachines.query.filter_by(id=id, type="docker").one()
    # -- 시작 (start)
    # service
    if type == "Resume":
        # 이미 서비스가 돌아가는 상태인 경우는 아무 것도 안하고 끝낸다.
        if service.status == "Running":
            ds.logout()
            return jsonify(status=False, message="서비스가 이미 실행중입니다.", result=service.to_json())
        else:
            # commit된 내용을 가지고 서비스 생성.
            # image = "%s:backup" % service.internal_name
            image = "%s:backup" % service.id
            restart_service = ds.docker_service_start(
                id=id, image=service.gnDockerServices[0].image, backup_image=image,
                cpu=service.cpu, memory=str(service.memory)+"MB")
            logger.debug(restart_service)
            if restart_service == 'error':
                service.status = 'Error'
                sql_session.commit()
                ds.logout()
                return jsonify(status=False, message="error", result=None)

            # 변경된 내용을 DB에 Update
            # 서비스쪽 데이터 수정
            service.internal_id = restart_service[0]["ID"]
            service.internal_name = restart_service[0]['Spec']['Name']
            service.start_time = datetime.strptime(restart_service[0]['CreatedAt'][:-2], '%Y-%m-%dT%H:%M:%S.%f')
            service.status = "Running"
            time.sleep(2)
            # 컨테이너 데이터 수정
            service_container_list = ds.get_service_containers(restart_service[0]["ID"])
            for service_container in service_container_list:
                node = GnHostMachines.query.filter_by(name=service_container['host_name']).first()
                container = GnDockerContainers.query.filter_by(service_id=id, host_id=node.id).first()
                container.internal_id = service_container['internal_id']
                container.internal_name = service_container['internal_name']
            # 볼륨은 변경사항이 없기에 수정 X..? (이미지 세부사항 추가 시의 경우를 생각해 둘 필요성은 있음)
            # 포트 정보 수정
            ports = restart_service[0]['Endpoint']['Ports']
            for port in ports:
                getports = GnDockerPorts.query.filter_by(protocol=port['Protocol'], target_port=port['TargetPort']).all()
                for getport in getports:
                    sql_session.delete(getport)
                sql_session.commit()
                set_port = GnDockerPorts(service_id=id, protocol=port['Protocol'], target_port=port['TargetPort'], published_port=port['PublishedPort'])
                sql_session.add(set_port)
            sql_session.commit()
            ds.logout()
            return jsonify(status=True, message="서비스가 시작되었습니다.", result=service.to_json())
    # -- 정지 (suspend)
    elif type == "Suspend":
        if service.status != "Running":
            ds.logout()
            return jsonify(status=False, message="서비스가 실행중이 아닙니다.", result=service.to_json())
        else:
            ds.docker_service_stop(service)
            service.stop_time = datetime.now()
            service.ssh_key_id = "1"
            service.status = "Suspend"
            sql_session.commit()
            ds.logout()
            return jsonify(status=True, message="서비스가 정지되었습니다.", result=service.to_json())
    # -- 재시작 (restart)
    elif type == "Reboot":
        if service.status == "Running":
            ds.docker_service_stop(service)
            service.stop_time = datetime.now()
            service.status = "Suspend"
            sql_session.commit()
            # commit된 내용을 가지고 서비스 생성.
            # image = "%s:backup" % service.internal_name
        image = "%s:backup" % service.id
        restart_service = ds.docker_service_start(
            id=id, image=service.gnDockerServices[0].image, backup_image=image,
            cpu=service.cpu, memory=str(service.memory) + "MB")
        logger.debug(restart_service)
        # 변경된 내용을 DB에 Update
        # 서비스쪽 데이터 수정
        service.internal_id = restart_service[0]["ID"]
        service.internal_name = restart_service[0]['Spec']['Name']
        service.start_time = datetime.strptime(restart_service[0]['CreatedAt'][:-2], '%Y-%m-%dT%H:%M:%S.%f')
        service.status = "Running"
        # 컨테이너 데이터 수정
        time.sleep(2)
        service_container_list = ds.get_service_containers(restart_service[0]["ID"])
        for service_container in service_container_list:
            node = GnHostMachines.query.filter_by(name=service_container['host_name']).first()
            container = GnDockerContainers.query.filter_by(service_id=id, host_id=node.id).first()
            container.internal_id = service_container['internal_id']
            container.internal_name = service_container['internal_name']
        # 볼륨은 변경사항이 없기에 수정 X..? (이미지 세부사항 추가 시의 경우를 생각해 둘 필요성은 있음)
        # 포트 정보 수정
        ports = restart_service[0]['Endpoint']['Ports']
        for port in ports:
            getports = GnDockerPorts.query.filter_by(protocol=port['Protocol'], target_port=port['TargetPort']).all()
            for getport in getports:
                sql_session.delete(getport)
            sql_session.commit()
            set_port = GnDockerPorts(service_id=id, protocol=port['Protocol'], target_port=port['TargetPort'], published_port=port['PublishedPort'])
            sql_session.add(set_port)
        sql_session.commit()
        ds.logout()
        return jsonify(status=True, message="서비스가 재시작되었습니다.", result=service.to_json())
    else:
        ds.logout()
        return jsonify(status=False, message="정의된 상태값이 아닙니다.")


# Docker Service 스냅샷 저장
def doc_snap():
    ds = None
    try:
        sql_session = db_session
        if 'userId' in request.json:
            user_id = request.json['userId']
        else:
            user_id = session['userId']
        if 'teamCode' in request.json:
            team_code = request.json['teamCode']
        else:
            team_code = session['teamCode']
        ord_id = request.json['ord_id']
        name = request.json['name']
        ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
        # ds.docker_create_snapshot(ord_id, name, user_id, team_code)
        # -- 스냅샷
        service = GnDockerServices.query.filter_by(service_id=ord_id).one()
        # baseimage = GnDockerImages.query.filter_by(name=service.image).one()
        baseimage = service.gnDockerImages
        # 이미지 커밋 및 레지스트리에 스냅샷 이미지 저장
        snapshot = ds.snap_containers(ord_id)
        # Docker Image 정보 입력
        image_id = random_string(config.SALT, 8)
        # id 중복 체크 (랜덤값 중 우연히 기존에 있는 id와 같은 값이 나올 수도 있음...)
        while len(GnDockerImages.query.filter_by(id=ord_id).all()) != 0:
            image_id = random_string(config.SALT, 8)
        # 이미지 Tag 중복 체크 중복되는 값이 존재할 경우 False 리턴 후 종료.
        if len(GnDockerImages.query.filter_by(name=snapshot["name"]).all()) != 0:
            ds.logout()
            return jsonify(status=False, message="이미 존재하는 이미지입니다.")
        image = GnDockerImages(
            id=image_id, base_image=baseimage.id, name=snapshot["name"], view_name=name, tag=baseimage.tag, os=baseimage.os,
            os_ver=baseimage.os_ver, sub_type=snapshot["sub_type"], team_code=team_code, author_id=user_id,
            create_time=datetime.now(), status="Running"
        )
        sql_session.add(image)
        sql_session.commit()
        sql_session.remove()
        # result 값에서 에러가 발생하여 일단 주석처리 해둠.
        # return jsonify(status=True, message="Success", result=image.to_json())
        ds.logout()
        return jsonify(status=True, message="Success")
    except Exception as err:
        if ds is not None:
            ds.logout()
        return jsonify(status=False, message="Error: %s" % err)


# Docker 서비스 삭제
def doc_delete(id,sql_session):
    ds = None
    # 지정된 Docker 서비스를 삭제한다.

    logger.debug('delete docker start ~~~')
    try:
        ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
        login_check = ds.docker_login()
        login_count = 0
        while not login_check:
            if login_count > 5:
                docker_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
                docker_info.status = 'Error'
                sql_session.commit()
                return jsonify(status=False, message="login failure")
            time.sleep(10)
            login_check = ds.docker_login()
            login_count += 1

        logger.debug('after ssh shell prompt')
        service = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()

        logger.debug('delete docker %s' % service.internal_name)
        # 서비스 삭제 (서비스 및 컨테이너가 삭제된다)
        result = ds.docker_service_rm(service.internal_id)
        logger.debug('after docker_service_rm')
        for container in service.gnDockerContainers:
            # 각 컨테이너 노드 별로 존재하는 볼륨 삭제
            result2 = ds.docker_volume_rm(container.host_id, service.gnDockerVolumes)
        logger.debug('after docker_volume_rm')
        # DB에 삭제된 내용을 업데이트한다.
        if service is not None:
            # 서비스 상태 수정
            #service.status = "Removed"
            sql_session.query(GnVmMachines).filter(GnVmMachines.id == service.id).delete()

            # 컨테이너 상태 수정
            for container in service.gnDockerContainers:
                sql_session.query(GnDockerContainers).filter(GnDockerContainers.service_id == container.service_id).delete()
                # container.status = "Removed"
            # 볼륨 상태 수정
            for volume in service.gnDockerVolumes:
                sql_session.query(GnDockerVolumes).filter(GnDockerVolumes.service_id == volume.service_id).delete()
                #volume.status = "Removed"

            sql_session.query(GnDockerServices).filter(GnDockerServices.service_id == service.id).delete()

            update_instance_status = db_session.query(GnInstanceStatus).filter(GnInstanceStatus.vm_id == service.id) \
                .update({"delete_time": datetime.now().strftime('%Y%m%d%H%M%S')})

            sql_session.commit()
        ds.logout()
    except Exception as err:
        logger.error(err)

    if result == service.internal_id:
        return jsonify(status=True, message="서비스가 삭제되었습니다.")
    else:
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


# Container 이미지 생성 및 업로드
# 1차에서는 이미지 정보를 입력받는 정도로만 하자.
def doc_new_image():
    sql_session = db_session
    # Docker Image 정보 입력
    id = random_string(config.SALT, 8)
    # id 중복 체크 (랜덤값 중 우연히 기존에 있는 id와 같은 값이 나올 수도 있음...)
    while len(GnDockerImages.query.filter_by(id=id).all()) != 0:
        id = random_string(config.SALT, 8)
    name = request.json["name"]
    # 이미지 Tag 중복 체크 중복되는 값이 존재할 경우 False 리턴 후 종료.
    if len(GnDockerImages.query.filter_by(name=name).all()) != 0:
        return jsonify(status=False, message="이미 존재하는 이미지입니다.")
    view_name = request.json["view_name"]
    tag = request.json["tag"]
    os = request.json["os"]
    os_ver = request.json["os_ver"]
    sub_type = "base"
    team_code = None
    author_id = None
    # team_code = request.json["team_code"]
    # author_id = request.json["author_id"]
    create_time = datetime.strptime(request.json["create_time"][:-2], '%Y-%m-%dT%H:%M:%S.%f')
    status = "Running"
    image = GnDockerImages(
        id=id, base_image=id, name=name, view_name=view_name, tag=tag, os=os, os_ver=os_ver, sub_type=sub_type, team_code=team_code,
        author_id=author_id, create_time=create_time, status=status
    )
    sql_session.add(image)
    sql_session.commit()
    return jsonify(status=True, message="이미지 추가 완료", result=image.to_json())


# todo. Container 이미지 수정
def doc_modify_image():
    return jsonify(status=False, message="미구현")


# Docker 이미지 세부정보 입력
def doc_new_image_detail(image_id):
    sql_session = db_session
    id = random_string(config.SALT, 8)
    # id 중복 체크 (랜덤값 중 우연히 기존에 있는 id와 같은 값이 나올 수도 있음...)
    while len(GnDockerImageDetail.query.filter_by(id=id).all()) != 0:
        id = random_string(config.SALT, 8)
    arg_type = request.json["arg_type"]
    argument = request.json["argument"]
    description = request.json["description"]
    image_detail = GnDockerImageDetail.query.filter_by(id=id, image_id=image_id).first()
    try:
        image_detail = GnDockerImageDetail(
            id=id, image_id=image_id, arg_type=arg_type, argument=argument, description=description
        )
        sql_session.add(image_detail)
    except:
        sql_session.rollback()
    finally:
        sql_session.commit()
    return jsonify(status=True, message="이미지 세부정보 입력 완료", result=image_detail.to_json())


# Docker 이미지 세부정보 수정
def doc_update_image_detail(image_id, id):
    sql_session = db_session
    arg_type = request.json["arg_type"]
    argument = request.json["argument"]
    description = request.json["description"]
    image_detail = GnDockerImageDetail.query.filter_by(id=id, image_id=image_id).first()
    try:
        if image_detail is None:
            return jsonify(status=False, message="존재하지 않는 세부정보입니다.")
        else:
            image_detail.arg_type = arg_type
            image_detail.argument = argument
            image_detail.description = description
    except:
        sql_session.rollback()
    finally:
        sql_session.commit()
    return jsonify(status=True, message="이미지 세부정보 수정 완료", result=image_detail.to_json())


# Docker 이미지 세부정보 삭제
def doc_delete_image_detail(image_id, id):
    sql_session = db_session
    image_detail = GnDockerImageDetail.query.filter_by(id=id, image_id=image_id).first()
    try:
        if image_detail is None:
            return jsonify(status=False, message="존재하지 않는 이미지 세부정보입니다.")
        else:
            sql_session.delete(image_detail)
    except:
        sql_session.rollback()
    finally:
        sql_session.commit()
    return jsonify(status=True, message="이미지 세부정보 입력 완료", result=image_detail.to_json())


# Container 이미지 삭제
def doc_delete_image(id):
    sql_session = db_session
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    login_check = ds.docker_login()
    login_count = 0
    while not login_check:
        if login_count > 5:
            docker_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
            docker_info.status = 'Error'
            sql_session.commit()
            return jsonify(status=False, message="login failure")
        time.sleep(10)
        login_check = ds.docker_login()
        login_count += 1

    version = "v1"
    repositories = "repositories"
    namespace = "library"
    # 레지스트리 노드 정보 가지고 오기
    registry = GnHostMachines.query.filter_by(type="docker_r").one()
    # 삭제할 이미지 정보 저장
    image = GnDockerImages.query.filter_by(id=id).first()
    if image is None:
        ds.logout()
        return jsonify(status=False, message="존재하지 않는 이미지입니다.")
    image_name = image.name.split("/")[1].split(":")[0]
    # Docker Registry 이미지 삭제
    result = ds.send(
        address=registry.ip,
        port="5000",
        method="DELETE",
        uri="/" + version + "/" + repositories + "/" + namespace + "/" + image_name
    )
    ds.logout()
    # 삭제된 상태를 이미지 및 이미지 상세 테이블에 적용
    if result:
        try:
            image.status = "Removed"
            image_detail = GnDockerImageDetail.query.filter_by(id=id).delete()
        except:
            sql_session.rollback()
        finally:
            sql_session.commit()
        return jsonify(status=True, message="이미지 삭제 완료")
    else:
        return jsonify(status=False, message="이미지 삭제 실패")


# Container 이미지 리스트
def doc_image_list():
    imagelist = GnDockerImages.query.all()
    result = []
    for image in imagelist:
        result.append(image.to_json())
    return jsonify(status=True, message="컨테이너 이미지 리스트 호출 완료.", result=result)

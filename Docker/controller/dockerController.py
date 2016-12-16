# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import jsonify, request
from datetime import datetime
from service.dockerService import DockerService
from db.database import db_session
from db.models import GnContainers
from util.config import config
from util.hash import random_string


# service 생성 및 실행
# 실행은 따로 구현하지 않아도 될 듯.. 하나?
def doc_create():
    name = request.form["name"]
    tag = request.form["tag"]
    cpu = request.form["cpu"]
    memory = request.form["memory"]
    connect_port = request.form["connect_port"]
    in_port = request.form["in_port"]
    image = request.form["image"]
    environmant = request.form["environmant"]
    # Docker Container를 생성한다.
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    docker_service = ds.docker_service_create(
        cpu=cpu,
        memory=memory,
        connect_port=connect_port,
        in_port=in_port,
        image=image,
        environmant=environmant
    )
    if type(docker_service) is not list:
        return jsonify(status=False, message=docker_service)
    else:
        # Docker Container 정보를 DB에 저장한다.
        container = GnContainers(
            id=random_string(config.SALT, 8),
            name=name,
            tag=tag,
            internal_id=docker_service[0]['ID'],
            internal_name=docker_service[0]['Spec']['Name'],
            host_id="1",
            cpu=cpu,
            memory=docker_service[0]['Spec']['TaskTemplate']['Resources']['Reservations']['MemoryBytes']/1024,
            disk=0,
            team_code=None,
            author_id=u"전제현",
            create_time=datetime.strptime(docker_service[0]['CreatedAt'][:-2], '%Y-%m-%dT%H:%M:%S.%f'),
            status="running")
        db_session.add(container)
        db_session.commit()
        return jsonify(status=True, message="서비스를 생성하였습니다.", result=container.to_json())


# todo. Container 상태변경
def doc_state(id):
    # todo doc_state 1. Docker Container의 상태를 수정한다.
    # todo doc_state 2. Docker Container 정보를 DB에 업데이트한다.
    return jsonify(status=False, message="미구현")


# Container 삭제
def doc_delete(id):
    # todo doc_delete 1. 지정된 Docker Container를 삭제한다.
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    result = ds.docker_service_rm(id)
    # todo doc_delete 2. DB에 삭제된 내용을 업데이트한다.
    container = GnContainers.query.filter_by(internal_id=id).first()
    if container is not None:
        container.status = "deleted"
        db_session.commit()
    if result == id:
        return jsonify(status=True, message="서비스가 삭제되었습니다.")
    else:
        return jsonify(status=False, message=result)


# todo. Container 정보
def doc_vm():
    return jsonify(status=False, message="미구현")


# todo. Container 리스트
def doc_vm_list():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 생성 및 업로드
def doc_new_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 수정
def doc_modify_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 삭제
def doc_delete_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 리스트
def doc_image_list():
    return jsonify(status=False, message="미구현")

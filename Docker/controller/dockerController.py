# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import jsonify, request
from service.dockerService import DockerService
from db.database import db_session
from db.models import DateTime, GnContainers
from util.config import config


# todo. service 생성 및 실행
def doc_create():
    name = request.form["name"]
    cpu = request.form["cpu"]
    memory = request.form["memory"]
    connect_port = request.form["connect_port"]
    in_port = request.form["in_port"]
    image = request.form["image"]
    environmant = request.form["environmant"]
    # todo doc_create 1. Docker Container를 생성한다.
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    docker_service = ds.docker_service_create(
        name=name,
        cpu=cpu,
        memory=memory,
        connect_port=connect_port,
        in_port=in_port,
        image=image,
        environmant=environmant
    )
    # todo doc_create 2. Docker Container 정보를 DB에 저장한다.
    container = GnContainers(
        id="",
        name="",
        tag="",
        internal_id=docker_service[0]['ID'],
        internal_name=docker_service[0]['Spec']['Name'],
        host_id="1",
        cpu=cpu,
        memory=docker_service[0]['Spec']['TaskTemplate']['Resources']['Reservations']['MemoryBytes']/1024,
        disk=None,
        team_code=None,
        author_id="전제현",
        create_time=DateTime.strptime(docker_service[0]['CreateAt'], "%Y-%M-%D %H:%M:%S"),
        start_time="",
        stop_time="",
        status="")
    db_session.add(container)
    db_session.commit()
    return jsonify(status=True, message="미구현", result=docker_service)


# todo. Container 상태변경
def doc_state(id):
    # todo doc_state 1. Docker Container의 상태를 수정한다.
    # todo doc_state 2. Docker Container 정보를 DB에 업데이트한다.
    return jsonify(status=False, message="미구현")


# todo. Container 삭제
def doc_delete(id):
    # todo doc_delete 1. 지정된 Docker Container를 삭제한다.
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    docker_name = ds.docker_service_rm(id)
    return jsonify(status=True, message="미구현", result=docker_name)


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

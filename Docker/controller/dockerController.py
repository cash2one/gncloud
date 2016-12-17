# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import jsonify, request
from datetime import datetime
from service.dockerService import DockerService
from db.database import db_session
from db.models import GnContainers, GnDockerImage, GnDockerImageDetail
from util.config import config
from util.hash import random_string


# service 생성 및 실행
# 실행은 따로 구현하지 않아도 될 듯.. 하나?
def doc_create():
    id = random_string(config.SALT, 8)
    # id 중복 체크 (랜덤값 중 우연히 기존에 있는 id와 같은 값이 나올 수도 있음...)
    while len(GnContainers.query.filter_by(id=id).all()) != 0:
        id = random_string(config.SALT, 8)
    name = request.form["name"]
    tag = request.form["tag"]
    cpu = request.form["cpu"]
    memory = request.form["memory"]
    image = request.form["image"]
    # Docker Container를 생성한다.
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    docker_service = ds.docker_service_create(image=image, cpu=cpu, memory=memory)
    if type(docker_service) is not list:
        return jsonify(status=False, message=docker_service)
    else:
        # Docker Container 정보를 DB에 저장한다.
        container = GnContainers(
            id=id,
            name=name,
            tag=tag,
            internal_id=docker_service[0]['ID'],
            internal_name=docker_service[0]['Spec']['Name'],
            host_id="1",
            cpu=cpu,
            memory=docker_service[0]['Spec']['TaskTemplate']['Resources']['Reservations']['MemoryBytes']/1024,
            disk=0,
            team_code=None,
            author_id="jhjeon",
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
    # 지정된 Docker Container를 삭제한다.
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    result = ds.docker_service_rm(id)
    # DB에 삭제된 내용을 업데이트한다.
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


# Container 이미지 생성 및 업로드
# 1차에서는 이미지 정보를 입력받는 정도로만 하자.
def doc_new_image():
    # Docker Image 정보 입력
    id = random_string(config.SALT, 8)
    # id 중복 체크 (랜덤값 중 우연히 기존에 있는 id와 같은 값이 나올 수도 있음...)
    while len(GnDockerImage.query.filter_by(id=id).all()) != 0:
        id = random_string(config.SALT, 8)
    name = request.form["name"]
    # 이미지 Tag 중복 체크 중복되는 값이 존재할 경우 False 리턴 후 종료.
    if len(GnDockerImage.query.filter_by(name=name).all()) != 0:
        return jsonify(status=False, message="이미 존재하는 이미지입니다.")
    filename = ""
    team_code = request.form["team_code"]
    author_id = request.form["author_id"]
    create_time = datetime.strptime(request.form["create_time"][:-2], '%Y-%m-%dT%H:%M:%S.%f')
    status = ""
    image = GnDockerImage(id=id, name=name, filename=filename, team_code=team_code, author_id=author_id, create_time=create_time, status=status)
    db_session.add(image)
    db_session.commit()
    return jsonify(status=True, message="이미지 추가 완료", result=image.to_json())


# Container 이미지 세부정보 입력
def doc_new_image_detail():
    id = request.form["id"]
    arg_type = request.form["arg_type"]
    argument = request.form["argument"]
    description = request.form["description"]
    image_detail = GnDockerImageDetail(id=id, arg_type=arg_type, argument=argument, description=description)
    db_session.add(image_detail)
    db_session.commit()
    return jsonify(status=True, message="이미지 세부정보 입력 완료", result=image_detail.to_json())


# todo. Container 이미지 수정
def doc_modify_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 삭제
def doc_delete_image():
    return jsonify(status=False, message="미구현")


# todo. Container 이미지 리스트
def doc_image_list():
    return jsonify(status=False, message="미구현")

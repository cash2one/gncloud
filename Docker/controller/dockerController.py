# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import jsonify, request
from datetime import datetime
from service.dockerService import DockerService
from db.database import db_session
from db.models import GnDockerServices, GnDockerContainers, GnDockerVolumes, GnDockerImage, GnDockerImageDetail, GnHostDocker
from util.config import config
from util.hash import random_string


# service 생성 및 실행
# 실행은 따로 구현하지 않아도 될 듯.. 하나?
def doc_create():
    id = random_string(config.SALT, 8)
    # id 중복 체크 (랜덤값 중 우연히 기존에 있는 id와 같은 값이 나올 수도 있음...)
    while len(GnDockerServices.query.filter_by(id=id).all()) != 0:
        id = random_string(config.SALT, 8)
    author_id = request.json["author_id"]
    team_code = request.json["team_code"]
    name = request.json["name"]
    tag = request.json["tag"]
    cpu = request.json["cpu"]
    memory = request.json["memory"]
    image = request.json["image"]
    # 컨테이너의 도커 서비스 초기화 ()
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    # Docker Swarm Service를 생성한다.
    docker_service = ds.docker_service_create(replicas=2, image=image, cpu=cpu, memory=memory)
    if type(docker_service) is not list:
        return jsonify(status=False, message=docker_service)
    else:
        # Service 정보를 DB에 저장한다.
        service = GnDockerServices(
            id=id,
            name=name,
            tag=tag,
            internal_id=docker_service[0]['ID'],
            internal_name=docker_service[0]['Spec']['Name'],
            cpu=cpu,
            memory=docker_service[0]['Spec']['TaskTemplate']['Resources']['Reservations']['MemoryBytes']/1024,
            volume=id,
            team_code=team_code,
            author_id=author_id,
            create_time=datetime.strptime(docker_service[0]['CreatedAt'][:-2], '%Y-%m-%dT%H:%M:%S.%f'),
            status="running")
        # 생성된 Service의 Container 정보를 DB에 저장한다.
        service_container_list = ds.get_service_containers(id)
        for service_container in service_container_list:
            node = GnHostDocker.query.filter_by(name=service_container['host_name']).first()
            container = GnDockerContainers(
                service_id=id,
                internal_id=service_container['internal_id'],
                internal_name=service_container['internal_name'],
                host_id=node.id
            )
            db_session.add(container)
        # t생성된 volume 정보를 DB에 저장한다.
        service_volume_list = ds.get_service_volumes(docker_service[0]['ID'])
        for service_volume in service_volume_list:
            volume = GnDockerVolumes(
                service_id=id,
                name=service_volume['Source'],
                path=service_volume['Target']
            )
            db_session.add(container)
        db_session.add(service)
        db_session.commit()
        return jsonify(status=True, message="서비스를 생성하였습니다.", result=service.to_json())


# todo. Container 상태변경
def doc_state(id):
    # todo doc_state 1. Docker Container의 상태를 수정한다.
    # todo doc_state 2. Docker Container 정보를 DB에 업데이트한다.
    return jsonify(status=False, message="미구현")


# Container 삭제
def doc_delete(id):
    # 지정된 Docker 서비스를 삭제한다.
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    result = ds.docker_service_rm(id)
    # DB에 삭제된 내용을 업데이트한다.
    service = GnDockerServices.query.filter_by(internal_id=id).first()
    if service is not None:
        service.status = "deleted"
        db_session.commit()
    if result == id:
        return jsonify(status=True, message="서비스가 삭제되었습니다.")
    else:
        return jsonify(status=False, message=result)


# Docker Service 정보
def doc_vm(id):
    user_id = request.json["user_id"]
    service = GnDockerServices(author_id=user_id, internal_id=id).first()
    return jsonify(status=True, message="컨테이너 정보를 가져왔습니다.", result=service)


# Docker 리스트
def doc_vm_list():
    user_id = request.json["user_id"]
    service = GnDockerServices(author_id=user_id).all()
    return jsonify(status=False, message="미구현", result=service)


# Container 이미지 생성 및 업로드
# 1차에서는 이미지 정보를 입력받는 정도로만 하자.
def doc_new_image():
    # Docker Image 정보 입력
    id = random_string(config.SALT, 8)
    # id 중복 체크 (랜덤값 중 우연히 기존에 있는 id와 같은 값이 나올 수도 있음...)
    while len(GnDockerImage.query.filter_by(id=id).all()) != 0:
        id = random_string(config.SALT, 8)
    name = request.json["name"]
    # 이미지 Tag 중복 체크 중복되는 값이 존재할 경우 False 리턴 후 종료.
    if len(GnDockerImage.query.filter_by(name=name).all()) != 0:
        return jsonify(status=False, message="이미 존재하는 이미지입니다.")
    filename = ""
    team_code = request.json["team_code"]
    author_id = request.json["author_id"]
    create_time = datetime.strptime(request.json["create_time"][:-2], '%Y-%m-%dT%H:%M:%S.%f')
    status = ""
    image = GnDockerImage(
        id=id, name=name, filename=filename, team_code=team_code,
        author_id=author_id, create_time=create_time, status=status
    )
    db_session.add(image)
    db_session.commit()
    return jsonify(status=True, message="이미지 추가 완료", result=image.to_json())


# Container 이미지 세부정보 입력
def doc_new_image_detail():
    id = request.json["id"]
    arg_type = request.json["arg_type"]
    argument = request.json["argument"]
    description = request.json["description"]
    image_detail = GnDockerImageDetail.query.filter_by(id=id, arg_type=arg_type).first()
    try:
        if image_detail is not None:
            image_detail.argument = argument
            image_detail.description = description
        else:
            image_detail = GnDockerImageDetail(
                id=id, arg_type=arg_type, argument=argument, description=description
            )
            db_session.add(image_detail)
    except:
        db_session.rollback()
    finally:
        db_session.commit()
    return jsonify(status=True, message="이미지 세부정보 입력 완료", result=image_detail.to_json())


# todo. Container 이미지 수정
def doc_modify_image():
    return jsonify(status=False, message="미구현")


# Container 이미지 삭제
def doc_delete_image(id):
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    version = "v1"
    repositories = "repositories"
    tags = "tags"
    image = GnDockerImage.query.filter_by(id=id).first()
    if image is None:
        return jsonify(status=False, message="존재하지 않는 이미지입니다.")
    image_name = image.name.split("/")[1].split(":")[0]
    image_tag = image.name.split("/")[1].split(":")[1]
    # Docker Registry 이미지 삭제
    result = ds.send(
        address="192.168.22.23",
        port="5000",
        method="DELETE",
        uri="/" + version + "/" + repositories + "/" + image_name + "/" + tags + "/" + image_tag
    )
    # 삭제된 상태를 이미지 및 이미지 상세 테이블에 적용
    if result:
        try:
            image.status = "deleted"
            image_detail = GnDockerImageDetail.query.filter_by(id=id).delete()
        except:
            db_session.rollback()
        finally:
            db_session.commit()
        return jsonify(status=True, message="이미지 삭제 완료")
    else:
        return jsonify(status=False, message="이미지 삭제 실패")


# Container 이미지 리스트
def doc_image_list():
    imagelist = GnDockerImage.query.all()
    result = []
    for image in imagelist:
        result.append(image.to_json())
    return jsonify(status=True, message="컨테이너 이미지 리스트 호출 완료.", result=result)

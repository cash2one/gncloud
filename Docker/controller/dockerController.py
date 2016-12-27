# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import jsonify, request
from datetime import datetime

from service.dockerService import DockerService
from db.database import db_session
from db.models import GnDockerServices, GnDockerContainers, GnDockerVolumes, \
    GnDockerImage, GnDockerImageDetail, GnHostDocker, GnDockerPorts
from util.config import config
from util.hash import random_string


# Docker Service 생성 및 실행
# 서비스 생성 시에는 실행은 자동이다.
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
    docker_service = ds.docker_service_create(id=id, replicas=2, image=image, cpu=cpu, memory=memory)
    # 데이터베이스에 없는 도커 이미지로 컨테이너를 생성할 경우
    if docker_service is None:
        return jsonify(status=False, message="존재하지 않는 도커 이미지입니다.")
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
            image=image,
            cpu=cpu,
            memory=docker_service[0]['Spec']['TaskTemplate']['Resources']['Limits']['MemoryBytes']/1024,
            volume=id,
            team_code=team_code,
            author_id=author_id,
            create_time=datetime.strptime(docker_service[0]['CreatedAt'][:-2], '%Y-%m-%dT%H:%M:%S.%f'),
            status="running")
        # 생성된 Service의 Container 정보를 DB에 저장한다.
        service_container_list = ds.get_service_containers(docker_service[0]['ID'])
        for service_container in service_container_list:
            node = GnHostDocker.query.filter_by(name=service_container['host_name']).first()
            container = GnDockerContainers(
                service_id=id,
                internal_id=service_container['internal_id'],
                internal_name=service_container['internal_name'],
                host_id=node.id
            )
            db_session.add(container)
        # 생성된 volume 정보를 DB에 저장한다.
        service_volume_list = ds.get_service_volumes(service.internal_id)
        for service_volume in service_volume_list:
            volume = GnDockerVolumes(
                service_id=id,
                name=service_volume['Source'],
                source_path=service_volume['Mountpoint'],
                destination_path=service_volume['Target']
            )
            db_session.add(volume)
        db_session.add(service)
        # 생성된 접속 포트 정보를 DB에 저장한다.
        ports = docker_service[0]['Endpoint']['Ports']
        for port in ports:
            set_port = GnDockerPorts(service_id=id, protocol=port['Protocol'], target_port=port['TargetPort'], published_port=port['PublishedPort'])
            db_session.add(set_port)
        db_session.commit()
        return jsonify(status=True, message="서비스를 생성하였습니다.", result=service.to_json())


# Docker Service 상태변경
def doc_state(id):
    type = request.json["type"]
    team_code = request.json["team_code"]
    author_id = request.json["author_id"]
    # count = request.json["count"] # 쓸 일 없을 듯...
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    # 서비스 DB 데이터 가져오기
    service = GnDockerServices.query.filter_by(id=id).first()
    # -- 시작 (start)
    # service
    if type == "start":
        # 이미 서비스가 돌아가는 상태인 경우는 아무 것도 안하고 끝낸다.
        if service.status == "running":
            return jsonify(status=False, message="서비스가 이미 실행중입니다.", result=service.to_json())
        else:
            # commit된 내용을 가지고 서비스 생성.
            # image = "%s:backup" % service.internal_name
            image = "%s:backup" % service.id
            restart_service = ds.docker_service_start(
                id=id, replicas=2, image=service.image, backup_image=image,
                cpu=service.cpu, memory="%sMB" % (service.memory/1024))
            # 변경된 내용을 DB에 Update
            # 서비스쪽 데이터 수정
            service.internal_id = restart_service[0]["ID"]
            service.internal_name = restart_service[0]['Spec']['Name']
            service.start_time = datetime.strptime(restart_service[0]['CreatedAt'][:-2], '%Y-%m-%dT%H:%M:%S.%f')
            service.status = "running"
            # 컨테이너 데이터 수정
            service_container_list = ds.get_service_containers(service.internal_id)
            for service_container in service_container_list:
                node = GnHostDocker.query.filter_by(name=service_container['host_name']).first()
                container = GnDockerContainers.query.filter_by(service_id=id, host_id=node.id).first()
                container.internal_id = service_container['internal_id']
                container.internal_name = service_container['internal_name']
            # 볼륨은 변경사항이 없기에 수정 X..? (이미지 세부사항 추가 시의 경우를 생각해 둘 필요성은 있음)
            # 포트 정보 수정
            ports = restart_service[0]['Endpoint']['Ports']
            for port in ports:
                getports = GnDockerPorts.query.filter_by(protocol=port['Protocol'], target_port=port['TargetPort']).all()
                for getport in getports:
                    db_session.delete(getport)
                set_port = GnDockerPorts(service_id=id, protocol=port['Protocol'], target_port=port['TargetPort'], published_port=port['PublishedPort'])
                db_session.add(set_port)
            db_session.commit()
            return jsonify(status=True, message="서비스가 시작되었습니다.", result=service.to_json())
    # -- 정지 (stop)
    elif type == "stop":
        if service.status != "running":
            return jsonify(status=False, message="서비스가 실행중이 아닙니다.", result=service.to_json())
        else:
            ds.docker_service_stop(service)
            service.stop_time = datetime.now()
            service.status = "stop"
            db_session.commit()
            return jsonify(status=True, message="서비스가 정지되었습니다.", result=service.to_json())
    # -- 재시작 (restart)
    elif type == "restart":
        if service.status == "running":
            ds.docker_service_stop(service)
            service.stop_time = datetime.now()
            service.status = "stop"
            db_session.commit()
            # commit된 내용을 가지고 서비스 생성.
            # image = "%s:backup" % service.internal_name
        image = "%s:backup" % service.id
        restart_service = ds.docker_service_start(
            id=id, replicas=2, image=service.image, backup_image=image,
            cpu=service.cpu, memory="%sMB" % (service.memory/1024))
        # 변경된 내용을 DB에 Update
        # 서비스쪽 데이터 수정
        service.internal_id = restart_service[0]["ID"]
        service.internal_name = restart_service[0]['Spec']['Name']
        service.start_time = datetime.strptime(restart_service[0]['CreatedAt'][:-2], '%Y-%m-%dT%H:%M:%S.%f')
        service.status = "running"
        # 컨테이너 데이터 수정
        service_container_list = ds.get_service_containers(service.internal_id)
        for service_container in service_container_list:
            node = GnHostDocker.query.filter_by(name=service_container['host_name']).first()
            container = GnDockerContainers.query.filter_by(service_id=id, host_id=node.id).first()
            container.internal_id = service_container['internal_id']
            container.internal_name = service_container['internal_name']
        # 볼륨은 변경사항이 없기에 수정 X..? (이미지 세부사항 추가 시의 경우를 생각해 둘 필요성은 있음)
        # 포트 정보 수정
        ports = restart_service[0]['Endpoint']['Ports']
        for port in ports:
            getports = GnDockerPorts.query.filter_by(protocol=port['Protocol'], target_port=port['TargetPort']).all()
            for getport in getports:
                db_session.delete(getport)
            set_port = GnDockerPorts(
                service_id=id, protocol=port['Protocol'], target_port=port['TargetPort'], published_port=port['PublishedPort'])
            db_session.add(set_port)
        db_session.commit()
        return jsonify(status=True, message="서비스가 재시작되었습니다.", result=service.to_json())
    # -- 재시작 (restart)
    elif type == "snap":
        # 이미지 커밋 및 레지스트리에 스냅샷 이미지 저장
        snapshot = ds.snap_containers(id)
        # todo snap 2. 저장된 스냅샷 정보를 DB에 저장
        # Docker Image 정보 입력
        image_id = random_string(config.SALT, 8)
        # id 중복 체크 (랜덤값 중 우연히 기존에 있는 id와 같은 값이 나올 수도 있음...)
        while len(GnDockerImage.query.filter_by(id=id).all()) != 0:
            image_id = random_string(config.SALT, 8)
        name = snapshot["name"]
        # 이미지 Tag 중복 체크 중복되는 값이 존재할 경우 False 리턴 후 종료.
        if len(GnDockerImage.query.filter_by(name=name).all()) != 0:
            return jsonify(status=False, message="이미 존재하는 이미지입니다.")
        sub_type = snapshot["sub_type"]
        create_time = datetime.now()
        status = ""
        image = GnDockerImage(
            id=image_id, name=name, sub_type=sub_type, team_code=team_code,
            author_id=author_id, create_time=create_time, status=status
        )
        db_session.add(image)
        db_session.commit()
        return jsonify(status=True, message="스냅샷 추가 완료", result=image.to_json())
    else:
        return jsonify(status=False, message="정의된 상태값이 아닙니다.")


# Docker 서비스 삭제
def doc_delete(id):
    # 지정된 Docker 서비스를 삭제한다.
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    service = GnDockerServices.query.filter_by(id=id).first()
    containers = GnDockerContainers.query.filter_by(service_id=id).all()
    volumes = GnDockerVolumes.query.filter_by(service_id=id).all()
    volume_delete_success = True
    # 서비스 삭제 (서비스 및 컨테이너가 삭제된다)
    result = ds.docker_service_rm(service.internal_id)
    for container in containers:
        # 각 컨테이너 노드 별로 존재하는 볼륨 삭제
        result2 = ds.docker_volume_rm(container.host_id, id)
        if result2 != id:
            volume_delete_success = False
    # DB에 삭제된 내용을 업데이트한다.
    if service is not None:
        # 서비스 상태 수정
        service.status = "deleted"
        # 컨테이너 상태 수정
        for container in containers:
            container.status = "deleted"
        # 볼륨 상태 수정
        for volume in volumes:
            volume.status = "deleted"
        db_session.commit()
    if result == str(service.internal_id) and volume_delete_success:
        return jsonify(status=True, message="서비스가 삭제되었습니다.")
    else:
        return jsonify(status=False, message=result)


# Docker Service 정보
def doc_vm(id):
    user_id = request.args.get("user_id")
    team_code = request.args.get("team_code")
    if team_code is None:
        service = db_session.query(GnDockerServices).filter(
            GnDockerServices.author_id == user_id, GnDockerServices.id == id, GnDockerServices.status != "deleted"
        ).first()
    else:
        service = db_session.query(GnDockerServices).filter(
            GnDockerServices.team_code == team_code, GnDockerServices.id == id, GnDockerServices.status != "deleted"
        ).first()
        service = GnDockerServices.query.filter_by(team_code=team_code, id=id).first()
    if service is None:
        return jsonify(status=False, message="서비스 정보를 가져올 수 없습니다.")
    else:
        return jsonify(status=True, message="서비스 정보를 가져왔습니다.", result=service.to_json())


# Docker Service 리스트
def doc_vm_list():
    user_id = request.args["user_id"]
    if "team_code" in request.args:
        team_code = request.args["team_code"]
    else:
        team_code = None
    if team_code == "" or team_code is None:
        services = db_session.query(GnDockerServices).filter(
            GnDockerServices.author_id == user_id, GnDockerServices.status != "deleted"
        ).all()
    else:
        services = db_session.query(GnDockerServices).filter(
            GnDockerServices.team_code == team_code, GnDockerServices.status != "deleted"
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
    # Docker Image 정보 입력
    id = random_string(config.SALT, 8)
    # id 중복 체크 (랜덤값 중 우연히 기존에 있는 id와 같은 값이 나올 수도 있음...)
    while len(GnDockerImage.query.filter_by(id=id).all()) != 0:
        id = random_string(config.SALT, 8)
    name = request.json["name"]
    # 이미지 Tag 중복 체크 중복되는 값이 존재할 경우 False 리턴 후 종료.
    if len(GnDockerImage.query.filter_by(name=name).all()) != 0:
        return jsonify(status=False, message="이미 존재하는 이미지입니다.")
    sub_type = "base"
    team_code = request.json["team_code"]
    author_id = request.json["author_id"]
    create_time = datetime.strptime(request.json["create_time"][:-2], '%Y-%m-%dT%H:%M:%S.%f')
    status = ""
    image = GnDockerImage(
        id=id, name=name, sub_type=sub_type, team_code=team_code,
        author_id=author_id, create_time=create_time, status=status
    )
    db_session.add(image)
    db_session.commit()
    return jsonify(status=True, message="이미지 추가 완료", result=image.to_json())


# todo. Container 이미지 수정
def doc_modify_image():
    return jsonify(status=False, message="미구현")


# Docker 이미지 세부정보 입력
def doc_new_image_detail(image_id):
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
        db_session.add(image_detail)
    except:
        db_session.rollback()
    finally:
        db_session.commit()
    return jsonify(status=True, message="이미지 세부정보 입력 완료", result=image_detail.to_json())


# Docker 이미지 세부정보 수정
def doc_update_image_detail(image_id, id):
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
        db_session.rollback()
    finally:
        db_session.commit()
    return jsonify(status=True, message="이미지 세부정보 수정 완료", result=image_detail.to_json())


# Docker 이미지 세부정보 삭제
def doc_delete_image_detail(image_id, id):
    image_detail = GnDockerImageDetail.query.filter_by(id=id, image_id=image_id).first()
    try:
        if image_detail is None:
            return jsonify(status=False, message="존재하지 않는 이미지 세부정보입니다.")
        else:
            db_session.delete(image_detail)
    except:
        db_session.rollback()
    finally:
        db_session.commit()
    return jsonify(status=True, message="이미지 세부정보 입력 완료", result=image_detail.to_json())


# Container 이미지 삭제
def doc_delete_image(id):
    ds = DockerService(config.DOCKER_MANAGE_IPADDR, config.DOCKER_MANAGER_SSH_ID, config.DOCKER_MANAGER_SSH_PASSWD)
    version = "v1"
    repositories = "repositories"
    namespace = "library"
    # 레지스트리 노드 정보 가지고 오기
    registry = GnHostDocker.query.filter_by(type="registry").first()
    # 삭제할 이미지 정보 저장
    image = GnDockerImage.query.filter_by(id=id).first()
    if image is None:
        return jsonify(status=False, message="존재하지 않는 이미지입니다.")
    image_name = image.name.split("/")[1].split(":")[0]
    # Docker Registry 이미지 삭제
    result = ds.send(
        address=registry.ip,
        port="5000",
        method="DELETE",
        uri="/" + version + "/" + repositories + "/" + namespace + "/" + image_name
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

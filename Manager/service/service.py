# -*- coding: utf-8 -*-

__author__ = 'NaDa'

import json
import os
import subprocess

import humanfriendly
import requests
from flask import render_template
from pexpect import pxssh
from sqlalchemy import func

from Manager.db.database import db_session
from Manager.db.models import *
from Manager.util.config import config
from Manager.util.hash import random_string, convertToHashValue, convertsize


def saveErrorTrace(id, action, sql_session):
    #vm 조회
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    error_hist = GnErrorHist(type=vm_info.type,action=action,team_code=vm_info.team_code,author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name)
    sql_session.add(error_hist)
    sql_session.commit()

def error_history_info(id, sql_session):
    info = sql_session.query(GnErrorHist)\
                      .filter(GnErrorHist.id == id).one()
    return info


def server_create(name, size_id, image_id, team_code, user_id, sshkeys, tag, type, password, backup ,sql_session):

    # host 선택 룰
    # host의 조회 순서를 우선으로 가용할 수 있는 자원이 있으면 해당 vm을 해당 host에서 생성한다
    host_id = None
    size_info = sql_session.query(GnVmSize).filter(GnVmSize.id == size_id).one()
    max_cpu = int(size_info.cpu)
    max_mem = int(size_info.mem)
    max_disk = int(size_info.disk)

    team_info = sql_session.query(GnTeam).filter(GnTeam.team_code == team_code).one()

    #조직의 리소스 체크
    current_info = sql_session.query(
                                      func.ifnull(func.sum(GnVmMachines.cpu),0).label("sum_cpu"),
                                      func.ifnull(func.sum(GnVmMachines.memory),0).label("sum_mem"),
                                     ) \
                              .filter(GnVmMachines.team_code == team_code) \
                              .filter(GnVmMachines.status != config.REMOVE_STATUS).filter(GnVmMachines.status != config.ERROR_STATUS).one()

    disk_info = sql_session.query(
                                    func.ifnull(func.sum(GnVmMachines.disk),0).label("sum_disk")
                                 ) \
        .filter(GnVmMachines.team_code == team_code) \
        .filter(GnVmMachines.type != 'docker') \
        .filter(GnVmMachines.status != config.REMOVE_STATUS).filter(GnVmMachines.status != config.ERROR_STATUS).one()

    if type == "kvm" or type == "hyperv":
        if (current_info.sum_cpu + max_cpu) >  team_info.cpu_quota or (current_info.sum_mem + max_mem) > team_info.mem_quota or (disk_info.sum_disk + max_disk) > team_info.disk_quota:
            return {"status":False, "value":"팀의 사용량을 초과하였습니다"}
    else:
        if (current_info.sum_cpu + max_cpu) >  team_info.cpu_quota \
                or (current_info.sum_mem + max_mem) >  team_info.mem_quota:
            return {"status":False, "value":"팀의 사용량을 초과하였습니다"}


    #호스트의 남아있는 자원체크
    host_list = sql_session.query(GnHostMachines).filter(GnHostMachines.type == type).all()
    for host_info in host_list:
        use_sum_info = db_session.query(func.ifnull(func.sum(GnVmMachines.cpu),0).label("sum_cpu"),
                                        func.ifnull(func.sum(GnVmMachines.memory),0).label("sum_mem"),
                                        func.ifnull(func.sum(GnVmMachines.disk),0).label("sum_disk")
                                        ).filter(GnVmMachines.host_id == host_info.id)\
                                         .filter(GnVmMachines.status != config.REMOVE_STATUS) \
                                         .filter(GnVmMachines.status != config.ERROR_STATUS) \
                                         .first()
        rest_cpu = host_info.cpu - use_sum_info.sum_cpu
        rest_mem = host_info.mem - use_sum_info.sum_mem
        rest_disk = host_info.disk - use_sum_info.sum_disk

        if type == "kvm" or type == "hyperv":
            if rest_cpu >= max_cpu and rest_mem >= max_mem and rest_disk >= max_disk:
                host_id = host_info.id
                max_cpu = rest_cpu
                max_mem = rest_mem
                max_disk = rest_disk

    if host_id is None and type != "docker":
        return {"status":False, "value":"HOST 머신 리소스가 부족합니다"}

    #backup imfo
    if(backup == True):
        backup = "true"
    else:
        backup= "false"
    #db 저장
    #id 생성
    while True:
        id = random_string(8)
        check_info = sql_session.query(GnId).filter(GnId.id == id).first()
        if not check_info:
            id_info = GnId(id,type)
            sql_session.add(id_info)
            sql_session.commit()
            break
    if(type == "hyperv"):
        vm_machine = GnVmMachines(id=id, name=name, cpu=size_info.cpu, memory=size_info.mem, disk=size_info.disk
                              , type=type, team_code=team_code, author_id=user_id
                              , status=config.STARTING_STATUS, tag=tag, image_id=image_id, create_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                              , host_id=host_id, hyperv_pass=password, backup_confirm=backup, size_id=size_id)
    elif(type=="kvm"):
        vm_machine = GnVmMachines(id=id, name=name, cpu=size_info.cpu, memory=size_info.mem, disk=size_info.disk
                                  , type=type, team_code=team_code, author_id=user_id
                                  , status=config.STARTING_STATUS, tag=tag, image_id=image_id, create_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                                  , host_id=host_id, ssh_key_id=sshkeys, backup_confirm=backup,size_id=size_id)
    else:
        vm_machine = GnVmMachines(id=id, name=name, cpu=size_info.cpu, memory=size_info.mem, disk=size_info.disk
                                  , type=type, team_code=team_code, author_id=user_id
                                  , status=config.STARTING_STATUS, tag=tag, image_id=image_id, create_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                                  , host_id="", backup_confirm=backup,size_id=size_id)
                                
    sql_session.add(vm_machine)

    # history 추가
    action_hist = GnInstanceActionHist(user_id=user_id,team_code=team_code,action="Create",action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(action_hist)
    sql_session.commit()
    return {"status":True, "value":id}

def server_create_snapshot(ord_id, name, user_id, team_code, type, sql_session):
    guest_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == ord_id).one()
    image_info = sql_session.query(GnVmImages).filter(GnVmImages.id == guest_info.image_id).one()


    #id 생성
    while True:
        vm_id = random_string(8)
        check_info = GnId.query.filter(GnId.id == vm_id).first()
        if not check_info:
            break

    guest_snap = GnVmImages(id=vm_id, name=name, type=type, sub_type="snap", filename="", ssh_id=image_info.ssh_id
                            , icon="", os=guest_info.os, os_ver=guest_info.os_ver, os_subver=guest_info.os_sub_ver
                            , os_bit=guest_info.os_bit, team_code=team_code, author_id=user_id, status=config.STARTING_STATUS
                            ,host_id=guest_info.host_id, create_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                            ,parent_id=guest_info.image_id)
    sql_session.add(guest_snap)
    sql_session.commit()
    return {"status":True,"ord_id":ord_id, "snap_id":vm_id}

def snapshot_delete(id, sql_session):
    snap_info = sql_session.query(GnVmImages).filter(GnVmImages.id ==id).one()
    if(snap_info.filename == ""):
        sql_session.query(GnVmImages).filter(GnVmImages.id ==id).delete()
        sql_session.commit()
        return False
    elif(snap_info.filename != None):
        snap_info.status = "Deleting"
        sql_session.commit()
        return True

def server_change_status(id, status,team_code, user_id, sql_session):
    #vm 조회
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()

    # history 데이터 생성
    vm_hist = GnInstanceActionHist(user_id=user_id,team_code=team_code,action=status,action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(vm_hist)
    if(vm_info.status == "Error"):
        sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).delete()
        sql_session.commit()
        return False
    else:
        vm_info.status = status
        sql_session.commit()
        return True

def vm_list(sql_session, team_code):
    list_query = sql_session.query(GnVmMachines) \
                            .filter(GnVmMachines.status != config.REMOVE_STATUS)

    if team_code != "000":
        list_query = list_query.filter(GnVmMachines.team_code == team_code)
    list = list_query.order_by(GnVmMachines.create_time.desc()).all()

    for vmMachine in list:
        vmMachine.create_time = vmMachine.create_time.strftime('%Y-%m-%d %H:%M:%S')
        vmMachine.disk = convertHumanFriend(vmMachine.disk)
        vmMachine.memory = convertHumanFriend(vmMachine.memory)
        vmMachine.author_id =vmMachine.gnUser.user_name

    retryCheck = False
    if not all((e.status != "Starting" and e.status != "Deleting") for e in list):
        retryCheck = True

    return {"guest_list":list,"retryCheck":retryCheck}

def vm_list_snap(sql_session, team_code):
    list = sql_session.query(GnVmMachines)\
                      .filter(GnVmMachines.status != config.REMOVE_STATUS)\
                      .filter(GnVmMachines.team_code == team_code)\
                      .filter(GnVmMachines.type != 'docker')\
                      .order_by(GnVmMachines.create_time.desc()).all()
    for vmMachine in list:
        vmMachine.create_time = vmMachine.create_time.strftime('%Y-%m-%d %H:%M:%S')
        vmMachine.disk = convertHumanFriend(vmMachine.disk)
        vmMachine.memory = convertHumanFriend(vmMachine.memory)

    retryCheck = False
    if not all((e.status != config.STARTING_STATUS and e.status != config.DELETING_STATUS) for e in list):
        retryCheck = True

    return {"guest_list":list,"retryCheck":retryCheck}

def vm_info(sql_session, id):
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    name_info = sql_session.query(GnUser).filter(GnUser.user_id == vm_info.author_id).one()
    if vm_info.type != 'docker':
        image_info = sql_session.query(GnVmImages).filter(GnVmImages.id == vm_info.image_id).one_or_none()
    else:
        image_info = sql_session.query(GnDockerImages).filter(GnDockerImages.id == vm_info.image_id).one()
    monitor_info = sql_session.query(GnMonitor).filter(GnMonitor.id == id).first()
    mem_info={}
    disk_info = {}
    if monitor_info is not None:
        total = vm_info.disk
        use = int(monitor_info.disk_usage)
        disk_per_info = int((use*100)/total)
        rest_disk = total - use;
        disk_info = {"total":convertHumanFriend(total), "use":convertHumanFriend(use), "rest_disk":convertHumanFriend(rest_disk), "disk_per_info":disk_per_info}

        mem_total = vm_info.memory
        mem_use = int(monitor_info.mem_usage)
        mem_per_info = int((mem_use*100)/mem_total)
        rest_mem = mem_total - mem_use;
        mem_info = {"mem_total":convertHumanFriend(mem_total), "mem_use":convertHumanFriend(mem_use), "rest_mem":convertHumanFriend(rest_mem), "mem_per_info":mem_per_info}
    vm_info.disk = convertHumanFriend(vm_info.disk)
    vm_info.memory = convertHumanFriend(vm_info.memory)
    info = {"vm_info":vm_info, "disk_info":disk_info,"mem_info":mem_info,"name_info":name_info,"image_info":image_info}
    return info

def vm_info_graph(sql_session, id):
    monitor_history_list = sql_session.query(GnMonitorHist).filter(GnMonitorHist.id == id).order_by(GnMonitorHist.cur_time.desc()).limit(30).all()
    x_info=[]
    cpu_per_info=[]
    memory_per_info=[]
    for list in reversed(monitor_history_list):
        x_info.append(list.cur_time.strftime('%H:%M'))
        cpu_per_info.append(int(list.cpu_usage))
        memory_per_info.append(int(list.mem_usage))
    info = {"x_info":x_info, "cpu_per_info":cpu_per_info, "memory_per_info":memory_per_info}
    return info


def login_list(user_id, password, sql_session):
    password = convertToHashValue(password)
    user_info = sql_session.query(GnUser, GnUserTeam)\
                           .outerjoin(GnUserTeam, GnUserTeam.user_id == GnUser.user_id) \
                           .filter(GnUser.user_id == user_id) \
                           .filter(GnUser.password == password)\
                           .one_or_none()
    if user_info != None:
        if(user_info.GnUserTeam != None):
            login_hist=GnLoginHist(user_id=user_info.GnUser.user_id, action='login',team_code=user_info.GnUserTeam.team_code,action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            sql_session.add(login_hist)
            sql_session.commit()
        else:
            login_hist=GnLoginHist(user_id=user_info.GnUser.user_id, action='login',action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            sql_session.add(login_hist)
            sql_session.commit()
    return user_info


def teamwon_list(user_id,team_code,team,sql_session):
    list =sql_session.query(GnUser, GnUserTeam).join(GnUserTeam, GnUserTeam.user_id == GnUser.user_id).filter(GnUserTeam.team_code == team_code)\
                    .filter(GnUserTeam.team_owner==team).order_by(GnUserTeam.team_owner.desc()).all()
    if len(list) ==0:
        list = None
    team_list = len(sql_session.query(GnUserTeam).filter(GnUserTeam.team_code == team_code).all())
    infor = {"list":list, "info":team_list}
    return infor

def teamwoninfo_list(user_id,sql_session):
    list = sql_session.query(GnUser,GnUserTeam).join(GnUserTeam, GnUserTeam.user_id == GnUser.user_id).filter(GnUserTeam.user_id == user_id).all()
    for vm in list:
        vm[1].apply_date = vm[1].apply_date.strftime('%Y-%m-%d %H:%M:%S')
        if(vm[1].approve_date != None):
            vm[1].approve_date = vm[1].approve_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            vm[1].approve_date = "-"
    return list

def teamcheck_list(teamcode):
    return db_session.query(GnUser).filter(GnUser.team_code == teamcode).all()


def tea(user_id, team_code, sql_session):
    sub_stmt = sql_session.query(GnUserTeam.user_id).filter(GnUserTeam.team_code == team_code)
    list = sql_session.query(GnUser).filter(GnUser.user_id.in_(sub_stmt)).all()
    return list


def teamcheck_list(user_id,sql_session):
    list = sql_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).all()
    return list


def sign_up(user_name, user_id, password, password_re):
    check = db_session.query(GnUser).filter(GnUser.user_id == user_id).one_or_none()
    if(password == password_re):
        if(check == None):
            password_sha = convertToHashValue(password_re)
            sign_up_info = GnUser(user_id = user_id, password = password_sha,user_name = user_name,tel="-",email="-",start_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            db_session.add(sign_up_info)
            db_session.commit()
            return 'success'
        else:
            return 'user_id'
    else:
        return 'password'

def repair(user_id, password, password_new, password_re, tel, email, sql_session):
    test = sql_session.query(GnUser).filter(GnUser.user_id == user_id).one()
    if password != "":
        password = convertToHashValue(password)
        list = sql_session.query(GnUser).filter(GnUser.user_id == user_id).filter(GnUser.password==password).one_or_none()
        if (list != None and password_re == password_new):
              list.password = convertToHashValue(password_re)
        else:
                return 1
    if tel!="":
        test.tel = tel

    if email != "":
        test.email = email
    sql_session.commit()
    return 2


def server_image_list(type, sub_type, sql_session, team_code):
    if type == "base":
        if sub_type != "":
            list = sql_session.query(GnVmImages).filter(GnVmImages.sub_type == type).filter(GnVmImages.type == sub_type).filter(GnVmImages.status != config.REMOVE_STATUS).all()
        else:
            list = sql_session.query(GnVmImages).filter(GnVmImages.sub_type == type).filter(GnVmImages.status != config.REMOVE_STATUS).all()
    else:
        if sub_type != "":
            list = sql_session.query(GnVmImages).filter(GnVmImages.sub_type == type).filter(GnVmImages.type == sub_type).filter(GnVmImages.team_code==team_code).filter(GnVmImages.status != config.REMOVE_STATUS).all()
        else:
            list = sql_session.query(GnVmImages).filter(GnVmImages.sub_type == type).filter(GnVmImages.team_code==team_code).filter(GnVmImages.status != config.REMOVE_STATUS).all()
    return list


def server_image(type, sql_session, team_code):
    if type == "base":
        list = sql_session.query(GnVmImages)\
                          .filter(GnVmImages.sub_type == type)\
                          .filter(GnVmImages.status != config.REMOVE_STATUS)\
                          .order_by(GnVmImages.create_time.desc()).all();
    else:
        list_query = sql_session.query(GnVmImages)\
                                .filter(GnVmImages.sub_type == type)\
                                .filter(GnVmImages.status != config.REMOVE_STATUS)
        if team_code != "000":
          list_query = list_query.filter(GnVmImages.team_code == team_code)
        list = list_query.order_by(GnVmImages.create_time.desc()).all()

    for vm in list:
        vm.create_time = vm.create_time.strftime('%Y-%m-%d %H:%M:%S')

    retryCheck = False
    if not all((e.status != config.STARTING_STATUS and e.status != config.DELETING_STATUS) for e in list):
        retryCheck = True

    return {"guest_list":list,"retryCheck":retryCheck}

def getQuotaOfTeam(team_code, sql_session):

    #현재 cpu, 메모리 사용량
    current_query = sql_session.query(func.sum(GnVmMachines.cpu).label("sum_cpu"),
                                      func.sum(GnVmMachines.memory).label("sum_mem")) \
                               .filter(GnVmMachines.status != config.REMOVE_STATUS)\
                               .filter(GnVmMachines.status != config.ERROR_STATUS)
    if team_code != "000":
        current_query = current_query.filter(GnVmMachines.team_code == team_code)
    current_info = current_query.one()

    #현재 disk 사용량
    current_disk_query = sql_session.query(func.sum(GnVmMachines.disk).label("sum_disk")) \
                                    .filter(GnVmMachines.status != config.REMOVE_STATUS) \
                                    .filter(GnVmMachines.type != "docker")
    if team_code != "000":
        current_disk_query = current_disk_query.filter(GnVmMachines.team_code == team_code)
    current_disk_info = current_disk_query.one()

    #쿼터 제한
    if team_code != "000":
        limit_quota = sql_session.query(GnTeam)\
                                 .filter(GnTeam.team_code == team_code).one()
    else:
        limit_quota = sql_session.query(func.sum(GnTeam.cpu_quota).label("cpu_quota"),
                                        func.sum(GnTeam.mem_quota).label("mem_quota"),
                                        func.sum(GnTeam.disk_quota).label("disk_quota")).one()

    #러닝 인스턴스
    vm_run_query = sql_session.query(func.count(GnVmMachines.id).label("count")) \
                              .filter(GnVmMachines.status == config.RUN_STATUS) \
                              .filter(GnVmMachines.type != "docker")\
                              .filter(GnVmMachines.status != config.ERROR_STATUS)
    if team_code != "000":
        vm_run_query = vm_run_query.filter(GnVmMachines.team_code == team_code)
    vm_run_count = vm_run_query.one()

    #정지 인스턴스
    vm_stop_query = sql_session.query(func.count(GnVmMachines.id).label("count")) \
                               .filter(GnVmMachines.status != config.REMOVE_STATUS) \
                               .filter(GnVmMachines.status != config.RUN_STATUS) \
                               .filter(GnVmMachines.type != "docker")\
                               .filter(GnVmMachines.status != config.ERROR_STATUS)
    if team_code != "000":
        vm_stop_query = vm_stop_query.filter(GnVmMachines.team_code == team_code)
    vm_stop_count = vm_stop_query.one()

    #kvm 인스턴스 개수
    vm_kvm_query = sql_session.query(func.count(GnVmMachines.id).label("count")) \
                              .filter(GnVmMachines.status != config.REMOVE_STATUS) \
                              .filter(GnVmMachines.type == "kvm") \
                              .filter(GnVmMachines.status != config.ERROR_STATUS)
    if team_code != "000":
        vm_kvm_query = vm_kvm_query.filter(GnVmMachines.team_code == team_code)
    vm_kvm_count = vm_kvm_query.one()


    #hyperv 인스턴스 개수
    vm_hyperv_query = sql_session.query(func.count(GnVmMachines.id).label("count")) \
                                 .filter(GnVmMachines.status != config.REMOVE_STATUS) \
                                 .filter(GnVmMachines.type == "hyperv") \
                                 .filter(GnVmMachines.status != config.ERROR_STATUS)
    if team_code != "000":
        vm_hyperv_query = vm_hyperv_query.filter(GnVmMachines.team_code == team_code)
    vm_hyperv_count = vm_hyperv_query.one()


    #docker 인스턴스 개수
    vm_docker_query = sql_session.query(func.count(GnVmMachines.id).label("count")) \
                                 .filter(GnVmMachines.status != config.REMOVE_STATUS) \
                                 .filter(GnVmMachines.type == "docker") \
                                 .filter(GnVmMachines.status != config.ERROR_STATUS)
    if team_code != "000":
        vm_docker_query = vm_docker_query.filter(GnVmMachines.team_code == team_code)
    vm_docker_count = vm_docker_query.one()

    #팀정보
    team_info = sql_session.query(GnTeam)\
                           .filter(GnTeam.team_code == team_code).one()

    #팀유저
    team_user_query = sql_session.query(func.count(GnUserTeam.user_id).label("count")) \
                                 .filter(GnUserTeam.comfirm == "Y")
    if team_code != "000":
        team_user_query = team_user_query.filter(GnUserTeam.team_code == team_code)
    team_user_cnt = team_user_query.one()

    #유저별 vm리스트
    user_list_query = sql_session.query(GnVmMachines.author_id,GnUser.user_name, GnTeam.team_name,func.count().label("count")) \
                                 .outerjoin(GnUser, GnVmMachines.author_id == GnUser.user_id) \
                                 .join(GnTeam, GnVmMachines.team_code == GnTeam.team_code) \
                                 .filter(GnVmMachines.status != config.REMOVE_STATUS) \
                                 .filter(GnVmMachines.type != "docker")\
                                 .filter(GnVmMachines.status != config.ERROR_STATUS) \
                                 .group_by(GnVmMachines.author_id)\
                                 .order_by(func.count().desc())
    if team_code != "000":
        user_list_query = user_list_query.filter(GnVmMachines.team_code == team_code)
    user_list = user_list_query.all()

    #이미지별 vm리스트
    image_type_query = sql_session.query(GnVmImages.name,GnTeam.team_name, func.count().label("count")) \
                                  .join(GnVmMachines, GnVmImages.id == GnVmMachines.image_id) \
                                  .join(GnTeam, GnVmMachines.team_code == GnTeam.team_code) \
                                  .filter(GnVmMachines.status != config.REMOVE_STATUS) \
                                  .filter(GnVmMachines.status != config.ERROR_STATUS) \
                                  .group_by(GnVmImages.id) \
                                  .order_by(func.count().desc())
    if team_code != "000":
        image_type_query = image_type_query.filter(GnVmMachines.team_code == team_code)
    image_type_list = image_type_query.all()

    if current_info.sum_cpu is None:
        cpu_per_info = [0,100]
        cpu_cnt_info = [0,int(limit_quota.cpu_quota)]
    else:
        cpu_per_info = [int((current_info.sum_cpu/int(limit_quota.cpu_quota))*100), 100 - (int((current_info.sum_cpu/int(limit_quota.cpu_quota))*100))]
        cpu_cnt_info = [int(current_info.sum_cpu), int(limit_quota.cpu_quota)]

    if current_info.sum_mem is None:
        memory_per_info = [0,100]
        mem_cnt_info = [0, convertHumanFriend(int(limit_quota.mem_quota))]
    else:
        memory_per_info = [int((current_info.sum_mem/int(limit_quota.mem_quota))*100), 100 - (int((current_info.sum_mem/int(limit_quota.mem_quota))*100))]
        mem_cnt_info = [convertHumanFriend(int(current_info.sum_mem)), convertHumanFriend(int(limit_quota.mem_quota))]

    if current_disk_info.sum_disk is None:
        disk_per_info = [0,100]
        disk_cnt_info = [0, convertHumanFriend(int(limit_quota.disk_quota))]
    else:
        disk_per_info = [int((current_disk_info.sum_disk/int(limit_quota.disk_quota))*100), 100 - (int((current_disk_info.sum_disk/int(limit_quota.disk_quota))*100))]
        disk_cnt_info = [convertHumanFriend(int(current_disk_info.sum_disk)), convertHumanFriend(int(limit_quota.disk_quota))]

    count_info = [vm_run_count.count,vm_stop_count.count]
    type_info = [vm_kvm_count.count,vm_hyperv_count.count]
    docker_info = vm_docker_count.count
    vm_kvm_per = 0
    vm_hyperv_per = 0
    if vm_kvm_count.count != 0:
        vm_kvm_per = (vm_kvm_count.count*100)/(vm_kvm_count.count+vm_hyperv_count.count)
    if vm_hyperv_count.count != 0:
        vm_hyperv_per = (vm_hyperv_count.count*100)/(vm_kvm_count.count+vm_hyperv_count.count)

    quato_info = {'team_name':team_info.team_name, 'cpu_per':cpu_per_info, 'mem_per':memory_per_info, 'disk_per':disk_per_info
                 , 'cpu_cnt':cpu_cnt_info, 'mem_cnt':mem_cnt_info, 'disk_cnt':disk_cnt_info
                 , 'vm_count':count_info, 'vm_type':type_info, 'docker_info':docker_info
                 , 'team_user_count':team_user_cnt, 'user_list':user_list
                 , 'vm_kvm_per':vm_kvm_per, 'vm_hyperv_per':vm_hyperv_per
                 , "image_type_list":image_type_list};
    return quato_info

def list_user_sshkey(team_code, sql_session):
    list = sql_session.query(GnSshKeys).all()
    return list

def vm_update_info(id,type,change_value,sql_session):
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    if type == 'name':
        vm_info.name = change_value
    elif type == 'tag':
        vm_info.tag = change_value
    sql_session.commit()

def teamsignup_list(comfirm, user_id):
    if(comfirm == 'N'):
        com= db_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).all()
        com.comfirm = 'Y'
        db_session.commit()
    return 1

def team_list(user_id, sql_sesssion):
    list= sql_sesssion.query(GnUser).filter(GnUser.user_id ==user_id).one()
    return list

def container(type,team_code ,sql_sesssion):
    if type == "base":
        list = sql_sesssion.query(GnDockerImages).filter(GnDockerImages.sub_type == type).filter(GnDockerImages.status != "Removed").all()
    else:
        list = sql_sesssion.query(GnDockerImages).filter(GnDockerImages.sub_type == type).filter(GnDockerImages.team_code ==team_code).filter(GnDockerImages.status != "Removed").all()
    for vm in list:
        vm.create_time = vm.create_time.strftime('%Y-%m-%d %H:%M:%S')
    return list

def containers(sql_sesssion):
    list = sql_sesssion.query(GnDockerImages).filter(GnDockerImages.status != config.REMOVE_STATUS).order_by(GnDockerImages.create_time.desc()).all()
    for vm in list:
        vm.create_time = vm.create_time.strftime('%Y-%m-%d %H:%M:%S')
    return list

def teamset(team_code, sql_session):
    list = sql_session.query(GnUser,GnUserTeam).join(GnUserTeam, GnUserTeam.user_id == GnUser.user_id).filter(GnUserTeam.team_code == team_code).all()
    for vm in list:
        vm[0].start_date = vm[0].start_date.strftime('%Y-%m-%d %H:%M:%S')
        vm[1].apply_date = vm[1].apply_date.strftime('%Y-%m-%d %H:%M:%S')
        if(vm[1].approve_date != None):
            vm[1].approve_date = vm[1].approve_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            vm[1].approve_date = "-"
    return list

def approve_set(user_id,code,type,user_name,sql_session):
    if(type == 'approve'):
        list = sql_session.query(GnUserTeam).filter(GnUserTeam.user_id==user_id).filter(GnUserTeam.team_code == code).first()
        if(list.comfirm == 'Y'):
            return False
        list.comfirm = "Y"
        list.team_owner='user'
        sql_session.commit()
        return 1
    if(type == 'change'):
        list = sql_session.query(GnUserTeam).filter(GnUserTeam.user_id== user_id).first()
        if(list.team_owner == 'owner'):
            list.team_owner = 'user'
            sql_session.commit()
            return 4
        elif(list.team_owner == 'user'):
            list.team_owner = 'owner'
            sql_session.commit()
            return 2
    if(type == 'reset'):
        list = sql_session.query(GnUser).filter(GnUser.user_id==user_id).first()
        list.password = convertToHashValue('11111111')
        sql_session.commit()
        return 3

def team_delete(id ,code):
    db_session.query(GnUserTeam).filter(GnUserTeam.user_id == id).filter(GnUserTeam.team_code == code).delete()
    db_session.commit()
    return True

def signup_team(team_code,user_id,sql_session):
    list = sql_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).one_or_none()
    if(list ==None):
        vm = GnUserTeam(user_id= user_id, team_code= team_code, comfirm = 'N',apply_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'),team_owner='user')
        db_session.add(vm)
        db_session.commit()
        return 1
    return 2

def comfirm_list(user_id, sql_session):
    team =sql_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).one()
    team.apply_date = team.apply_date.strftime('%Y-%m-%d')
    if(team.comfirm != 'Y'):
        list =sql_session.query(GnTeam).filter(GnTeam.team_code ==team.team_code).one()
        team_info = {'user_id' : user_id, 'apply_date': team.apply_date, 'team_name':list.team_name, 'team_code': team.team_code}
    return team_info


def createteam_list(user_id,team_name, team_code, author_id, sql_session):
    if(sql_session.query(GnTeam).filter(GnTeam.team_name == team_name).one_or_none() == None):
        if(sql_session.query(GnTeam).filter(GnTeam.team_code == team_code).one_or_none() == None):
            vm = GnTeam(team_code= team_code, team_name=team_name, author_id=author_id,cpu_quota=30,mem_quota=21474836480,disk_quota= 107374182400, create_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            tm = GnUserTeam(user_id=user_id, team_code=team_code, comfirm='Y', apply_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'),approve_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'), team_owner='owner')
            db_session.add(vm)
            db_session.add(tm)
            db_session.commit()
            return 'success'
        else:
            return 'team_code'
    else:
        return 'team_name'
def select(sql_session ):
    return sql_session.query(GnTeam).filter(GnTeam.author_id != 'System').all()

def select_info(team_code, sql_session): #팀 프로필 팀생성일/ 이름 개인설정 팀프로필 팀 생성일 /이름
    list =sql_session.query(GnTeam).filter(GnTeam.team_code == team_code).order_by(GnTeam.create_date.desc()).one()
    list.create_date = list.create_date.strftime('%Y-%m-%d %H:%M:%S')
    return list

def select_put(team_name, team_code): #팀 수정
    lit =db_session.query(GnTeam).filter(GnTeam.team_code== team_code).one()
    lit.team_name = team_name
    db_session.commit()
    return True

def select_putsys(team_name, team_code, team_cpu, team_memory, team_disk): #팀 시스템 수정 / cpu / memory / disk
    lit =db_session.query(GnTeam).filter(GnTeam.team_code== team_code).one()
    try:
        lit.team_name = team_name
        lit.cpu_quota = team_cpu
        lit.mem_quota = convertsize(team_memory)
        lit.disk_quota = convertsize(team_disk)
        db_session.commit()
        return True
    except:
        return False

def team_table(sql_sesseion): #시스템 팀 테이블 리스트 / 리소스 소스
    list = sql_sesseion.query(GnTeam).filter(GnTeam.author_id != 'System').order_by(GnTeam.create_date.desc()).all()
    result = []
    for team_info in list:
        team_info.create_date = team_info.create_date.strftime('%Y-%m-%d %H:%M:%S')
        user_list = sql_sesseion.query(GnUserTeam, GnUser).join(GnUser, GnUserTeam.user_id == GnUser.user_id).filter(GnUserTeam.team_code == team_info.team_code).all()
        current_info = sql_sesseion.query(func.sum(GnVmMachines.cpu).label("sum_cpu"),
                                         func.sum(GnVmMachines.memory).label("sum_mem")
                                         ).filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.status != config.REMOVE_STATUS).one()
        current_info_disk=sql_sesseion.query(func.sum(GnVmMachines.disk).label("sum_disk")
                                            ).filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.type != "docker").filter(GnVmMachines.status == config.RUN_STATUS).one()
        limit_quota = sql_sesseion.query(GnTeam).filter(GnTeam.team_code == team_info.team_code).one()
        vm_run_count = sql_sesseion.query(func.count(GnVmMachines.id).label("count")) \
            .filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.status == config.RUN_STATUS).one()
        vm_stop_count = sql_sesseion.query(func.count(GnVmMachines.id).label("count")) \
            .filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.status == config.SUSPEND_STATUS).one()
        vm_kvm_count = sql_sesseion.query(func.count(GnVmMachines.id).label("count")) \
            .filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.type == "kvm").one()
        vm_hyperv_count = sql_sesseion.query(func.count(GnVmMachines.id).label("count")) \
            .filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.type == "hyperv").one()
        vm_docker_count = sql_sesseion.query(func.count(GnVmMachines.id).label("count")) \
            .filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.type == "docker").one()
        team_info = sql_sesseion.query(GnTeam).filter(GnTeam.team_code == team_info.team_code).one()
        if current_info.sum_cpu is None:
            cpu_per_info = [0,100]
            cpu_cnt_info = [0,limit_quota.cpu_quota]
        else:
            cpu_per_info = [int((current_info.sum_cpu/limit_quota.cpu_quota)*100), 100 - (int((current_info.sum_cpu/limit_quota.cpu_quota)*100))]
            cpu_cnt_info = [int(current_info.sum_cpu), limit_quota.cpu_quota]

        if current_info.sum_mem is None:
            memory_per_info = [0,100]
            mem_cnt_info = [0, convertHumanFriend(limit_quota.mem_quota)]
        else:
            memory_per_info = [int((current_info.sum_mem/limit_quota.mem_quota)*100), 100 - (int((current_info.sum_mem/limit_quota.mem_quota)*100))]
            mem_cnt_info = [convertHumanFriend(int(current_info.sum_mem)), convertHumanFriend(limit_quota.mem_quota)]

        if current_info_disk.sum_disk is None:
            disk_per_info = [0,100]
            disk_cnt_info = [0, convertHumanFriend(limit_quota.disk_quota)]
        else:
            disk_per_info = [int((current_info_disk.sum_disk/limit_quota.disk_quota)*100), 100 - (int((current_info_disk.sum_disk/limit_quota.disk_quota)*100))]
            disk_cnt_info = [convertHumanFriend(int(current_info_disk.sum_disk)), convertHumanFriend(limit_quota.disk_quota)]
        count_info = [vm_run_count.count,vm_stop_count.count]
        type_info = [vm_kvm_count.count,vm_hyperv_count.count]
        docker_info = vm_docker_count.count
        quato_info = {'team_name':team_info.team_name, 'cpu_per':cpu_per_info, 'mem_per':memory_per_info, 'disk_per':disk_per_info
            , 'cpu_cnt':cpu_cnt_info, 'mem_cnt':mem_cnt_info, 'disk_cnt':disk_cnt_info
            , 'vm_count':count_info, 'vm_type':type_info, 'docker_info':docker_info};
        team_table = {"team_info":team_info, "user_list":user_list, "quto_info":quato_info}
        result.append(team_table);
    return result

def pathimage(sql_session): #시스템 이미지 리스트 path 쿼리
    list = sql_session.query(GnImagePool, GnVmImages).join(GnVmImages, GnImagePool.id == GnVmImages.pool_id).order_by(GnImagePool.id.desc()).all()
    for data in list:
        data[1].create_time = data[1].create_time.strftime('%Y-%m-%d %H:%M:%S')
    return list

def delteam_list(team_code, sql_session): #팀삭제 쿼리
    if((sql_session.query(GnVmMachines).filter(GnVmMachines.team_code == team_code).filter(GnVmMachines.status != config.REMOVE_STATUS).one_or_none())==None):
        user_list =sql_session.query(GnUserTeam).filter(GnUserTeam.team_code == team_code).all()
        while True:
            del_code=random_string(8)
            check = sql_session.query(GnTeamHist).filter(GnTeamHist.team_del_code == del_code).one_or_none()
            if(check == None):
                break

        for user in user_list:
            user_hist = GnUserTeamHist(user_id=user.user_id, team_code=user.team_code, comfirm=user.comfirm, apply_date=user.apply_date, approve_date=user.approve_date \
                                   , team_owner=user.team_owner, team_del_code=del_code, delete_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S') )
            sql_session.add(user_hist)
            sql_session.commit()
        team_info = sql_session.query(GnTeam).filter(GnTeam.team_code ==team_code).all()
        for team in team_info:
            team_hist = GnTeamHist(team_code=team.team_code, team_del_code= del_code, team_name=team.team_name, author_id=team.author_id, cpu_quota=team.cpu_quota \
                                   , mem_quota=team.mem_quota, disk_quota=team.disk_quota, delete_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            sql_session.add(team_hist)
            sql_session.commit()
        sql_session.query(GnUserTeam).filter(GnUserTeam.team_code == team_code).delete()
        sql_session.query(GnTeam).filter(GnTeam.team_code==team_code).delete()
        sql_session.commit()
        return 1
    else:
        return 2

def convertHumanFriend(num):
    return humanfriendly.format_size(num,binary=True).replace("i","")


def hostMachineList(sql_session):
    list = sql_session.query(GnCluster).filter(GnCluster.status != config.REMOVE_STATUS).order_by(GnCluster.create_time.desc()).all()
    for vmMachine in list:
        vmMachine.create_time = vmMachine.create_time.strftime('%Y-%m-%d %H:%M:%S')
    return list

def hostMachineInfo(id,sql_session):
    return sql_session.query(GnCluster).filter(GnCluster.id == id).one()

def deleteHostMachine(id,sql_session):
    sql_session.query(GnHostMachines).filter(GnHostMachines.id == id).delete()
    sql_session.query(GnImagePool).filter(GnImagePool.host_id == id).delete()
    sql_session.commit()

def updateClusterInfo(id,ip,sql_session):
    try:
        cluster_info = sql_session.query(GnCluster).filter(GnCluster.id == id).one()
        cluster_info.ip = ip
        cluster_list = sql_session.query(GnCluster).filter(GnCluster.status == config.RUN_STATUS)
        nginx_reload(cluster_list)
        sql_session.commit()
    except:
        sql_session.rollback()


def insertClusterInfo(type,ip,sql_session):
    try:
        while True:
            id = random_string(8)
            check_info = sql_session.query(GnCluster).filter(GnCluster.id == id).first()
            if not check_info:
                break

        cluster_info =GnCluster(id=id,type=type, ip=ip, status=config.RUN_STATUS)
        sql_session.add(cluster_info)
        sql_session.commit()
        cluster_list = sql_session.query(GnCluster).filter(GnCluster.status == config.RUN_STATUS).all()
        nginx_reload(cluster_list)
    except:
        sql_session.rollback()

def nginx_reload(cluster_list):
    #nginx reload
    kvm_str = ""
    hyper_str = ""
    docker_str = ""
    if any((e.type == "kvm") for e in cluster_list):
        kvm_info = [x for x in cluster_list if x.type == "kvm"].pop()
        kvm_str = kvm_info.ip
    if any((e.type == "hyperv") for e in cluster_list):
        hyperv_info = [x for x in cluster_list if x.type == "hyperv"].pop()
        hyper_str = hyperv_info.ip
    if any((e.type == "docker") for e in cluster_list):
        docker_info = [x for x in cluster_list if x.type == "docker"].pop()
        docker_str = docker_info.ip

    subprocess.check_output("cp "+config.NGINX_CONF_PATH+"nginx.conf "+config.NGINX_CONF_PATH+"nginx.conf_bak", shell=True)
    nginx_conf = render_template(
        "nginx.conf"
        ,kvm_endpoint = kvm_str
        ,hyperv_endpoint = hyper_str
        ,docker_endpoint = docker_str
    );
    f = open("/usr/local/nginx/conf/nginx.conf", 'w')
    f.write(nginx_conf)
    f.close()
    subprocess.check_output("/usr/local/nginx/sbin/nginx -s reload", shell=True)


def deleteCluster(id,sql_session):
    cluster_info = sql_session.query(GnCluster).filter(GnCluster.id == id).one()
    cluster_info.status = config.REMOVE_STATUS
    sql_session.commit()


def insertHostInfo(ip,cpu,mem,mem_size,disk,disk_size,type,sql_session):
    mem=mem+mem_size
    disk=disk+disk_size
    byte_mem=convertsize(mem)
    byte_disk=convertsize(disk)

    #insert host
    while True:
        id = random_string(8)
        check_info = sql_session.query(GnHostMachines).filter(GnVmImages.id == id).first();
        if not check_info:
            break

    host_info = GnHostMachines(id=id,ip=ip, cpu=cpu,mem=byte_mem,disk=byte_disk,type=type)
    sql_session.add(host_info)
    sql_session.commit()


def insertImageInfo(type,os,os_ver,os_bit,filename,icon,sql_session):
    #id 생성
    while True:
        id = random_string(8)
        check_info = sql_session.query(GnVmImages).filter(GnVmImages.id == id).first();
        if not check_info:
            id_info = GnId(id,type)
            sql_session.add(id_info)
            sql_session.commit()
            break
    image_info = GnVmImages(id=id, filename=filename, type=type, os=os, name=os, sub_type="base"
                            , icon=icon, os_ver=os_ver, os_bit=os_bit, author_id=None, status=config.RUN_STATUS)
    sql_session.add(image_info)
    sql_session.commit()


def deleteImageInfo(id,sql_session):
    sql_session.query(GnVmImages).filter(GnVmImages.id == id).delete();
    sql_session.commit()


def selectImageInfo(id,sql_session):
    return sql_session.query(GnVmImages).filter(GnVmImages.id == id).one()


def updateImageInfo(id,type,os_name,os_ver,os_bit,filename,icon,sql_session):
    image_info = sql_session.query(GnVmImages).filter(GnVmImages.id == id).one();
    image_info.type = type
    image_info.os = os_name
    image_info.os_ver = os_ver;
    image_info.os_bit = os_bit
    image_info.filename = filename
    if icon != "":
        image_info.icon = icon

    sql_session.commit()


def selectImageInfoDocker(id,sql_session):
    return sql_session.query(GnDockerImages).filter(GnDockerImages.id == id).one()


def insertImageInfoDocker(name,os_ver,tag,icon,port,env,vol,sql_session):
    try:
        #id 생성
        while True:
            image_id = random_string(8)
            check_info = sql_session.query(GnDockerImages).filter(GnDockerImages.id == image_id).first();
            if not check_info:
                break
        image_info = GnDockerImages(id=image_id, view_name=name, sub_type="base",tag=tag, icon=icon, os_ver=os_ver, status=config.RUN_STATUS)
        sql_session.add(image_info)

        #port 부분
        portArr = port.split(',')

        for str_port in portArr:
            while True:
                detail_id = random_string(8)
                check_info = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.id == detail_id).first();
                if not check_info:
                    break

            detail_info = GnDockerImageDetail(id=detail_id, image_id=image_id, arg_type="port", argument="-p "+str_port)
            sql_session.add(detail_info)

        #환경변수 부분
        envArr = env.split('\n')

        for str_env in envArr:
            while True:
                detail_id = random_string(8)
                check_info = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.id == detail_id).first();
                if not check_info:
                    break

            detail_info = GnDockerImageDetail(id=detail_id, image_id=image_id, arg_type="env", argument=str_env)
            sql_session.add(detail_info)

        #환경변수 부분
        volArr = vol.split('\n')

        for str_vol in volArr:
            while True:
                detail_id = random_string(8)
                check_info = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.id == detail_id).first();
                if not check_info:
                    break

            detail_info = GnDockerImageDetail(id=detail_id, image_id=image_id, arg_type="mount", argument=str_vol)
            sql_session.add(detail_info)

    except:
        sql_session.rollback()

    sql_session.commit()

def updateImageInfoDocker(id,name,os_ver,tag,icon,port,env,vol,sql_session): #컨테이너 이미지 관리
    try:
        image_info = sql_session.query(GnDockerImages).filter(GnDockerImages.id == id).one()
        image_info.view_name = name
        image_info.os_ver = os_ver;
        image_info.tag = tag
        if icon != "":
            image_info.icon = icon

        sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.image_id == id).delete()

        #port 부분
        portArr = port.split(',')

        for str_port in portArr:
            #id 생성
            while True:
                detail_id = random_string(8)
                check_info = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.id == detail_id).first();
                if not check_info:
                    break

            detail_info = GnDockerImageDetail(id=detail_id, image_id=image_info.id, arg_type="port", argument="-p "+str_port)
            sql_session.add(detail_info)

        #환경변수 부분
        envArr = env.split('\n')

        for str_env in envArr:
            #id 생성
            while True:
                detail_id = random_string(8)
                check_info = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.id == detail_id).first();
                if not check_info:
                    break

            detail_info = GnDockerImageDetail(id=detail_id, image_id=image_info.id, arg_type="env", argument=str_env)
            sql_session.add(detail_info)

        #환경변수 부분
        volArr = vol.split('\n')

        for str_vol in volArr:
            #id 생성
            while True:
                detail_id = random_string(8)
                check_info = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.id == detail_id).first();
                if not check_info:
                    break

            detail_info = GnDockerImageDetail(id=detail_id, image_id=image_info.id, arg_type="mount", argument=str_vol)
            sql_session.add(detail_info)

    except:
        sql_session.rollback()

    sql_session.commit()


def deleteImageInfoDocker(id,sql_session): #dockerimage 삭제용 / 시스템 > 이미지관리
    image_info = sql_session.query(GnDockerImages).filter(GnDockerImages.id == id).one();
    image_info.status = "Removed"
    sql_session.commit()


def team_table_info(team_code,sql_sesseion): #시스템 팀 테이블 리스트 / 리소스 소스
    list = sql_sesseion.query(GnTeam).filter(GnTeam.team_code==team_code).order_by(GnTeam.create_date.desc()).all()
    result = []
    for team_info in list:
        team_info.create_date = team_info.create_date.strftime('%Y-%m-%d %H:%M:%S')
        user_list = sql_sesseion.query(GnUserTeam, GnUser).join(GnUser, GnUserTeam.user_id == GnUser.user_id).filter(GnUserTeam.team_code == team_info.team_code).all()
        current_info = sql_sesseion.query(func.sum(GnVmMachines.cpu).label("sum_cpu"),
                                          func.sum(GnVmMachines.memory).label("sum_mem")
                                          ).filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.status != config.REMOVE_STATUS).one()
        current_info_disk=sql_sesseion.query(func.sum(GnVmMachines.disk).label("sum_disk")
                                             ).filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.type != "docker").filter(GnVmMachines.status == config.RUN_STATUS).one()
        limit_quota = sql_sesseion.query(GnTeam).filter(GnTeam.team_code == team_info.team_code).one()
        vm_run_count = sql_sesseion.query(func.count(GnVmMachines.id).label("count")) \
            .filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.status == config.RUN_STATUS).one()
        vm_stop_count = sql_sesseion.query(func.count(GnVmMachines.id).label("count")) \
            .filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.status == config.SUSPEND_STATUS).one()
        vm_kvm_count = sql_sesseion.query(func.count(GnVmMachines.id).label("count")) \
            .filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.type == "kvm").one()
        vm_hyperv_count = sql_sesseion.query(func.count(GnVmMachines.id).label("count")) \
            .filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.type == "hyperv").one()
        vm_docker_count = sql_sesseion.query(func.count(GnVmMachines.id).label("count")) \
            .filter(GnVmMachines.team_code == team_info.team_code).filter(GnVmMachines.type == "docker").one()
        team_info = sql_sesseion.query(GnTeam).filter(GnTeam.team_code == team_info.team_code).one()
        if current_info.sum_cpu is None:
            cpu_per_info = [0,100]
            cpu_cnt_info = [0,limit_quota.cpu_quota]
        else:
            cpu_per_info = [int((current_info.sum_cpu/limit_quota.cpu_quota)*100), 100 - (int((current_info.sum_cpu/limit_quota.cpu_quota)*100))]
            cpu_cnt_info = [int(current_info.sum_cpu), limit_quota.cpu_quota]

        if current_info.sum_mem is None:
            memory_per_info = [0,100]
            mem_cnt_info = [0, convertHumanFriend(limit_quota.mem_quota)]
        else:
            memory_per_info = [int((current_info.sum_mem/limit_quota.mem_quota)*100), 100 - (int((current_info.sum_mem/limit_quota.mem_quota)*100))]
            mem_cnt_info = [convertHumanFriend(int(current_info.sum_mem)), convertHumanFriend(limit_quota.mem_quota)]

        if current_info_disk.sum_disk is None:
            disk_per_info = [0,100]
            disk_cnt_info = [0, convertHumanFriend(limit_quota.disk_quota)]
        else:
            disk_per_info = [int((current_info_disk.sum_disk/limit_quota.disk_quota)*100), 100 - (int((current_info_disk.sum_disk/limit_quota.disk_quota)*100))]
            disk_cnt_info = [convertHumanFriend(int(current_info_disk.sum_disk)), convertHumanFriend(limit_quota.disk_quota)]
        count_info = [vm_run_count.count,vm_stop_count.count]
        type_info = [vm_kvm_count.count,vm_hyperv_count.count]
        docker_info = vm_docker_count.count
        quato_info = {'team_name':team_info.team_name, 'cpu_per':cpu_per_info, 'mem_per':memory_per_info, 'disk_per':disk_per_info
            , 'cpu_cnt':cpu_cnt_info, 'mem_cnt':mem_cnt_info, 'disk_cnt':disk_cnt_info
            , 'vm_count':count_info, 'vm_type':type_info, 'docker_info':docker_info};
        team_table = {"team_info":team_info, "user_list":user_list, "quto_info":quato_info}
        result.append(team_table);
    return result

def create_size(sql_session): # 인스턴스 생성 size
    list= sql_session.query(GnVmSize).all()
    for vm in list:
        vm.mem = convertHumanFriend(vm.mem)
        vm.disk = convertHumanFriend(vm.disk)
    return list

def price_list(sql_seesion):
    price_info = sql_seesion.query(GnVmSize).order_by(GnVmSize.cpu.desc()).all()
    for price in price_info:
        price.mem = convertHumanFriend(price.mem)
        price.disk = convertHumanFriend(price.disk)
    return price_info

def price_put(cpu, mem, disk,price,disk_size,mem_size,price_hour, sql_session):
    byte_cpu = cpu
    mem=mem+mem_size
    disk=disk+disk_size
    byte_mem = convertsize(mem)
    byte_disk= convertsize(disk)
    while True:
        id = random_string(8)
        check_info = sql_session.query(GnVmSize).filter(GnVmSize.id == id).first()
        if not check_info:
            break
    price_info = GnVmSize(id=id,cpu=byte_cpu, mem=byte_mem, disk=byte_disk, hour_price=price_hour, day_price=price)
    sql_session.add(price_info)
    sql_session.commit()

def price_del(id,sql_session):
    sql_session.query(GnVmSize).filter(GnVmSize.id == id).delete()
    sql_session.commit()


def snap_list_info(id, sql_session):
    snap_info = sql_session.query(GnVmImages).filter(GnVmImages.id == id).one()
    user_info = sql_session.query(GnUser).filter(GnUser.user_id == snap_info.author_id).one()
    snap_info.create_time = snap_info.create_time.strftime('%Y-%m-%d %H:%M:%S')
    parent_history = selectParentImageInfo(snap_info.parent_id,sql_session)
    info={"snap_info":snap_info, "user_info":user_info, "parent_history":snap_info.name + parent_history}
    return info

def selectParentImageInfo(parent_id,sql_session):
    parent_info = sql_session.query(GnVmImages).filter(GnVmImages.id == parent_id).one_or_none()

    if parent_info != None:
        return "," + parent_info.name +selectParentImageInfo(parent_info.parent_id,sql_session);
    else:
        return ""


def logout_info(user_id, team_code, sql_session):
    logout = GnLoginHist(user_id=user_id, team_code=team_code, action='logout', action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(logout)
    sql_session.commit()

def login_history(page, sql_session): #login history
    page_size=10
    page=int(page)-1
    list=sql_session.query(GnLoginHist).order_by(GnLoginHist.action_time.desc()).limit(page_size).offset(page*page_size).all()
    total_page= sql_session.query(func.count(GnLoginHist.id).label("count")).one()
    total = total_page.count /10
    login_info={};
    for login_hist in list:
        login_hist.action_time = login_hist.action_time.strftime('%Y-%m-%d %H:%M:%S')
    login_info={"list":list,"page":page,"total":total}
    return login_info

def use_history(page, sql_session):
    page_size=10
    page=int(page)-1
    list=sql_session.query(GnInstanceActionHist)\
                    .order_by(GnInstanceActionHist.action_time.desc())\
                    .limit(page_size).offset(page*page_size).all()
    total_page= sql_session.query(func.count(GnInstanceActionHist.id).label("count")).one()
    total = total_page.count /10
    for use_hist in list:
        use_hist.action_time = use_hist.action_time.strftime('%Y-%m-%d %H:%M:%S')
    use_info={"list":list,"page":page,"total":total}
    return use_info

def error_history(page,year,month,solve,notsolve,sql_session):
    page_size = 10
    page = int(page)-1

    list_query = sql_session.query(GnErrorHist) \
                            .filter(GnErrorHist.action_year == year) \
                            .filter(GnErrorHist.action_month == month)


    if solve == 'true' and notsolve == 'false':
        list_query = list_query.filter(GnErrorHist.solver_name != None)
    elif solve == 'false' and notsolve == 'true':
        list_query = list_query.filter(GnErrorHist.solver_name == None)
    elif solve == 'false' and notsolve == 'false':
        list_query = list_query.filter(GnErrorHist.solver_name != None).filter(GnErrorHist.solver_name == None)

    list = list_query.order_by(GnErrorHist.action_time.desc()) \
                     .limit(page_size).offset(page*page_size).all()

    total_count = sql_session.query(func.count(GnErrorHist.id).label("count")).one()
    solve_count = sql_session.query(func.count(GnErrorHist.id).label("count"))\
                             .filter(GnErrorHist.solver_name != None).one()
    not_solve_count = sql_session.query(func.count(GnErrorHist.id).label("count"))\
                                 .filter(GnErrorHist.solver_name == None).one()
    total = total_count.count /10
    for error_hist in list:
        error_hist.action_time = error_hist.action_time.strftime('%Y-%m-%d %H:%M:%S')
    error_info = {"list":list,"page":page,"total":total, "total_count":total_count.count,"solve_count":solve_count.count, "not_solve_count":not_solve_count.count}
    return error_info


def backupchnage(id, backup, sql_sseion): #백업 수정
    list = sql_sseion.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    list.backup_confirm = backup
    sql_sseion.commit()

def setting_list(sql_ssesion):
    setting_info = sql_ssesion.query(GnSystemSetting).one()
    if(setting_info.backup_schedule_type == 'D'):
        return {"billing":setting_info.billing_type,"list":setting_info.monitor_period, "backup_type":setting_info.backup_schedule_type
                ,"backup_week":setting_info.backup_schedule_period,"backup_days":setting_info.backup_day}
    else:
        week_info = list(str(setting_info.backup_schedule_period))
        return {"billing":setting_info.billing_type,"list":setting_info.monitor_period, "backup_type":setting_info.backup_schedule_type
            ,"backup_week":week_info,"backup_days":setting_info.backup_day}

def monitoring_time_change(monitor_period, sql_session):
    list = sql_session.query(GnSystemSetting).one()
    list.monitor_period = monitor_period
    sql_session.commit()

def billing_time_change(bills, sql_session):
    list=sql_session.query(GnSystemSetting).one()
    list.billing_type = bills
    sql_session.commit()

def backup_time_change(type, day,backday ,sql_session):
    list=sql_session.query(GnSystemSetting).one()
    list.backup_schedule_type = type
    list.backup_schedule_period = day
    list.backup_day =backday
    sql_session.commit()

def insertVmHist(id,action,user_id,team_code,sql_session):
    vm_hist = GnInstanceActionHist(user_id=user_id,team_code=team_code,action=action,action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(vm_hist)
    sql_session.commit()

#-------------공지사항 관련 start ------------------------------------#

def notice_list(page,sql_session):
    page_size=10
    page=int(page)-1
    list = sql_session.query(GnNotice).order_by(GnNotice.write_date.desc()).limit(page_size).offset(page*page_size).all()
    total_page= sql_session.query(func.count(GnNotice.id).label("count")).one()
    total=int(total_page.count)/10
    for vm in list:
        vm.write_date = vm.write_date.strftime('%Y-%m-%d %H:%M')
    return {"list":list, "total_page":total_page.count,"total":total, "page":page}

def notice_info(id,sql_session):
    list = sql_session.query(GnNotice).filter(GnNotice.id ==id).one()
    list.write_date = list.write_date.strftime('%Y-%m-%d %H:%M')
    return list

def notice_create(title, text, sql_session):
    notice_info = GnNotice(title=title, text=text,write_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(notice_info)
    sql_session.commit()

def notice_change(id ,text, sql_session):
    notice_info=sql_session.query(GnNotice).filter(GnNotice.id == id).one()
    notice_info.text = text
    sql_session.commit()

def notice_delete(id, sql_session):
    sql_session.query(GnNotice).filter(GnNotice.id == id).delete()
    sql_session.commit()

#-------------공지사항 관련 END ------------------------------------#

#-------------QNA START-------------------------------------#

def qna_list(page,team_code,syscheck,sql_session):
    if syscheck =='sysowner':
        page_size=10
        page=int(page)-1
        qna_info = sql_session.query(GnQnA).filter(GnQnA.farent_id == None)\
            .order_by(GnQnA.create_date.desc()).limit(page_size).offset(page*page_size).all()
        total_page = total_page= sql_session.query(func.count(GnQnA.id).label("count")) \
                                            .filter(GnQnA.farent_id==None).one()
        total=int(total_page.count)/10
        for qna in qna_info:
            qna.create_date = qna.create_date.strftime('%Y-%m-%d %H:%M')
    else:
        page_size=10
        page=int(page)-1
        qna_info = sql_session.query(GnQnA).filter(GnQnA.farent_id == None) \
            .order_by(GnQnA.create_date.desc()).filter(GnQnA.team_code==team_code).limit(page_size).offset(page*page_size).all()
        total_page = total_page= sql_session.query(func.count(GnQnA.id).label("count")) \
            .filter(GnQnA.farent_id==None).filter(GnQnA.team_code==team_code).one()
        total=int(total_page.count)/10
        for qna in qna_info:
            qna.create_date = qna.create_date.strftime('%Y-%m-%d %H:%M')
    return {"list":qna_info, "total_page":total_page.count,"total":total, "page":page}
def qna_info_list(id,sql_session):
    qna_info = sql_session.query(GnQnA).filter(GnQnA.id ==id).one()
    qna_ask = sql_session.query(GnQnA).filter(GnQnA.farent_id ==id).all()
    for qna in qna_ask:
       qna.author_id = qna.gnUser.user_name
    qna_info.create_date = qna_info.create_date.strftime('%Y-%m-%d %H:%M')
    return {"qna_info":qna_info, "qna_ask":qna_ask}

def qna_ask(title,text,user_id,team_code,sql_session):
    qna_ask_inf = GnQnA(title=title, text=text,author_id=user_id, team_code=team_code,create_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(qna_ask_inf)
    sql_session.commit()

def qna_ask_reply(id, text, user_id,team_code ,sql_session):
    qna_ask_replys=GnQnA(farent_id=id ,text=text,author_id=user_id,team_code=team_code,create_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(qna_ask_replys)
    sql_session.commit()

def qna_ask_reply_change(id,user_id ,text, sql_session):
    qna_ask_replys= sql_session.query(GnQnA).filter(GnQnA.id==id).one()
    qna_ask_replys.text = text
    sql_session.commit()

def qna_ask_change(id, user_id , text, sql_session):
    qna_ask_info = sql_session.query(GnQnA).filter(GnQnA.id == id).filter(GnQnA.farent_id == None).one()
    qna_ask_info.text =text
    sql_session.commit()

def qna_ask_delete(id, sql_session):
    sql_session.query(GnQnA).filter(GnQnA.id==id).delete()
    sql_session.query(GnQnA).filter(GnQnA.farent_id==id).delete()
    sql_session.commit()

def qna_ask_reply_delete(id , sql_session):
    sql_session.query(GnQnA).filter(GnQnA.id==id).delete()
    sql_session.commit()

#-------------QNA END-------------------------------------#

#_______________클러스터 없을시 인스턴스생성부분 __________________________________________#
def cluster_info(sql_session):
    hyperv = sql_session.query(GnCluster).filter(GnCluster.type =='hyperv').filter(GnCluster.status != 'Removed').one_or_none()
    kvm = sql_session.query(GnCluster).filter(GnCluster.type =='kvm').filter(GnCluster.status != 'Removed').one_or_none()
    docker = sql_session.query(GnCluster).filter(GnCluster.type =='docker').filter(GnCluster.status != 'Removed').one_or_none()
    return {"hyper":hyperv,"kvm":kvm,"docker":docker}

def healthcheck_info(team_code,sql_session):
    cluster_list = sql_session.query(GnCluster).filter(GnCluster.status != 'Removed').all()
    result_list = []
    for e in cluster_list:
        host_list = []
        try:
            URL = 'http://'+e.ip+"/service/isAlive"
            response = requests.get(URL)
            response_cluster = response.status_code
        except:
            response_cluster = 0

        for host in e.gnHostMachines:
            if e.gnHostMachines:
                if e.type == 'kvm' or e.type == 'docker':
                    try:
                        s = pxssh.pxssh(timeout=1)
                        s.login(host.ip, "root")
                        response_host = 0
                    except:
                        response_host = 1
                else:
                    response_host = response_host = os.system("ping -c 1 -p "+ str(host.host_agent_port) +" "+ host.ip)

                host_list.append({"host_check":response_host,"host_ip":host.ip})

        result_list.append({"cluster_info":e,"status":response_cluster,"host_list":host_list})

    return result_list



#_________________________과금______________________________________________________________#

def team_price_lsit(team_code,sql_session):
    list = sql_session.query(GnInvoiceResult).all()

    return list

def team_price_lsit_info(year,month,team_code,sql_session):
    list = sql_session.query(GnInvoiceResult).filter(GnInvoiceResult.year==year).filter(GnInvoiceResult.month == month)\
                                            .filter(GnInvoiceResult.team_code==team_code).one()
    team_name = sql_session.query(GnTeam).filter(GnTeam.team_code == team_code).one()
    instance=json.loads(list.invoice_data)
    team = sql_session.query(GnTeam).filter(GnTeam.team_code == list.team_code).one()
    return {"list":list, "instance":instance, "team_code":team_name}


#_________________________백업______________________________________________________________#
def backup_list(page,sql_session):
    page_size = 30
    page = int(page)-1
    total_page= sql_session.query(func.count(GnBackup.vm_id).label("count")).one()
    list=sql_session.query(GnBackup).order_by(GnBackup.backup_time.desc()).limit(page_size).offset(page*page_size).all()
    total=int(total_page.count)/30
    for vm in list:
        vm.backup_time = vm.backup_time.strftime('%Y-%m-%d %H:%M')
    return {"list":list, "total_page":total_page.count,"total":total, "page":page}

def backup_hist(vm_id, sql_session):
    vm_info = sql_session.query(GnBackup).filter(GnBackup.vm_id == vm_id).one()
    hist_info = sql_session.query(GnBackupHist).filter(GnBackupHist.vm_id == vm_id).order_by(GnBackupHist.backup_time.desc()).all()
    total = len(hist_info)
    for hist in hist_info:
        hist.backup_time = hist.backup_time.strftime('%Y-%m-%d %H:%M')
    return {"vm_info":vm_info,"hist_info":hist_info,"total":total}

def team_backup_list(page,team_code,sql_session):
    page_size = 30
    page = int(page)-1
    total_page= sql_session.query(func.count(GnBackup.vm_id).label("count")).filter(GnBackup.team_code == team_code).one()
    list=sql_session.query(GnBackup).filter(GnBackup.team_code == team_code).order_by(GnBackup.backup_time.desc()).limit(page_size).offset(page*page_size).all()
    total=int(total_page.count)/30
    for vm in list:
        vm.backup_time = vm.backup_time.strftime('%Y-%m-%d %H:%M')
    return {"list":list, "total_page":total_page.count,"total":total, "page":page}
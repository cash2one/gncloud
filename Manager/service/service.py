# -*- coding: utf-8 -*-

__author__ = 'NaDa'

import json
import os
import subprocess

import humanfriendly
import requests
from flask import render_template
from pexpect import pxssh
from sqlalchemy import func,or_

from Manager.db.database import db_session
from Manager.db.models import *
from Manager.util.config import config
from Manager.util.hash import random_string, convertToHashValue, convertsize



def server_create(name, size_id, image_id, team_code, user_id, sshkeys, tag, type, password, backup ,sql_session):

    # host 선택 룰
    # host의 조회 순서를 우선으로 가용할 수 있는 자원이 있으면 해당 vm을 해당 host에서 생성한다
    host_id = None
    size_info = sql_session.query(GnVmSize).filter(GnVmSize.id == size_id).one()
    if type != 'docker':
        image_info = sql_session.query(GnVmImages).filter(GnVmImages.id == image_id).one()
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
            return {"status":False, "value":"팀의 사용량을 초과하였습니다."}
    else:
        if (current_info.sum_cpu + max_cpu) >  team_info.cpu_quota \
                or (current_info.sum_mem + max_mem) >  team_info.mem_quota:
            return {"status":False, "value":"팀의 사용량을 초과하였습니다."}


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
                              , host_id=host_id, hyperv_pass=password, backup_confirm=backup, size_id=size_id, os=image_info.os)
    elif(type=="kvm"):
        vm_machine = GnVmMachines(id=id, name=name, cpu=size_info.cpu, memory=size_info.mem, disk=size_info.disk
                                  , type=type, team_code=team_code, author_id=user_id
                                  , status=config.STARTING_STATUS, tag=tag, image_id=image_id, create_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                                  , host_id=host_id, ssh_key_id=sshkeys, backup_confirm=backup,size_id=size_id, os=image_info.os)
    else:
        vm_machine = GnVmMachines(id=id, name=name, cpu=size_info.cpu, memory=size_info.mem, disk=size_info.disk
                                  , type=type, team_code=team_code, author_id=user_id
                                  , status=config.STARTING_STATUS, tag=tag, image_id=image_id, create_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                                  , host_id="", backup_confirm=backup,size_id=size_id, os='docker')
                                
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
                            .filter(GnVmMachines.type != "docker") \
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

def sv_list(sql_session, team_code):
    list_query = sql_session.query(GnVmMachines) \
                            .filter(GnVmMachines.type == "docker") \
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

def vm_list_snap(sql_session,owner,author_id ,team_code):
    list = sql_session.query(GnVmMachines)\
                      .filter(GnVmMachines.status != config.REMOVE_STATUS)\
                      .filter(GnVmMachines.team_code == team_code)\
                      .filter(GnVmMachines.type != 'docker')

    if owner != 'owner':
        list = list.filter(GnVmMachines.author_id == author_id)
    list_q=list.order_by(GnVmMachines.create_time.desc()).all()
    if len(list_q) !=0:
        for vmMachine in list_q:
            vmMachine.create_time = vmMachine.create_time.strftime('%Y-%m-%d %H:%M:%S')
            vmMachine.disk = convertHumanFriend(vmMachine.disk)
            vmMachine.memory = convertHumanFriend(vmMachine.memory)
    else:
        list_q=""

    return {"guest_list":list_q}

def vm_info(sql_session, id):
    vol_info={}
    host_contents=''
    container_name=''
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    name_info = sql_session.query(GnUser).filter(GnUser.user_id == vm_info.author_id).one()
    if vm_info.type != 'docker':
        image_info = sql_session.query(GnVmImages).filter(GnVmImages.id == vm_info.image_id).one_or_none()
        host_machine = sql_session.query(GnHostMachines).filter(GnHostMachines.id == vm_info.host_id).first()
        host_contents = '%s | %s\r\n' % (host_machine.name, host_machine.ip)
    else:
        image_info = sql_session.query(GnDockerImages).filter(GnDockerImages.id == vm_info.image_id).one()

        host_contents = ''
        container_count=0
        container_info = sql_session.query(GnDockerContainers).filter(GnDockerContainers.service_id == id).all()
        for container in container_info:
            if container_count> 0:
                container_name = '%s,' % container_name
            host_machine = sql_session.query(GnHostMachines).filter(GnHostMachines.id == container.host_id).first()
            host_contents = '%s%s | %s\r\n' % (host_contents, host_machine.name, host_machine.ip)
            container_name = '%s%s' % (container_name, container.internal_name)

        data_vol=''
        log_vol=''
        volume_info = sql_session.query(GnDockerVolumes).filter(GnDockerVolumes.service_id == id).all()
        for volume in volume_info:
            if volume.name.find('DATA') >= 0:
                data_vol='%s:%s' % (volume.source_path, volume.destination_path)
            elif volume.name.find('LOG') >= 0:
                log_vol='%s:%s' % (volume.source_path, volume.destination_path)
        vol_info={"data_vol":data_vol, "log_vol":log_vol}
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
    container_name = '%s | %s' % (vm_info.os, container_name)
    info = {"vm_info":vm_info, "disk_info":disk_info,"mem_info":mem_info,"name_info":name_info,"image_info":image_info,
            "ssh_key":vm_info.gnSshkeys, "vol_info":vol_info, "host_info":host_contents, "container_name":container_name}
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



def container(type,team_code ,sql_sesssion):
    list = sql_sesssion.query(GnDockerImages).filter(GnDockerImages.sub_type == type).filter(or_(GnDockerImages.team_code ==team_code, GnDockerImages.team_code == 000)).filter(GnDockerImages.status != "Removed").all()
    for vm in list:
        vm.create_time = vm.create_time.strftime('%Y-%m-%d %H:%M:%S')
    return list

def containers(sql_sesssion):
    list = sql_sesssion.query(GnDockerImages).filter(GnDockerImages.status != config.REMOVE_STATUS).order_by(GnDockerImages.create_time.desc()).all()
    for vm in list:
        vm.create_time = vm.create_time.strftime('%Y-%m-%d %H:%M:%S')
    return list




def convertHumanFriend(num):
    return humanfriendly.format_size(num,binary=True).replace("i","")


def create_size(sql_session): # 인스턴스 생성 size
    list= sql_session.query(GnVmSize).order_by(GnVmSize.cpu.asc(),GnVmSize.mem.asc(),GnVmSize.disk.asc()).all()
    for vm in list:
        vm.mem = convertHumanFriend(vm.mem)
        vm.disk = convertHumanFriend(vm.disk)
    return list

#==========================snap

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

#=============================================================================================================

#_______________클러스터 없을시 인스턴스생성부분 __________________________________________#
def cluster_info(sql_session):
    hyperv = sql_session.query(GnCluster).filter(GnCluster.type =='hyperv').filter(GnCluster.status != 'Removed').one_or_none()
    kvm = sql_session.query(GnCluster).filter(GnCluster.type =='kvm').filter(GnCluster.status != 'Removed').one_or_none()
    docker = sql_session.query(GnCluster).filter(GnCluster.type =='docker').filter(GnCluster.status != 'Removed').one_or_none()
    return {"hyper":hyperv,"kvm":kvm,"docker":docker}




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
                    host.ip = host.ip.split(':')[0]
                    response_host = os.system("ping -c 1 -p "+ config.AGENT_PORT +" "+ host.ip)

                host_list.append({"host_check":response_host,"host_ip":host.ip,"host_name":host.name})

        result_list.append({"cluster_info":e,"status":response_cluster,"host_list":host_list})

    return result_list

def getQuotaOfTeam(team_code, sql_session):

    #현재 cpu, 메모리 사용량
    current_query = sql_session.query(func.sum(GnVmMachines.cpu).label("sum_cpu"),
                                      func.sum(GnVmMachines.memory).label("sum_mem")) \
        .filter(GnVmMachines.status != config.REMOVE_STATUS) \
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
        limit_quota = sql_session.query(GnTeam) \
            .filter(GnTeam.team_code == team_code).one()
    else:
        limit_quota = sql_session.query(func.sum(GnTeam.cpu_quota).label("cpu_quota"),
                                        func.sum(GnTeam.mem_quota).label("mem_quota"),
                                        func.sum(GnTeam.disk_quota).label("disk_quota")).one()

    #러닝 인스턴스
    vm_run_query = sql_session.query(func.count(GnVmMachines.id).label("count")) \
        .filter(GnVmMachines.status == config.RUN_STATUS) \
        .filter(GnVmMachines.type != "docker") \
        .filter(GnVmMachines.status != config.ERROR_STATUS)
    if team_code != "000":
        vm_run_query = vm_run_query.filter(GnVmMachines.team_code == team_code)
    vm_run_count = vm_run_query.one()

    #정지 인스턴스
    vm_stop_query = sql_session.query(func.count(GnVmMachines.id).label("count")) \
        .filter(GnVmMachines.status != config.REMOVE_STATUS) \
        .filter(GnVmMachines.status != config.RUN_STATUS) \
        .filter(GnVmMachines.type != "docker") \
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
    team_info = sql_session.query(GnTeam) \
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
        .filter(GnVmMachines.type != "docker") \
        .filter(GnVmMachines.status != config.ERROR_STATUS) \
        .group_by(GnVmMachines.author_id, GnUser.user_name, GnTeam.team_name) \
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
        .group_by(GnVmImages.id, GnVmImages.name,GnTeam.team_name) \
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

def convertHumanFriend(num):
    return humanfriendly.format_size(num,binary=True).replace("i","")
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


def convertHumanFriend(num):
    return humanfriendly.format_size(num,binary=True).replace("i","")


def error_history_save(id,solve_content,user_id,sql_session):
    error_hist = sql_session.query(GnErrorHist).filter(GnErrorHist.id == id).one()
    error_hist.solve_content = solve_content
    error_hist.solver_id = user_id
    error_hist.solve_time = datetime.datetime.now()
    sql_session.commit()

def error_history_save_checked(id,checked,user_id,sql_session):
    if checked == 'true':
        error_hist = sql_session.query(GnErrorHist).filter(GnErrorHist.id == id).one()
        error_hist.solver_id = user_id
        error_hist.solve_time = datetime.datetime.now()
    else:
        error_hist = sql_session.query(GnErrorHist).filter(GnErrorHist.id == id).one()
        error_hist.solver_id = None
        error_hist.solve_time = None
        error_hist.solve_content = None

    sql_session.commit()

def saveErrorTrace(id, action, sql_session):
    #vm 조회
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    error_hist = GnErrorHist(type=vm_info.type,action=action,team_code=vm_info.team_code,author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name)
    sql_session.add(error_hist)
    sql_session.commit()

def error_history_info(id, sql_session):
    info = sql_session.query(GnErrorHist) \
        .filter(GnErrorHist.id == id).one()
    info.action_time = info.action_time.strftime('%Y-%m-%d %H:%M:%S')
    if info.solve_time != None:
        info.solve_time = info.solve_time.strftime('%Y-%m-%d %H:%M:%S')
    return info


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
    if len(sql_session.query(GnVmMachines).filter(GnVmMachines.team_code == team_code).all()) == 0:
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


def hostMachineList(sql_session):
    list = sql_session.query(GnCluster).filter(GnCluster.status != config.REMOVE_STATUS).order_by(GnCluster.create_time.desc()).all()
    for vmMachine in list:
        vmMachine.create_time = vmMachine.create_time.strftime('%Y-%m-%d %H:%M:%S')
    return list

def hostMachineInfo(id,sql_session):
    return sql_session.query(GnCluster).filter(GnCluster.id == id).one()

def deleteHostMachine(id,sql_session):
    if len(sql_session.query(GnVmMachines).filter(GnVmMachines.host_id == id).all()) == 0:
        sql_session.query(GnHostMachines).filter(GnHostMachines.id == id).delete()
        sql_session.query(GnImagePool).filter(GnImagePool.host_id == id).delete()
        sql_session.commit()
        return True
    else:
        return False


def insertClusterInfo(type,sql_session):
    try:
        while True:
            id = random_string(8)
            check_info = sql_session.query(GnCluster).filter(GnCluster.id == id).first()
            if not check_info:
                break

        cluster_info =GnCluster(id=id,type=type,ip= type ,status=config.RUN_STATUS)
        sql_session.add(cluster_info)
        sql_session.commit()
        cluster_list = sql_session.query(GnCluster).filter(GnCluster.status == config.RUN_STATUS).all()

    except:
        sql_session.rollback()

def deleteCluster(id,sql_session):
    cluster_info = sql_session.query(GnCluster).filter(GnCluster.id == id).one()
    host_info = sql_session.query(GnHostMachines).filter(GnHostMachines.type == cluster_info.type).all()
    for host in host_info:
        vm_list = sql_session.query(GnVmMachines).filter(GnVmMachines.host_id == host.id).all()
        if len(vm_list) != 0:
            return False

    cluster_info.status = config.REMOVE_STATUS
    sql_session.commit()
    return True

def insertHostInfo(ip,cpu,mem,mem_size,disk,disk_size,type,name,sql_session):
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

    host_info = GnHostMachines(id=id,ip=ip, cpu=cpu,mem=byte_mem,disk=byte_disk,type=type,name=name)
    sql_session.add(host_info)
    sql_session.commit()


def insertImageInfo(type,os,os_ver,os_bit,filename,icon,name,sql_session):
    #id 생성
    while True:
        id = random_string(8)
        check_info = sql_session.query(GnVmImages).filter(GnVmImages.id == id).first();
        if not check_info:
            id_info = GnId(id,type)
            sql_session.add(id_info)
            sql_session.commit()
            break
    image_info = GnVmImages(id=id, filename=filename, type=type, os=os, name=name, sub_type="base"
                            , icon=icon, os_ver=os_ver, os_bit=os_bit, author_id=None,ssh_id=os ,status=config.RUN_STATUS)
    sql_session.add(image_info)
    sql_session.commit()


def deleteImageInfo(id,sql_session):
    sql_session.query(GnVmImages).filter(GnVmImages.id == id).delete();
    sql_session.commit()


def selectImageInfo(id,sql_session):
    return sql_session.query(GnVmImages).filter(GnVmImages.id == id).one()


def updateImageInfo(id,type,os_name,os_ver,os_bit,filename,icon,name,sql_session):
    image_info = sql_session.query(GnVmImages).filter(GnVmImages.id == id).one();
    image_info.type = type
    image_info.os = os_name
    image_info.os_ver = os_ver;
    image_info.os_bit = os_bit
    image_info.filename = filename
    image_info.name = name
    if icon != "":
        image_info.icon = icon

    sql_session.commit()


def selectImageInfoDocker(id,sql_session):
    return sql_session.query(GnDockerImages).filter(GnDockerImages.id == id).one()


def insertImageInfoDocker(name,view_name,os,os_ver,tag,icon,port,env,data_vol,log_vol,team_code,sql_session):
    try:
        #id 생성
        while True:
            image_id = random_string(8)
            check_info = sql_session.query(GnDockerImages).filter(GnDockerImages.id == image_id).first();
            if not check_info:
                break
        image_info = GnDockerImages(id=image_id, name=name, view_name=view_name,team_code=team_code,os=os,sub_type="base",tag=tag, icon=icon, os_ver=os_ver, status=config.RUN_STATUS)
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

        #data_vol변수 부분
        data_volArr = data_vol.split('\n')

        for str_datavol in data_volArr:
            #id 생성
            while True:
                detail_id = random_string(8)
                check_info = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.id == detail_id).first();
                if not check_info:
                    break

            detail_info = GnDockerImageDetail(id=detail_id, image_id=image_info.id, arg_type="data_vol", argument=str_datavol)
            sql_session.add(detail_info)

        #log_vol변수 부분
        log_volArr = log_vol.split('\n')

        for str_logvol in log_volArr:
            #id 생성
            while True:
                detail_id = random_string(8)
                check_info = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.id == detail_id).first();
                if not check_info:
                    break

            detail_info = GnDockerImageDetail(id=detail_id, image_id=image_info.id, arg_type="log_vol", argument=str_logvol)
            sql_session.add(detail_info)

    except:
        sql_session.rollback()

    sql_session.commit()

def updateImageInfoDocker(id,name,view_name,os_ver,tag,icon,port,env,data_vol,log_vol,sql_session): #컨테이너 이미지 관리
    try:
        image_info = sql_session.query(GnDockerImages).filter(GnDockerImages.id == id).one()
        image_info.name = name
        image_info.view_name = view_name
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

        #data_vol변수 부분
        data_volArr = data_vol.split('\n')

        for str_datavol in data_volArr:
            #id 생성
            while True:
                detail_id = random_string(8)
                check_info = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.id == detail_id).first();
                if not check_info:
                    break

            detail_info = GnDockerImageDetail(id=detail_id, image_id=image_info.id, arg_type="data_vol", argument=str_datavol)
            sql_session.add(detail_info)

        #log_vol변수 부분
        log_volArr = log_vol.split('\n')

        for str_logvol in log_volArr:
            #id 생성
            while True:
                detail_id = random_string(8)
                check_info = sql_session.query(GnDockerImageDetail).filter(GnDockerImageDetail.id == detail_id).first();
                if not check_info:
                    break

            detail_info = GnDockerImageDetail(id=detail_id, image_id=image_info.id, arg_type="log_vol", argument=str_logvol)
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


#---------------------vm_size
def price_list(sql_seesion):
    price_info = sql_seesion.query(GnVmSize).order_by(GnVmSize.cpu.asc(),GnVmSize.mem.asc(),GnVmSize.disk.asc()).all()
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
    list=sql_session.query(GnInstanceActionHist) \
        .order_by(GnInstanceActionHist.action_time.desc()) \
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

    total_query = sql_session.query(func.count(GnErrorHist.id).label("count"))


    if solve == 'true' and notsolve == 'false':
        list_query = list_query.filter(GnErrorHist.solver_id != None)
        total_query = total_query.filter(GnErrorHist.solver_id != None)
    elif solve == 'false' and notsolve == 'true':
        list_query = list_query.filter(GnErrorHist.solver_id == None)
        total_query = total_query.filter(GnErrorHist.solver_id == None)
    elif solve == 'false' and notsolve == 'false':
        list_query = list_query.filter(GnErrorHist.solver_id != None).filter(GnErrorHist.solver_id == None)
        total_query = total_query.filter(GnErrorHist.solver_id != None).filter(GnErrorHist.solver_id == None)

    list = list_query.order_by(GnErrorHist.action_time.desc()) \
        .limit(page_size).offset(page*page_size).all()


    total_count = total_query.one()
    solve_count = sql_session.query(func.count(GnErrorHist.id).label("count")) \
        .filter(GnErrorHist.solver_id != None).one()
    not_solve_count = sql_session.query(func.count(GnErrorHist.id).label("count")) \
        .filter(GnErrorHist.solver_id == None).one()
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
    if type != "" and day != "":
        list.backup_schedule_type = type
        list.backup_schedule_period = day
    if backday != "":
        list.backup_day =backday
    sql_session.commit()

def insertVmHist(id,action,user_id,team_code,sql_session):
    vm_hist = GnInstanceActionHist(user_id=user_id,team_code=team_code,action=action,action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(vm_hist)
    sql_session.commit()

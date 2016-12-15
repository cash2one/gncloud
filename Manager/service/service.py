# -*- coding: utf-8 -*-
__author__ = 'NaDa'

from sqlalchemy import func
import datetime

from Manager.db.models import GnVmMachines, GnUser, GnTeam, GnVmImages, GnMonitor, GnMonitorHist
from Manager.db.database import db_session
from Manager.util.hash import random_string

def vm_list(sql_session):
    list = sql_session.query(GnVmMachines).all()
    for vmMachine in list:
        tagArr = vmMachine.tag.split(',')
        vmMachine.tag = tagArr[0] + '+' +str(len(tagArr))
        dt = vmMachine.create_time.strftime('%Y%m%d%H%M%S')
        dt2 = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        if(int(dt2[:4])-int(dt[:4]) == 0):
            if(int(dt2[:8])-int(dt[:8]) != 0):
                vmMachine.day1 = str(int(dt2[:8])-int(dt[:8]))+ "일 전"
            else:
                if(int(dt2[6:])-int(dt[6:]) != 0):
                    vmMachine.day1 = str((int(dt2[6:])-int(dt[6:]))/ 10000)+ "시간 전"
                else:
                    vmMachine.day1 = str((int(dt2[4:])-int(dt[4:]))/ 100)+ "분 전"
        else:
            vmMachine.day1 = str(int(dt2[:4])-int(dt[:4])) +"년 전"
    return list

def vm_info(sql_session, id):
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    vm_info.day1 = ""
    monitor_info = sql_session.query(GnMonitor).filter(GnMonitor.id == id).first()
    monitor_history_list = sql_session.query(GnMonitorHist).filter(GnMonitorHist.id == id).all()

    disk_info = {}
    if monitor_info is not None:
        total = vm_info.disk
        use = int(monitor_info.disk_usage)
        disk_per_info = int((use*100)/total)
        rest_disk = total - use;
        disk_info = {"total":total, "use":use, "rest_disk":rest_disk, "disk_per_info":disk_per_info}
    x_info=[]
    cpu_per_info=[]
    memory_x_info=[]
    memory_per_info=[]
    for list in monitor_history_list:
        x_info.append(list.cur_time.strftime('%H:%M'))
        cpu_per_info.append(int(list.cpu_usage))
        memory_per_info.append(int(list.mem_usage))


    info = {"vm_info":vm_info, "disk_info":disk_info, "x_info":x_info, "cpu_per_info":cpu_per_info, "memory_per_info":memory_per_info}

    return info


def login_list(user_id, password, team_code):
    password = random_string(password)
    return db_session.query(GnUser).filter(GnUser.team_code == team_code).filter(GnUser.user_id == user_id).filter(GnUser.password == password).one_or_none()


def me_list(myuser):
    return db_session.query(GnUser).filter(GnUser.user_id == myuser).one()


def teamcheck_list(teamcode):
    return db_session.query(GnUser).filter(GnUser.team_code == teamcode).all()


def sign_up(user_name, user_id, password, password_re):
    check = db_session.query(GnUser).filter(GnUser.user_id == user_id).one_or_none()
    print check
    if(password == password_re):
        if(check == None):
            password_sha = random_string(password_re)
            sign_up_info = GnUser(user_id = user_id, password = password_sha,user_name = user_name,start_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            db_session.add(sign_up_info)
            db_session.commit()
            return True
        else:
            return None
    else:
        return None

def repair(user_id, password, password_new, password_re, tel, email):
    test = db_session.query(GnUser).filter(GnUser.user_id == user_id).one_or_none()
    if password != "":
        password = random_string(password)
        test = db_session.query(GnUser).filter(GnUser.user_id == user_id).filter(GnUser.password==password).one_or_none()
        if (test != None and password_re == password_new):
              test.password = random_string(password_re)
        else:
                return 1


    if tel != "":
        test.tel = tel

    if email != "":
        test.eamil = email

    db_session.commit()
    return 2

def server_image_list(type, sub_type, sql_session):
    if(sub_type == ""):
        list = sql_session.query(GnVmImages).filter(GnVmImages.sub_type == type).all();
        return list
    elif(sub_type != ""):
        list = sql_session.query(GnVmImages).filter(GnVmImages.sub_type == type).filter(GnVmImages.type==sub_type).all()
        return list

def getQuotaOfTeam(team_code, sql_session):
    current_info = sql_session.query(func.sum(GnVmMachines.cpu).label("sum_cpu"),
                        func.sum(GnVmMachines.memory).label("sum_mem"),
                        func.sum(GnVmMachines.disk).label("sum_disk")
                        ).filter(GnVmMachines.team_code == team_code).one()
    limit_quota = sql_session.query(GnTeam).filter(GnTeam.team_code == team_code).one()
    vm_run_count = sql_session.query(func.count(GnVmMachines.id).label("count"))\
                   .filter(GnVmMachines.team_code == team_code and GnVmMachines.status == "running").one()
    vm_stop_count = sql_session.query(func.count(GnVmMachines.id).label("count")) \
        .filter(GnVmMachines.team_code == team_code and GnVmMachines.status == "stop").one()
    vm_kvm_count = sql_session.query(func.count(GnVmMachines.id).label("count")) \
        .filter(GnVmMachines.team_code == team_code).filter(GnVmMachines.type == "kvm").one()
    vm_hiperv_count = sql_session.query(func.count(GnVmMachines.id).label("count")) \
        .filter(GnVmMachines.team_code == team_code).filter(GnVmMachines.type == "hiperv").one()
    vm_docker_count = sql_session.query(func.count(GnVmMachines.id).label("count")) \
        .filter(GnVmMachines.team_code == team_code).filter(GnVmMachines.type == "docker").one()

    cpu_per_info = [int((current_info.sum_cpu/limit_quota.cpu_quota)*100), 100 - (int((current_info.sum_cpu/limit_quota.cpu_quota)*100))]
    memory_per_info = [int((current_info.sum_mem/limit_quota.mem_quota)*100), 100 - (int((current_info.sum_mem/limit_quota.mem_quota)*100))]
    disk_per_info = [int((current_info.sum_disk/limit_quota.disk_quota)*100), 100 - (int((current_info.sum_disk/limit_quota.disk_quota)*100))]
    cpu_cnt_info = [int(current_info.sum_cpu), limit_quota.cpu_quota]
    mem_cnt_info = [int(current_info.sum_mem), limit_quota.mem_quota]
    disk_cnt_info = [int(current_info.sum_disk), limit_quota.disk_quota]
    count_info = [vm_run_count.count,vm_stop_count.count]
    type_info = [vm_kvm_count.count,vm_hiperv_count.count]
    docker_info = vm_docker_count.count
    quato_info = {'cpu_per':cpu_per_info, 'memory_per':memory_per_info, 'disk_per':disk_per_info
                 , 'cpu_cnt':cpu_cnt_info, 'mem_cnt':mem_cnt_info, 'disk_cnt':disk_cnt_info
                 , 'vm_count':count_info, 'vm_type':type_info, 'docker_info':docker_info};

    return quato_info


def list_user_sshkey(team_code, sql_session):
    list = sql_session.query(GnSshKeys).all()
    return list




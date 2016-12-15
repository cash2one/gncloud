# -*- coding: utf-8 -*-
__author__ = 'NaDa'

from sqlalchemy import func
import datetime

from Manager.db.models import GnVmMachines, GnUser, GnTeam, GnVmImages, GnUserTeam, GnSshKeys, GnContanierImage
from Manager.db.database import db_session
from Manager.util.hash import random_string


def test_list():
    runlist = GnVmMachines.query.all()
    return runlist

def login_list(user_id, password):
    password = random_string(password)
    list = db_session.query(GnUser).filter(GnUser.user_id == user_id).filter(GnUser.password == password).one_or_none()
    return list


def me_list(user_id):
    team =db_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).one()
    list =db_session.query(GnTeam).filter(GnTeam.team_code ==team.team_code).one()
    return list

def tea(user_id, team_code):
    sub_stmt = db_session.query(GnUserTeam.user_id).filter(GnUserTeam.team_code == team_code)
    list = db_session.query(GnUser).filter(GnUser.user_id.in_(sub_stmt)).all()
    return list

def teamcheck_list(user_id):
    return db_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).all()

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

def server_image_list(type, sub_type):
    list = db_session.query(GnVmImages).filter(GnVmImages.sub_type == type).filter(GnVmImages.type==sub_type).all()
    return list

def server_image(type):
    list = db_session.query(GnVmImages).filter(GnVmImages.sub_type == type).all();
    return list

def getQuotaOfTeam(team_code):
    current_info = db_session.query(func.sum(GnVmMachines.cpu).label("sum_cpu"),
                        func.sum(GnVmMachines.memory).label("sum_mem"),
                        func.sum(GnVmMachines.disk).label("sum_disk")
                        ).filter(GnVmMachines.team_code == team_code).one()
    limit_quota = db_session.query(GnTeam).filter(GnTeam.team_code == team_code).one()
    vm_run_count = db_session.query(func.count(GnVmMachines.id).label("count"))\
                   .filter(GnVmMachines.team_code == team_code and GnVmMachines.status == "running").one()
    vm_stop_count = db_session.query(func.count(GnVmMachines.id).label("count")) \
        .filter(GnVmMachines.team_code == team_code and GnVmMachines.status == "stop").one()
    vm_kvm_count = db_session.query(func.count(GnVmMachines.id).label("count")) \
        .filter(GnVmMachines.team_code == team_code).filter(GnVmMachines.type == "kvm").one()
    vm_hiperv_count = db_session.query(func.count(GnVmMachines.id).label("count")) \
        .filter(GnVmMachines.team_code == team_code).filter(GnVmMachines.type == "hiperv").one()
    vm_docker_count = db_session.query(func.count(GnVmMachines.id).label("count")) \
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

def server_list(sql_session):
    list = sql_session.query(GnVmMachines).order_by("create_time desc").all()
    for vmMachine in list:
        tagArr = vmMachine.tag.split(',')
        vmMachine.num = tagArr[0] + '+' +str(len(tagArr))
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


def list_user_sshkey(team_code, sql_session):
    list = sql_session.query(GnSshKeys).all()
    return list


def teamsignup_list(comfirm, user_id):
    if(comfirm == 'N'):
        com= db_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).all()
        com.comfirm = 'Y'
        db_session.commit()
    return 1

def team_list(user_id):
    list= db_session.query(GnUser).filter(GnUser.user_id ==user_id).one()
    list.comfirm = ""
    return list

def container():
    return db_session.query(GnContanierImage).all()

def teamset(user_id, team_code):
    list = db_session.query(GnUser,GnUserTeam).join(GnUserTeam, GnUserTeam.user_id == GnUser.user_id).filter(GnUserTeam.team_code == team_code).all()
    return list

def approve_set(user_id,code,type,user_name):
    if(type == 'approve'):
        list = db_session.query(GnUserTeam).filter(GnUserTeam.user_id==user_id).filter(GnUserTeam.team_code == code).one()
        list.comfirm = "Y"
        db_session.commit()
        return True
    if(type == 'change'):
        list = db_session.query(GnTeam).filter(GnTeam.team_code== code).one()
        list.author_id = user_name
        db_session.commit()
        return True
    if(type == 'reset'):
        list = db_session.query(GnUser).filter(GnUser.user_id==user_id).one()
        list.password = random_string('11111111')
        db_session.commit()
        return True

def team_delete(id ,code):
    db_session.query(GnUserTeam).filter(GnUserTeam.user_id == id).filter(GnUserTeam.team_code == code).delete()
    db_session.commit()
    return True
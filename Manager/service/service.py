# -*- coding: utf-8 -*-
__author__ = 'NaDa'

from sqlalchemy import func
import datetime

from Manager.db.models import GnVmMachines, GnUser, GnTeam, GnVmImages, GnMonitor, GnMonitorHist, GnSshKeys, GnUserTeam, GnContanierImage
from Manager.db.database import db_session
from Manager.util.hash import random_string


def vm_list(sql_session):
    list = sql_session.query(GnVmMachines).order_by(GnVmMachines.create_time.desc()).all()
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

    disk_info = {}
    if monitor_info is not None:
        total = vm_info.disk
        use = int(monitor_info.disk_usage)
        disk_per_info = int((use*100)/total)
        rest_disk = total - use;
        disk_info = {"total":total, "use":use, "rest_disk":rest_disk, "disk_per_info":disk_per_info}

    info = {"vm_info":vm_info, "disk_info":disk_info}
    return info

def vm_info_graph(sql_session, id):
    monitor_history_list = sql_session.query(GnMonitorHist).filter(GnMonitorHist.id == id).order_by(GnMonitorHist.cur_time.desc()).limit(5).all()
    x_info=[]
    cpu_per_info=[]
    memory_per_info=[]
    for list in reversed(monitor_history_list):
        x_info.append(list.cur_time.strftime('%H:%M'))
        cpu_per_info.append(int(list.cpu_usage))
        memory_per_info.append(int(list.mem_usage))
    info = {"x_info":x_info, "cpu_per_info":cpu_per_info, "memory_per_info":memory_per_info}
    return info


def login_list(user_id, password):
    password = random_string(password)
    list = db_session.query(GnUser).filter(GnUser.user_id == user_id).filter(GnUser.password == password).one_or_none()
    return list


def teamwon_list(user_id):
    team =db_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).one()
    list =db_session.query(GnTeam).filter(GnTeam.team_code ==team.team_code).one()
    return list


def teamcheck_list(teamcode):
    return db_session.query(GnUser).filter(GnUser.team_code == teamcode).all()
def tea(user_id, team_code):
    sub_stmt = db_session.query(GnUserTeam.user_id).filter(GnUserTeam.team_code == team_code)
    list = db_session.query(GnUser).filter(GnUser.user_id.in_(sub_stmt)).all()
    return list
def checkteam(user_id):
    checklist = db_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).one_or_none()
    if(checklist != None):
        return db_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).one()
    else:
        return None

def teamcheck_list(user_id):
    list = db_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).all()
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

def server_image_list(type, sub_type, sql_session):
    if(sub_type == ""):
        list = sql_session.query(GnVmImages).filter(GnVmImages.sub_type == type).all();
        return list
    elif(sub_type != ""):
        list = sql_session.query(GnVmImages).filter(GnVmImages.sub_type == type).filter(GnVmImages.type==sub_type).all()
        return list
def server_image_list(type, sub_type, sql_session):
    list = sql_session.query(GnVmImages).filter(GnVmImages.sub_type == type).filter(GnVmImages.type==sub_type).all()
    return list


def server_image(type):
    list = db_session.query(GnVmImages).filter(GnVmImages.sub_type == type).all();
    return list

def getQuotaOfTeam(team_code):
    current_info = db_session.query(func.sum(GnVmMachines.cpu).label("sum_cpu"),
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

def team_list(user_id):
    list= db_session.query(GnUser).filter(GnUser.user_id ==user_id).one()
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

def signup_team(team_code,user_id):
    vm = GnUserTeam(user_id= user_id, team_code= team_code, comfirm = 'N',apply_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    db_session.add(vm)
    db_session.commit()
    return True

def comfirm_list(user_id):
    team =db_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).one()
    if(team.comfirm != 'Y'):
        list =db_session.query(GnTeam).filter(GnTeam.team_code ==team.team_code).one()
        return list

def createteam_list(team_name, team_code, author_id):
    vm = GnTeam(team_code= team_code, team_name=team_name, author_id=author_id)
    db_session.add(vm)
    db_session.commit()
    return True

def select():
    return db_session.query(GnTeam).all()
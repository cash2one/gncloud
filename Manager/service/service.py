from sqlalchemy import func

__author__ = 'NaDa'
import datetime

from Manager.db.models import GnVmMachines, GnUser, GnTeam
from Manager.db.database import db_session


def test_list():
    runlist = GnVmMachines.query.all()
    return runlist

def login_list(user_id, password, team_code):
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
            sign_up_info = GnUser(user_id = user_id, password = password,user_name = user_name,start_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            db_session.add(sign_up_info)
            db_session.commit()
            return True
        else:
            return None
    else:
        return None

def repair(user_id,user_name,team_code ,password, password_new, password_re, tel, email):
    test = db_session.query(GnUser).filter(GnUser.user_id == user_id).filter(GnUser.password == password).one_or_none()
    if(test != None):
        if(password_new == password_re):
            repair_info=GnUser(user_name=user_name,password= password_new, tel = tel, email = email)
            db_session.add(repair_info)
            db_session.commit()
            return True
        else:
            return 1
    else:
        pass

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




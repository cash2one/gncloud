# -*- coding: utf-8 -*-
__author__ = 'yhk'

import subprocess
import datetime
from pexpect import pxssh
from sqlalchemy import func
from kvm.db.models import GnVmMachines,GnHostMachines, GnMonitor, GnVmImages, GnMonitorHist, GnSshKeys, GnId
from kvm.db.database import db_session
from kvm.service.kvm_libvirt import kvm_create, kvm_change_status, kvm_vm_delete, kvm_image_copy, kvm_image_delete
from kvm.util.hash import random_string
from kvm.util.config import config

USER = "root"

def server_create(name, cpu, memory, disk, image_id, team_code, user_id, sshkeys, tag):
    result = {"status":True, "message":"sucess"}

    try:
        # host 선택 룰
        # host의 조회 순서를 우선으로 가용할 수 있는 자원이 있으면 해당 vm을 해당 host에서 생성한다
        host_ip = None
        host_id = None
        host_list = db_session.query(GnHostMachines).filter(GnHostMachines.type == "kvm").all()
        for host_info in host_list:
            use_sum_info = db_session.query(func.ifnull(func.sum(GnVmMachines.cpu),0).label("sum_cpu"),
                                            func.ifnull(func.sum(GnVmMachines.memory),0).label("sum_mem"),
                                            func.ifnull(func.sum(GnVmMachines.disk),0).label("sum_disk")
                                            ).filter(GnVmMachines.host_id == host_info.id).filter(GnVmMachines.status != "Removed").one_or_none()
            rest_cpu = host_info.max_cpu - use_sum_info.sum_cpu
            rest_mem = host_info.max_mem - use_sum_info.sum_mem
            rest_disk = host_info.max_disk - use_sum_info.sum_disk

            if rest_cpu >= int(cpu) and rest_mem >= int(memory) and rest_disk >= int(disk):
                host_ip = host_info.ip
                host_id = host_info.id


        if(host_ip is None):
            result = {"status":False, "message":"HOST 머신 리소스가 부족합니다"}
            return result

        # base image 조회
        image_info = db_session.query(GnVmImages).filter(GnVmImages.id == image_id).one()

        # vm 생성
        intern_id = kvm_create(name, cpu, memory, disk, image_info.filename, image_info.sub_type, host_ip)

        #ip 세팅
        ip = ""
        while len(ip) == 0:
            ip = getIpAddress(name, host_ip)

        if len(ip) != 0:
             setStaticIpAddress(ip, host_ip, image_info.ssh_id)

        # 기존 저장된 ssh key 등록
        if len(sshkeys) > 0:
            sshkey_list = GnSshKeys.query.filter(GnSshKeys.id.in_(sshkeys)).all()
            for gnSshkey in sshkey_list:
                s = pxssh.pxssh()
                s.login(host_ip, USER)
                s.sendline(config.SCRIPT_PATH+"add_sshkeys.sh '" + str(gnSshkey.path) + "' " + str(ip) + " "+image_info.ssh_id)
                s.logout()

        #db 저장
        #id 생성
        while True:
            id = random_string(8)
            check_info = GnId.query.filter(GnId.id == id).first();
            if not check_info:
                id_info = GnId(id,'kvn')
                db_session.add(id_info)
                db_session.commit()
                break

        vm_machine = GnVmMachines(id=id, name=name, cpu=cpu, memory=memory, disk=disk
                                  , type='kvm', internal_id=intern_id, internal_name=name, ip=ip, host_id=host_id, os=image_info.os
                                  , os_ver=image_info.os_ver, os_sub_ver=image_info.os_subver, os_bit=image_info.os_bit
                                  , team_code=team_code, author_id=user_id,status='running', tag=tag)
        db_session.add(vm_machine)
        return result
    except IOError as errmsg:
        db_session.rollback()
        print(errmsg)
    finally:
        db_session.commit()



def getIpAddress(name, host_ip):
    s = pxssh.pxssh()
    s.login(host_ip, USER)
    s.sendline(config.SCRIPT_PATH+"get_ipadress.sh " + name)
    s.prompt()
    ip = s.before.replace(config.SCRIPT_PATH+"get_ipadress.sh " + name + "\r\n", "")
    s.logout()
    return ip


def setStaticIpAddress(ip, host_ip, ssh_id):
    try:
        s = pxssh.pxssh()
        s.login(host_ip, USER)
        s.sendline(config.SCRIPT_PATH+"set_vm_ip.sh %s %s" % (ip, ssh_id))
        s.logout()
    except pxssh.TIMEOUT:
        print("==timeout==")
        pass
    except IOError as errmsg:
        pass

def server_delete(id,sql_session):
    guest_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one();

    # backup image
    s = pxssh.pxssh()
    s.login(guest_info.gnHostMachines.ip, USER)
    s.sendline("cp "+config.LIVERT_IMAGE_PATH+guest_info.internal_name+".img "+config.LIVERT_IMAGE_BACKUP_PATH+guest_info.internal_name+".img")
    s.close()

    # vm 삭제
    kvm_vm_delete(guest_info.internal_name, guest_info.gnHostMachines.ip);

    # db 저장
    guest_info.status = "Removed"
    sql_session.commit()


def server_image_delete(id, sql_session):

    image_info = sql_session.query(GnVmImages).filter(GnVmImages.id == id).one()
    # 물리적 이미지 삭제하지 않고 데이터만 삭제된걸로 수정
    kvm_image_delete(image_info.filename)
    image_info.status = "Removed"
    sql_session.commit()


def server_change_status(id, status, sql_session):
    guest_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    kvm_change_status(guest_info.internal_name, status, guest_info.gnHostMachines.ip)
    guest_info.status = status
    sql_session.commit()


def server_create_snapshot(id, name, user_id, team_code):
    try:
        guest_info = GnVmMachines.query.filter(GnVmMachines.id == id).one();

        # 네이밍
        new_image_name = guest_info.internal_name + "_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        # 디스크 복사
        kvm_image_copy(guest_info.internal_name, new_image_name, guest_info.gnHostMachines.ip)

        #id 생성
        while True:
            id = random_string(8)
            check_info = GnId.query.filter(GnId.id == id).first()
            if not check_info:
                break

        guest_snap = GnVmImages(id=id, name=name, type="kvm", sub_type="snap", filename=new_image_name + ".img"
                                , icon="", os=guest_info.os, os_ver=guest_info.os_ver, os_subver=guest_info.os_sub_ver
                                , os_bit=guest_info.os_bit, team_code=team_code, author_id=user_id)
        db_session.add(guest_snap)
    except:
        db_session.rollback()
    finally:
        db_session.commit()


def server_monitor(sql_session):
    try:
        lists = sql_session.query(GnVmMachines).filter(GnVmMachines.type == "kvm").all()
        for list in lists:
            host_ip = list.gnHostMachines.ip
            s = pxssh.pxssh()
            s.login(host_ip, USER)
            s.sendline(config.SCRIPT_PATH+"get_vm_use.sh cpu " + list.ip + " "+list.os)
            s.prompt()
            cpu_use = (str(s.before)).split("\r\n")[3]
            s.sendline(config.SCRIPT_PATH+"get_vm_use.sh mem " + list.ip + " "+list.os)
            s.prompt()
            mem_use = (str(s.before)).split("\r\n")[2]
            s.sendline(config.SCRIPT_PATH+"get_vm_use.sh disk " + list.ip + " "+list.os)
            s.prompt()
            disk_use = (str(s.before)).split("\r\n")[2]
            s.sendline(config.SCRIPT_PATH+"get_vm_use.sh net " + list.ip + " "+list.os)
            s.prompt()
            net_use = (str(s.before)).split("\r\n")[2]
            s.logout()

            vm_monitor_hist = GnMonitorHist(id=list.id, type="kvm", cpu_usage=cpu_use, mem_usage=mem_use, disk_usage=disk_use, net_usage=net_use)
            sql_session.add(vm_monitor_hist)

            gnMontor_info = sql_session.query(GnMonitor).filter(GnMonitor.id == list.id).one_or_none()
            if gnMontor_info is None:
                vm_monitor = GnMonitor(id=list.id, type="kvm", cpu_usage=cpu_use, mem_usage=mem_use, disk_usage=disk_use, net_usage=net_use)
                sql_session.add(vm_monitor)
            else:
                gnMontor_info.cpu_usage = cpu_use
                gnMontor_info.mem_usage = mem_use
                gnMontor_info.disk_usage = disk_use
                gnMontor_info.net_usage = net_use

    except:
        sql_session.rollback()
    finally:
        print("end")
        sql_session.commit()


def add_user_sshkey(team_code, name):
    try:
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        path = config.SSHKEY_PATH+now

        result = subprocess.check_output ("ssh-keygen -f "+ path +" -P ''", shell=True)
        fingerprint = result.split("\n")[4].split(" ")[0]

        # db 저장
        gnSshKeys = GnSshKeys(team_code=team_code, name=name, fingerprint=fingerprint, path=path)
        db_session.add(gnSshKeys)
    except:
        db_session.rollback()
    finally:
        db_session.commit()


def delete_user_sshkey(id):
    try:
        db_session.query(GnSshKeys).filter(GnSshKeys.id == id).delete();
    except:
        db_session.rollback()
    finally:
        db_session.commit()

    # 남아있는 key 리스트 조회
    # key_list = db_session.query(GnSshKeys).filter(GnSshKeys.team_code == team_name).all()
    # vm_list = db_session.query(GnVmMachines).filter(GnVmMachines.team_name == team_name).all()
    #
    # for gnVmMachine in vm_list:
    #     s = pxssh.pxssh()
    #     s.login(gnVmMachine.gnHostMachines.ip, USER)
    #     for gnSshkey in key_list:
    #         s.sendline("/root/libvirt/set_authorized_keys.sh '%s' %s" % (gnSshkey.key_content, 'create'))
    #
    #     s.sendline("/root/libvirt/set_authorized_keys.sh '%s' %s" % (gnVmMachine.ip, 'send'))
    #
    # s.logout()

def list_user_sshkey(team_code, sql_session):
    list = sql_session.query(GnSshKeys).all()
    return list

def getsshkey_info(id):
    return db_session.query(GnSshKeys).filter(GnSshKeys.id == id).one()

def vm_detail_info(id):
    db_session.query(GnVmMachines).filter(GnVmMachines.id == id).all()





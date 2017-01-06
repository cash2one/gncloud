# -*- coding: utf-8 -*-
__author__ = 'yhk'

import subprocess

import datetime
from pexpect import pxssh

from kvm.db.models import GnVmMachines,GnHostMachines, GnMonitor, GnVmImages, GnMonitorHist, GnSshKeys
from kvm.db.database import db_session
from kvm.service.kvm_libvirt import kvm_create, kvm_change_status, kvm_vm_delete, kvm_image_copy, kvm_image_delete
from kvm.util.config import config

USER = "root"

def server_create(team_code, user_id, id, sql_session):
    try:
        #vm 조회
        vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()

        #host 조회
        host_info = sql_session.query(GnHostMachines).filter(GnHostMachines.id == vm_info.host_id).one()

        # base image 조회
        image_info = db_session.query(GnVmImages).filter(GnVmImages.id == vm_info.image_id).one()

        # ssh 조회
        ssh_info = db_session.query(GnSshKeys).filter(GnSshKeys.id == vm_info.ssh_key_id).one()

        # vm 생성
        internal_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        intern_id = kvm_create(internal_name, vm_info.cpu, vm_info.memory, vm_info.disk, image_info.filename, image_info.sub_type, host_info.ip)

        #ip 세팅
        ip = ""
        while len(ip) == 0:
            ip = getIpAddress(internal_name, host_info.ip)

        if len(ip) != 0:
             setStaticIpAddress(ip, host_info.ip, image_info.ssh_id)

        # 기존 저장된 ssh key 등록
        # s = pxssh.pxssh()
        # s.login(host_info.ip, USER)
        # s.sendline(config.SCRIPT_PATH+"add_sshkeys.sh '" + str(ssh_info.path) + "' " + str(ip) + " "+image_info.ssh_id)
        # s.logout()

        vm_info.internal_name = internal_name
        vm_info.internal_id = intern_id
        vm_info.ip = ip
        vm_info.status = "Running"
        vm_info.os = image_info.os
        vm_info.os_ver = image_info.os_ver
        vm_info.os_sub_ver = image_info.os_subver
        vm_info.os_bit = image_info.os_bit
        sql_session.commit()
    except:
        vm_info.status="Error"
        sql_session.commit()


def getIpAddress(name, host_ip):
    s = pxssh.pxssh()
    s.login(host_ip, USER)
    s.sendline(config.SCRIPT_PATH+"get_ipaddress.sh " + name)
    s.prompt()
    ip = s.before.replace(config.SCRIPT_PATH+"get_ipaddress.sh " + name + "\r\n", "")
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
    kvm_image_delete(image_info.filename, image_info.gnHostMachines.ip)
    image_info.status = "Removed"
    sql_session.commit()


def server_change_status(id, status, sql_session):
    guest_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    kvm_change_status(guest_info.internal_name, status, guest_info.gnHostMachines.ip)
    if status == "Reboot" or status == "Resume":
        status = "Running"
    guest_info.status = status
    sql_session.commit()


def server_create_snapshot(id, image_id, user_id, team_code, sql_session):

    snap_info = sql_session.query(GnVmImages).filter(GnVmImages.id == image_id).one()
    guest_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    try:
        # 네이밍
        new_image_name = guest_info.internal_name + "_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        # 디스크 복사
        kvm_image_copy(guest_info.internal_name, new_image_name, guest_info.gnHostMachines.ip)

        snap_info.filename = new_image_name+'.img'
        snap_info.status = "Running"
        snap_info.host_id = guest_info.gnHostMachines.id
        sql_session.commit()
    except:
        snap_info.status = "Error"
        sql_session.commit()


def server_monitor(sql_session):
    try:
        lists = sql_session.query(GnVmMachines).filter(GnVmMachines.type == "kvm").filter(GnVmMachines.status == "running").all()
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
        path = config.SSHKEY_PATH+ now

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





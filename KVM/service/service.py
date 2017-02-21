# -*- coding: utf-8 -*-
__author__ = 'yhk'

import subprocess

from KVM.db.database import db_session
from KVM.db.models import *
from KVM.service.kvm_libvirt import *
from KVM.util.config import config

USER = "root"

def server_create(team_code, user_id, user_name, id, sql_session):
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
        print("complete init vm!!!")
        #ip 세팅
        ip = ""
        while len(ip) == 0:
            print(id+":processing init ip!!!")
            ip = getIpAddress(internal_name, host_info.ip)
        print("complete get ip="+ip)
        #ip 고정
        # if len(ip) != 0:
        #     print(id+":set init ip!!!")
        #     setStaticIpAddress(ip, host_info.ip, image_info.ssh_id)
        #     print(id+":complete set ip!!!")

        # 기존 저장된 ssh key 등록
        setSsh(host_info.ip,ssh_info.pub,ssh_info.org,ssh_info.name, ip, image_info.ssh_id)
        print(id+":processing modify data!!!")
        vm_info.internal_name = internal_name
        vm_info.internal_id = intern_id
        vm_info.ip = ip
        vm_info.status = "Running"
        vm_info.os = image_info.os
        vm_info.os_ver = image_info.os_ver
        vm_info.os_sub_ver = image_info.os_subver
        vm_info.os_bit = image_info.os_bit

        print(id+":insert payment info")
        vm_size = sql_session.query(GnVmSize).filter(GnVmSize.id == vm_info.size_id).first()
        system_setting = sql_session.query(GnSystemSetting).first()
        instance_status_price = None
        if system_setting.billing_type == 'D':
            instance_status_price = vm_size.day_price
        elif system_setting.billing_type == 'H':
            instance_status_price = vm_size.hour_price

        insert_instance_status = GnInstanceStatus(vm_id=vm_info.id,vm_name=vm_info.name,author_id=vm_info.author_id,author_name=user_name, team_code=vm_info.team_code
                                                  , price=instance_status_price,price_type=system_setting.billing_type
                                                  , cpu=vm_info.cpu, memory=vm_info.memory,disk=vm_info.disk)
        sql_session.add(insert_instance_status)

        sql_session.commit()
        print(id+":complete modify data!!!")
        return True
    except Exception as e:
        print(id+":init vm error!!!")
        print("error:"+e.message)
        error_hist = GnErrorHist(type=vm_info.type,action="Create",team_code=vm_info.team_code,author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name, cause=e.message, action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        sql_session.add(error_hist)
        vm_info.status = "Error"
        sql_session.commit()
        return False

def setSsh(host_ip, pub,org,name, ip, ssh_id):
    try:
        f = open("/data/kvm/sshkeys/"+name+".pub", 'w')
        f.write(pub)
        f.close()
        f = open("/data/kvm/sshkeys/"+name, 'w')
        f.write(org)
        f.close()
        print(":processing set sshkey!!!")
        s = pxssh.pxssh(timeout=1200)
        s.login(host_ip, USER)
        s.sendline(config.SCRIPT_PATH+"add_sshkeys.sh '" +"/data/kvm/sshkeys/"+name + "' " + str(ip) + " "+ssh_id)
        s.logout()
        print(":complete set sshkey!!!")
    except IOError as e:
        print(e)
        pass

def getIpAddress(name, host_ip):
    s = pxssh.pxssh(timeout=1200)
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
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    status_info = sql_session.query(GnInstanceStatus).filter(GnInstanceStatus.vm_id == id).one()
    backup_list = sql_session.query(GnBackupHist).filter(GnBackupHist.vm_id == id).all()
    try:
        # vm 삭제
        kvm_vm_delete(vm_info.internal_name, vm_info.gnHostMachines.ip);

        s = pxssh.pxssh()
        s.login(vm_info.gnHostMachines.ip, USER)
        for backup_info in backup_list:
            s.sendline("rm -f "+config.LIVERT_IMAGE_BACKUP_PATH+backup_info.filename)

        s.logout()
        sql_session.query(GnBackupHist).filter(GnBackupHist.vm_id == id).delete()

        # db 저장
        sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).delete()
        #과금 테이블 업데이트
        status_info.delete_time = datetime.datetime.now()
        sql_session.commit()
    except Exception as e:
        print("error:"+e.message)
        error_hist = GnErrorHist(type=vm_info.type,action="Delete",team_code=vm_info.team_code,author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name, cause=e.message, action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        sql_session.add(error_hist)
        sql_session.commit()

def server_image_delete(id, sql_session):

    image_info = sql_session.query(GnVmImages).filter(GnVmImages.id == id).one()
    s = pxssh.pxssh()
    s.login(image_info.gnHostMachines.ip, USER)
    s.sendline("rm -f "+config.LIVERT_IMAGE_SNAPSHOT_PATH+image_info.filename)
    s.logout()
    #kvm_image_delete(image_info.filename, image_info.gnHostMachines.ip)
    sql_session.query(GnVmImages).filter(GnVmImages.id == id).delete()
    sql_session.commit()


def server_change_status(id, status, sql_session):
    try:
        vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
        kvm_change_status(vm_info.internal_name, status, vm_info.gnHostMachines.ip)
        if status == "Reboot" or status == "Resume":
            status = "Running"
        vm_info.status = status
        sql_session.commit()
        return True
    except Exception as e:
        print("error"+ e.message)
        error_hist = GnErrorHist(type=vm_info.type,action=status,team_code=vm_info.team_code,author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name, cause=e.message,action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        sql_session.add(error_hist)
        sql_session.commit()
        return False



def server_create_snapshot(id, image_id, user_id, team_code, sql_session):
    snap_info = db_session.query(GnVmImages).filter(GnVmImages.id == image_id).one()
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).one()
    try:
        # 네이밍
        new_image_name = vm_info.internal_name + "_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        # 디스크 복사
        s = pxssh.pxssh(timeout=1200)
        s.login(vm_info.gnHostMachines.ip, USER)
        s.sendline("cp "+config.LIVERT_IMAGE_LOCAL_PATH+vm_info.internal_name+".img"+" "+config.LIVERT_IMAGE_SNAPSHOT_PATH+new_image_name+".img")
        s.logout()

        snap_info.filename = new_image_name+'.img'
        snap_info.status = "Running"
        snap_info.host_id = vm_info.gnHostMachines.id
        sql_session.commit()
    except Exception as e:
        print(e.message)
        error_hist = GnErrorHist(type=vm_info.type,action="Snap-create",team_code=vm_info.team_code,author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name, cause=e.message,action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        sql_session.add(error_hist)
        snap_info.status = "Error"
        sql_session.commit()

def setChangDhcp(host_ip,ip ,ssh_id, type):
    try:
        s = pxssh.pxssh()
        s.login(host_ip, USER)
        s.sendline(config.SCRIPT_PATH+"set_vm_dhcp.sh %s %s %s" % (ip, ssh_id, type))
        s.logout()
    except pxssh.TIMEOUT:
        print("==timeout==")
        pass
    except IOError as errmsg:
        pass



def server_monitor(sql_session):
    try:
        lists = sql_session.query(GnVmMachines).filter(GnVmMachines.type == "kvm").filter(GnVmMachines.status == "Running").all()
        for list in lists:
            try:
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
                continue

    except:
        sql_session.rollback()
    finally:
        print("end")
        sql_session.commit()


def add_user_sshkey(team_code, name):
    try:
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        path = config.SSHKEY_PATH+ now

        result = subprocess.check_output("ssh-keygen -f "+ path +" -P ''", shell=True)
        list = subprocess.check_output("cat "+path+".pub",shell=True)
        org = subprocess.check_output("cat "+path,shell=True)
        fingerprint = result.split("\n")[4].split(" ")[0]

        # db 저장
        gnSshKeys = GnSshKeys(team_code=team_code, name=name, fingerprint=fingerprint, pub=list, org=org)
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
    list = sql_session.query(GnSshKeys).filter(GnSshKeys.team_code == team_code).all()
    return list

def getsshkey_info(id):
    return db_session.query(GnSshKeys).filter(GnSshKeys.id == id).one()

def vm_detail_info(id):
    db_session.query(GnVmMachines).filter(GnVmMachines.id == id).all()




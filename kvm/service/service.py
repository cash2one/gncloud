# -*- coding: utf-8 -*-
__author__ = 'yhk'

from kvm.db.models import GnVmMachines, GnVmImages, GnHostMachines, GnVmMonitor
from kvm.db.database import db_session
from kvm.service.kvm_libvirt import kvm_create, kvm_change_status
import paramiko
import datetime
import time
from pexpect import pxssh

USER = "root"
LOCAL_SSH_KEY_PATH = "/Users/yhk/.ssh/id_rsa"


def server_create(name, cpu, memory, disk, image_id):
    try:
        # base image 조회
        image_info = db_session.query(GnVmImages).filter(GnVmImages.image_id == image_id).one()

        # vm 생성
        id = kvm_create(name, cpu, memory, disk, image_info.image_filename, image_info.image_sub_type)
        #ip 세팅
        ip = ""
        while len(ip) == 0:
            ip = getIpAddress(name, '192.168.0.131')

        print("start ==ssh set static ip==")
        if len(ip) != 0:
            setStaticIpAddress(ip, '192.168.0.131')

        # db 저장
        vm_machine = GnVmMachines(vm_id=id, vm_name=name, cpu=cpu, memory=memory, disk=disk
                                  , vm_type='kvm', ip=ip, host_id=1, os=image_info.os, os_ver=image_info.os_ver
                                  , os_sub_ver=image_info.os_subver, os_bit=image_info.os_bit, author_id='곽영호',
                                  status='running')
        db_session.add(vm_machine)
        db_session.commit()
    except IOError as errmsg:
        return str(errmsg)

    return "success"


def getIpAddress(name, HOST):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, key_filename=LOCAL_SSH_KEY_PATH)
    stdin, stdout, stderr = ssh.exec_command('/root/get_ipadress.sh ' + name)
    ip = stdout.readlines()
    ssh.close()
    return ip


def setStaticIpAddress(ip, HOST):
    try:
        # vm에 sudo명령을 사용하기 위해 ssh 접속 라이브러리 교체
        # ssh = paramiko.SSHClient()
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # ssh.connect(HOST, username=USER, key_filename=LOCAL_SSH_KEY_PATH)
        # stdin, stdout, stderr = ssh.exec_command('/root/set_vm_ip.sh ' + ip)
        # stdin, stdout, stderr = ssh.exec_command('/root/set_vm_ip.sh ' + ip)
        # ssh.close()
        print("start shell==ssh set static ip==")
        # pxssh
        s = pxssh.pxssh()
        s.login(HOST, USER)
        print("==c1==")
        s.sendline('/root/set_vm_ip.sh %s' % (ip[0]))
        s.prompt()
        print("==c2==")
        s.sendline('yes')
        s.prompt()
        print("==c3==")
        s.logout()
        print("==ssh set static ip==")
    except pxssh.TIMEOUT:
        print("==timeout==")
        pass
    except IOError as errmsg:
        pass


def server_list():
    list = GnVmMachines.query.all();
    return list


def server_image_list(type):
    list = db_session.query(GnVmImages).filter(GnVmImages.image_sub_type == type).all();
    return list


def server_change_status(name, status):
    guest_info = GnVmMachines.query.filter(GnVmMachines.name == name).one();
    ip = guest_info.gnHostMachines.ip
    URL = 'qemu+ssh://root@' + ip + '/system?socket=/var/run/libvirt/libvirt-sock'
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    kvm_change_status(name, status, now, URL)
    if status == 'delete':
        db_session.query(GnVmMachines).filter(GnVmMachines.vm_name == name).delete();
        db_session.commit()
    elif status == "snap":
        guest_snap = GnVmImages(name=name + "_" + now, type="kvm_snap", reg_dt=time.strftime('%Y-%m-%d %H:%M:%S'))
        db_session.add(guest_snap)
        db_session.commit()


def server_monitor():
    lists = db_session.query(GnVmMachines).filter(GnVmMachines.type == "kvm").all()

    for list in lists:
        HOST = list.gnHostMachines.ip
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=LOCAL_SSH_KEY_PATH)
        stdin, stdout, stderr = ssh.exec_command('/root/get_vm_use.sh mem ' + list.ip)
        cpu_use = stdout.readlines()
        stdin, stdout, stderr = ssh.exec_command('/root/get_vm_use.sh cpu ' + list.ip)
        mem_use = stdout.readlines()
        ssh.close()

        vm_monitor = GnVmMonitor(name=list.name, cpu_use=cpu_use, mem_use=mem_use)
        db_session.add(vm_monitor)
        db_session.commit()

# -*- coding: utf-8 -*-
__author__ = 'yhk'

from kvm.db.models import GnVmMachines, GnVmImages, GnHostMachines, GnVmMonitor, GnSshKeys
from kvm.db.database import db_session
from kvm.service.kvm_libvirt import kvm_create, kvm_change_status, kvm_vm_delete, kvm_image_copy, kvm_image_delete
import paramiko
import datetime
import time
from pexpect import pxssh
import pexpect

USER = "root"
LOCAL_SSH_KEY_PATH = "/Users/yhk/.ssh/id_rsa"


def server_create(name, cpu, memory, disk, image_id, team_name):
    try:
        # host 선택 룰
        host_ip = '192.168.0.131'
        # base image 조회
        image_info = db_session.query(GnVmImages).filter(GnVmImages.id == image_id).one()

        # vm 생성
        id = kvm_create(name, cpu, memory, disk, image_info.filename, image_info.sub_type)

        #ip 세팅
        ip = ""
        while len(ip) == 0:
            ip = getIpAddress(name, host_ip)

        if len(ip) != 0:
            setStaticIpAddress(ip, '192.168.0.131')


        # 기존 저장된 ssh key 등록
        sshkey_list = db_session.query(GnSshKeys).filter(GnSshKeys.team_name == team_name).all();
        for gnSshkey in sshkey_list:
            s = pxssh.pxssh()
            s.login(host_ip, USER)
            s.sendline("/root/libvirt/add_sshkeys.sh '" + str(gnSshkey.key_content) + "' " + str(ip))
            s.logout()

        # db 저장
        vm_machine = GnVmMachines(id=id[0:7], name=name, cpu=cpu, memory=memory, disk=disk
                                  , type='kvm', internal_id=id, internal_name=name, ip=ip, host_id=1, os=image_info.os,
                                  os_ver=image_info.os_ver
                                  , os_sub_ver=image_info.os_subver, os_bit=image_info.os_bit, author_id='곽영호',
                                  status='running')
        db_session.add(vm_machine)
        db_session.commit()
        print("==end==")
    except IOError as errmsg:
        return str(errmsg)

    return "success"


def getIpAddress(name, HOST):
    s = pxssh.pxssh()
    s.login(HOST, USER)
    s.sendline('/root/libvirt/get_ipadress.sh ' + name)
    s.prompt()
    ip = s.before.replace('/root/libvirt/get_ipadress.sh ' + name + '\r\n', "")
    s.logout()
    return ip


def setStaticIpAddress(ip, HOST):
    try:
        s = pxssh.pxssh()
        s.login(HOST, USER)
        s.sendline('/root/libvirt/set_vm_ip.sh %s' % (ip))
        s.prompt(timeout=120)
        s.logout()
    except pxssh.TIMEOUT:
        print("==timeout==")
        pass
    except IOError as errmsg:
        pass


def server_list():
    list = GnVmMachines.query.all();
    return list


def server_delete(id):
    guest_info = GnVmMachines.query.filter(GnVmMachines.id == id).one();

    # backup image
    s = pxssh.pxssh()
    s.login(guest_info.gnHostMachines.ip, USER)
    s.sendline('cp /var/lib/libvirt/image/%s.img /var/lib/libvirt/backup/$s.img' % (
    guest_info.internal_name, guest_info.internal_name))

    # vm 삭제
    kvm_vm_delete(guest_info.internal_name);

    # db 저장
    db_session.query(GnVmMachines).filter(GnVmMachines.id == id).delete();
    db_session.commit()

def server_image_list(type):
    list = db_session.query(GnVmImages).filter(GnVmImages.sub_type == type).all();
    return list


def server_image_delete(id):
    image_info = GnVmImages.query.filter(GnVmImages.id == id).one();
    # 물리적 이미지 삭제
    kvm_image_delete(image_info.filename)
    # db 저장
    db_session.query(GnVmImages).filter(GnVmImages.id == id).delete();
    db_session.commit()


def server_change_status(id, status):
    guest_info = GnVmMachines.query.filter(GnVmMachines.id == id).one();
    ip = guest_info.gnHostMachines.ip
    URL = 'qemu+ssh://root@' + ip + '/system?socket=/var/run/libvirt/libvirt-sock'
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    kvm_change_status(guest_info.internal_name, status, now, URL)


def server_create_snapshot(id, name, user_id, team_code):
    guest_info = GnVmMachines.query.filter(GnVmMachines.id == id).one();

    # 네이밍
    new_image_name = guest_info.internal_name + "_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    # 디스크 복사
    kvm_image_copy(guest_info.internal_name, new_image_name)

    # db 저장
    guest_snap = GnVmImages(id="1234", name=name, type="kvm", sub_type="snap", filename=new_image_name + ".img"
                            , icon="", os=guest_info.os, os_ver=guest_info.os_ver, os_subver=guest_info.os_sub_ver
                            , os_bit=guest_info.os_bit, team_code=team_code, author_id=user_id)
    db_session.add(guest_snap)
    db_session.commit()


def server_monitor():
    lists = db_session.query(GnVmMachines).filter(GnVmMachines.type == "kvm").all()

    for list in lists:
        HOST = list.gnHostMachines.ip
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=LOCAL_SSH_KEY_PATH)
        stdin, stdout, stderr = ssh.exec_command('/root/libvirt/get_vm_use.sh mem ' + list.ip)
        cpu_use = stdout.readlines()
        stdin, stdout, stderr = ssh.exec_command('/root/libvirt/get_vm_use.sh cpu ' + list.ip)
        mem_use = stdout.readlines()
        ssh.close()

        vm_monitor = GnVmMonitor(name=list.name, cpu_use=cpu_use, mem_use=mem_use)
        db_session.add(vm_monitor)
        db_session.commit()


def add_user_sshkey(team_name, sshkey, name):
    # 해당 팀의 vm 리스트 조회
    list = db_session.query(GnVmMachines).all();
    fingerprint = ""
    for gnVmMachine in list:
        s = pxssh.pxssh()
        s.login(gnVmMachine.gnHostMachines.ip, USER)
        s.sendline("/root/libvirt/add_sshkeys.sh '" + sshkey + "' " + gnVmMachine.ip)
        if fingerprint == "":
            s.sendline("ssh-keygen -lf /root/libvirt/sshkey.pub")
            s.prompt()
            fingerprint = s.before.replace("ssh-keygen -lf /root/libvirt/sshkey.pub\r\n", "").split(" ")[1]
        s.logout()

    # db 저장
    gnSshKeys = GnSshKeys(team_name=team_name, key_name=name, key_fingerprint=fingerprint, key_content=sshkey)
    db_session.add(gnSshKeys)
    db_session.commit()


def delete_user_sshkey(id, team_name):
    # db 삭제
    # gnSshKeys = GnSshKeys(id=id)
    # db_session.remove(gnSshKeys)
    # db_session.commit()

    # 남아있는 key 리스트 조회
    key_list = db_session.query(GnSshKeys).filter(GnSshKeys.team_name == team_name).all()
    vm_list = db_session.query(GnVmMachines).filter(GnVmMachines.team_name == team_name).all()

    for gnVmMachine in vm_list:
        s = pxssh.pxssh()
        s.login(gnVmMachine.gnHostMachines.ip, USER)
        for gnSshkey in key_list:
            s.sendline("/root/libvirt/set_authorized_keys.sh '%s' %s" % (gnSshkey.key_content, 'create'))

        s.sendline("/root/libvirt/set_authorized_keys.sh '%s' %s" % (gnVmMachine.ip, 'send'))

    s.logout()


def list_user_sshkey(team_name):
    return db_session.query(GnSshKeys).filter(GnSshKeys.team_name == team_name).all()


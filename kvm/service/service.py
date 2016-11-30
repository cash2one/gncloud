__author__ = 'yhk'

from kvm.db.models import GnGuestMachines, GnGuestImages
from kvm.db.database import db_session
from kvm.service.kvm_libvirt import kvm_create, kvm_change_status, server_write
import paramiko
import datetime
import time

HOST = "192.168.0.131"
USER = "root"

def server_create(name, cpu, memory, hdd, base):
    try:
        kvm_create(name, cpu, memory, hdd, base)

        ip = ""
        while len(ip) == 0:
            ip = getIpAddress(name)

        guest_machine = GnGuestMachines(name=name, cpu=cpu, memory=memory, hdd=hdd, type='kvm', ip=ip, status='running')
        db_session.add(guest_machine)
        db_session.commit()
    except IOError as errmsg:
        return errmsg

    return "ok"

def getIpAddress(name):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, key_filename="/Users/yhk/.ssh/id_rsa")
    stdin, stdout, stderr = ssh.exec_command('/root/get_ipadress.sh ' + name)
    ip = stdout.readlines()
    ssh.close()

    return ip

def server_list():
    list = GnGuestMachines.query.all();
    return list


def server_image_list(type):
    list = db_session.query(GnGuestImages).filter(GnGuestImages.type == type).all();
    return list

def server_change_status(name, status):
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    kvm_change_status(name, status, now)
    if status == 'delete':
        db_session.query(GnGuestMachines).filter(GnGuestMachines.name == name).delete();
        db_session.commit()
    elif status == "snap":
        guest_snap = GnGuestImages(name=name + "_" + now, type="kvm_snap", reg_dt=time.strftime('%Y-%m-%d %H:%M:%S'))
        db_session.add(guest_snap)
        db_session.commit()


def server_monitor():
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    server_write(now);

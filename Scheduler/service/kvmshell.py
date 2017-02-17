# -*- coding: utf-8 -*-
__author__ = 'nhcho'

import subprocess

import datetime
from pexpect import pxssh
from Scheduler.db.models import *
from Scheduler.db.database import db_session
from Scheduler.util.config import config


# It must be ssh key setting.
# for example  scheduler controller host is set 'ssh-keygen -f ~/.ssh/id_rsa'
#              kvm host is set from ssh copy    'ssh-copy-id -i  ~/.ssh/id_rsa.pub centos@192.168.1.5'
class KvmShell:
    def __init__(self):
        self.sql_session = db_session
        self.USER = "root"

    def backup_send(self, guest_info, dest_ip, dest_path):
        try:
            new_image_name = guest_info.internal_name + "_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            # 디스크 복사
            s = pxssh.pxssh(timeout=1200)
            s.login(dest_ip, self.USER)
            s.sendline("cp "+config.LIVERT_IMAGE_LOCAL_PATH+guest_info.internal_name+".img"+" "+dest_path+new_image_name+".img")
            s.logout()
            return new_image_name
        except Exception as e:
            print(e.message)
            return 'error'

    def backup_delete_send(self, dest_ip, filename, path):
        try:
            s = pxssh.pxssh(timeout=1200)
            s.login(dest_ip, self.USER)
            s.sendline("rm -f "+path+filename)
            s.logout()
            return True
        except Exception as e:
            print(e.message)
            return False
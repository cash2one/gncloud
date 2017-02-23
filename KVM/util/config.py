# -*- coding: utf-8 -*-
# 고정적으로 사용하는 값들을 한 곳에 모아두기 위해 만든 상수용 파이썬 파일
import ConfigParser
import os
import sys

from KVM.util.logger import logger

class Config:
    #[DEFAULT]
    #kvm manage server
    LIBVIRT_REMOTE_URL = 'qemu+ssh://root@ip/system?socket=/var/run/libvirt/libvirt-sock'
    POOL_NAME = 'gnpool'

    #db server
    DB_URL = 'mysql://gncloud:gncloud@db/gncloud?charset=utf8'

    #file_path
    #LIVERT_IMAGE_BASE_PATH = '/home/images/kvm/base/'
    #LIVERT_IMAGE_SNAPSHOT_PATH = '/home/images/kvm/snapshot/'
    #LIVERT_IMAGE_BACKUP_PATH = '/home/images/kvm/backup/'
    #LIVERT_IMAGE_LOCAL_PATH = '/home/images/kvm/instance/'
    SCRIPT_PATH = '/var/lib/gncloud/KVM/script/'
    SSHKEY_PATH = '/tmp/'

    IMAGE_PATH_PRIFIX = '/home/images/kvm/'

    #환경변수 /local/ /nas/
    #LOCAL_DRIVE = local
    #NETWORK_DRIVE = nas
    def __init__(self):
        NETOWRK_DRIVE = 'nas'
        LOCAL_DRIVE = 'local'
        keys = os.environ.keys()
        for values in keys:
            if values == 'NETWORK_DRIVE':
                self.LIVERT_IMAGE_BASE_PATH = self.IMAGE_PATH_PRIFIX + os.environ['NETWORK_DRIVE']+"/base/"
                self.LIVERT_IMAGE_SNAPSHOT_PATH = self.IMAGE_PATH_PRIFIX + os.environ['NETWORK_DRIVE']+"/snapshot/"
                self.LIVERT_IMAGE_BACKUP_PATH = self.IMAGE_PATH_PRIFIX + os.environ['NETWORK_DRIVE']+"/backup/"
            elif values== 'LOCAL_DRIVE':
                self.LIVERT_IMAGE_LOCAL_PATH = self.IMAGE_PATH_PRIFIX + os.environ['LOCAL_DRIVE']+"/instance/"
            else:
                self.LIVERT_IMAGE_BASE_PATH = self.IMAGE_PATH_PRIFIX+NETOWRK_DRIVE+ "/base/"
                self.LIVERT_IMAGE_SNAPSHOT_PATH = self.IMAGE_PATH_PRIFIX+NETOWRK_DRIVE +"/snapshot/"
                self.LIVERT_IMAGE_BACKUP_PATH = self.IMAGE_PATH_PRIFIX+NETOWRK_DRIVE +"/backup/"
                self.LIVERT_IMAGE_LOCAL_PATH = self.IMAGE_PATH_PRIFIX+LOCAL_DRIVE +"/instance/"

config = Config()
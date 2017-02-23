# -*- coding: utf-8 -*-
# 고정적으로 사용하는 값들을 한 곳에 모아두기 위해 만든 상수용 파이썬 파일
import ConfigParser
import os
import sys


class Config:
    DB_URL = 'mysql://gncloud:gncloud@db/gncloud?charset=utf8'
    SALT = 'Scheduler'
    MONITOR_CYCLE_SEC = 60
    INVOICE_VER = 1.0

    IMAGE_PATH_PREFIX = '/data/images/hyperv/'

    BACKUP_PATH = '' #C:/data/images/hyperv/backup
    LIVERT_IMAGE_BACKUP_PATH = '' #/home/images/kvm/backup/
    LIVERT_IMAGE_LOCAL_PATH = '' #/home/images/kvm/instance/


    def __init__(self):
        network_drive_letter = 'C'
        keys = os.environ.keys()
        for variable in keys:
            if variable == 'LIVERT_IMAGE_BACKUP_PATH':
                libvirt_backup_path = os.environ['LIVERT_IMAGE_BACKUP_PATH']
            elif variable == 'NETWORK_DRIVE_LETTER':
                network_drive_letter = os.environ['NETWORK_DRIVE_LETTER']

        self.BACKUP_PATH = network_drive_letter + ':' + self.IMAGE_PATH_PREFIX
# 전역 공통사용 객체이다.
config = Config()

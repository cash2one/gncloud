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

    HYPER_IMAGE_PATH_PREFIX = '/data/images/hyperv/'
    KVM_IMAGE_PATH_PREFIX = '/images/kvm'

    NETWORK_DRIVE = '/data/nas'
    LOCAL_DRIVE = '/data/local'

    MANAGER_PATH = ''
    BACKUP_PATH = '' #C:/data/images/hyperv/backup
    LIVERT_IMAGE_BACKUP_PATH = '' #/home/images/kvm/backup/
    LIVERT_IMAGE_LOCAL_PATH = '' #/home/images/kvm/instance/


    def __init__(self):
        local_drive_letter = 'C'
        network_drive_letter = 'C'
        network_drive = '/data/nas'
        local_drive = '/data/local'

        keys = os.environ.keys()
        for values in keys:
            if values == 'LOCAL_DRIVE_LETTER':
                local_drive_letter = os.environ['LOCAL_DRIVE_LETTER']
            elif values == 'NETWORK_DRIVE_LETTER':
                network_drive_letter = os.environ['NETWORK_DRIVE_LETTER']
            elif values == 'NETWORK_DRIVE':
                network_drive = os.environ['NETWORK_DRIVE']
            elif values== 'LOCAL_DRIVE':
                local_drive = os.environ['LOCAL_DRIVE']

        self.MANAGER_PATH = local_drive_letter + ':' + self.HYPER_IMAGE_PATH_PREFIX + '/manager/'
        self.BACKUP_PATH = network_drive_letter + ':' + self.HYPER_IMAGE_PATH_PREFIX + '/backup/'
        self.LIVERT_IMAGE_BACKUP_PATH = self.KVM_IMAGE_PATH_PREFIX+ network_drive +"/backup/"
        self.LIVERT_IMAGE_LOCAL_PATH = self.KVM_IMAGE_PATH_PREFIX+local_drive +"/instance/"

# 전역 공통사용 객체이다.
config = Config()

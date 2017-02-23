# -*- coding: utf-8 -*-
# 고정적으로 사용하는 값들을 한 곳에 모아두기 위해 만든 상수용 파이썬 파일

import os

class Config:
    DB_URL = 'mysql://gncloud:gncloud@db/gncloud?charset=utf8'
    SALT = 'Hyper-v'
    AGENT_PORT = 8180
    AGENT_REST_URI = 'powershell/execute'

    IMAGE_PATH_PREFIX = '/data/images/hyperv/'

    ######## working path ########
    LOCAL_PATH = ''
    NAS_PATH = ''
    MANAGER_PATH =''

    def __init__(self):
        local_drive_letter = 'C'
        network_drive_letter = 'C'
        keys = os.environ.keys()
        for variable in keys:
            if variable == 'LOCAL_DRIVE_LETTER':
                local_drive_letter = os.environ['LOCAL_DRIVE_LETTER']
            elif variable == 'NETWORK_DRIVE_LETTER':
                network_drive_letter = os.environ['NETWORK_DRIVE_LETTER']

        self.LOCAL_PATH = local_drive_letter + ':' + self.IMAGE_PATH_PREFIX
        self.MANAGER_PATH = local_drive_letter + ':' + self.IMAGE_PATH_PREFIX + 'manager'
        self.NAS_PATH = network_drive_letter + ':' + self.IMAGE_PATH_PREFIX


config = Config()

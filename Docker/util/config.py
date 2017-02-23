# -*- coding: utf-8 -*-
# 고정적으로 사용하는 값들을 한 곳에 모아두기 위해 만든 상수용 파이썬 파일

class Config:
    DB_URL = 'mysql://gncloud:gncloud@db/gncloud?charset=utf8'
    SALT = 'Docker'
    REPLICAS = 1
    RESTART_MAX_ATTEMPTS = 2

config = Config()

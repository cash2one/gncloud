# -*- coding: utf-8 -*-
# 고정적으로 사용하는 값들을 한 곳에 모아두기 위해 만든 상수용 파이썬 파일
import ConfigParser
import os
import sys


class Config:

    CONTROLLER_HOST = None
    CONTROLLER_PORT = None
    DB_URL = None
    SALT = None
    DOCKER_MANAGE_IPADDR = None
    DOCKER_MANAGER_SSH_ID = None
    DOCKER_MANAGER_SSH_PASSWD = None
    REPLICAS = None
    RESTART_MAX_ATTEMPTS = None

    def __init__(self, path="../conf/config.conf"):
        # 외부 Config파일을 환경변수로 설정시 이 파일을 이용한다.
        config_section = "DEFAULT"
        config_file = os.environ.get('APP_CONFIG')
        if config_file is None or config_file == '':
            config_file = os.path.join(os.path.dirname(__file__), path)

        if os.path.isfile(config_file):
            self.load(config_file, config_section)
        else:
            sys.exit('Cannot read config file : ' + config_file)

    def load(self, config_file, config_section="DEFAULT"):
        parser = ConfigParser.ConfigParser()
        result = parser.read(config_file)

        self.CONTROLLER_HOST = parser.get(config_section, "CONTROLLER_HOST")
        self.CONTROLLER_PORT = parser.get(config_section, "CONTROLLER_PORT")
        self.DB_URL = parser.get(config_section, "DB_URL")
        self.SALT = parser.get(config_section, "SALT")
        self.DOCKER_MANAGE_IPADDR = parser.get(config_section, "DOCKER_MANAGE_IPADDR")
        self.DOCKER_MANAGER_SSH_ID = parser.get(config_section, "DOCKER_MANAGER_SSH_ID")
        self.DOCKER_MANAGER_SSH_PASSWD = parser.get(config_section, "DOCKER_MANAGER_SSH_PASSWD")
        self.REPLICAS = parser.get(config_section, "REPLICAS")
        self.RESTART_MAX_ATTEMPTS = parser.get(config_section, "RESTART_MAX_ATTEMPTS")


# 전역 공통사용 객체이다.
config = Config()

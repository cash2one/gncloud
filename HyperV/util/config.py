# -*- coding: utf-8 -*-
# 고정적으로 사용하는 값들을 한 곳에 모아두기 위해 만든 상수용 파이썬 파일
import ConfigParser
import os
import sys


class Config:

    CONTROLLER_HOST = None
    CONTROLLER_PORT = None
    DB_URL = None
    AGENT_SERVER_IP = None
    AGENT_PORT = None
    AGENT_REST_URI = None
    SALT = None
    DNS_ADDRESS = None
    DNS_SUB_ADDRESS = None
    COMPUTER_NAME = None
    DISK_DRIVE = None
    MASK_BIT = None
    GATE_WAY = None
    HYPERV_PATH = None
    LOCAL_PATH = None
    NAS_PATH = None
    MANAGER_PATH = None
    BACKUP_PATH=None

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
        self.AGENT_SERVER_IP = parser.get(config_section, "AGENT_SERVER_IP")
        self.AGENT_PORT = parser.get(config_section, "AGENT_PORT")
        self.AGENT_REST_URI = parser.get(config_section, "AGENT_REST_URI")
        self.SALT = parser.get(config_section, "SALT")
        self.DNS_ADDRESS = parser.get(config_section, "DNS_ADDRESS")
        self.DNS_SUB_ADDRESS = parser.get(config_section, "DNS_SUB_ADDRESS")
        self.COMPUTER_NAME = parser.get(config_section, "COMPUTER_NAME")
        self.DISK_DRIVE = parser.get(config_section, "DISK_DRIVE")
        self.MASK_BIT = parser.get(config_section, "MASK_BIT")
        self.GATE_WAY = parser.get(config_section, "GATE_WAY")
        self.HYPERV_PATH = parser.get(config_section,"HYPERV_PATH")

        self.LOCAL_PATH = parser.get(config_section,"LOCAL_PATH")
        self.NAS_PATH = parser.get(config_section,"NAS_PATH")
        self.MANAGER_PATH = parser.get(config_section,"MANAGER_PATH")
        self.BACKUP_PATH = parser.get(config_section, "BACKUP_PATH")


# 전역 공통사용 객체이다.
config = Config()

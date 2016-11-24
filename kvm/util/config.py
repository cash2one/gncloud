# -*- coding: utf-8 -*-
# 고정적으로 사용하는 값들을 한 곳에 모아두기 위해 만든 상수용 파이썬 파일
import ConfigParser
import os
import sys

from kvm.util.logger import logger

class Config:

    LIBVIRT_REMOTE_URL = ""
    DB_URL = ""

    def __init__(self, path="../conf/config.conf"):
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
        logger.info("Default Conf file path : %s", os.path.abspath(config_file))
        result = parser.read(config_file)
        self.LIBVIRT_REMOTE_URL = parser.get(config_section, "LIBVIRT_REMOTE_URL")
        self.DB_URL = parser.get(config_section, "DB_URL")

# 전역 공통사용 객체이다.
local_custom_file = os.environ.get('CONFIG_FILE_PATH')
if local_custom_file is None:
    config = Config()
else:
    config = Config(local_custom_file)

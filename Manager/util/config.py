__author__ = 'NaDa'
# -*- coding: utf-8 -*-

import ConfigParser
import os

import sys
from Manager.util.logger import logger


class Config:

    DB_URL = ""
    IMAGE_PATH = ""
    RUN_STATUS = ""
    REMOVE_STATUS = ""
    DELETING_STATUS = ""
    STARTING_STATUS = ""
    ERROR_STATUS = ""
    SUSPEND_STATUS = ""
    KVM_HOST_POOL_IMAGE_PATH = ""
    HYPERV_HOST_POOL_IMAGE_PATH = ""
    NGINX_CONF_PATH = ""
    AGENT_PORT = ""

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
        self.DB_URL = parser.get(config_section, "DB_URL")
        self.IMAGE_PATH = parser.get(config_section, "IMAGE_PATH")
        self.RUN_STATUS = parser.get(config_section, "RUN_STATUS")
        self.REMOVE_STATUS = parser.get(config_section, "REMOVE_STATUS")
        self.STARTING_STATUS = parser.get(config_section, "STARTING_STATUS")
        self.DELETING_STATUS = parser.get(config_section, "DELETING_STATUS")
        self.ERROR_STATUS = parser.get(config_section, "ERROR_STATUS")
        self.SUSPEND_STATUS = parser.get(config_section, "SUSPEND_STATUS")
        self.KVM_HOST_POOL_IMAGE_PATH = parser.get(config_section, "KVM_HOST_POOL_IMAGE_PATH")
        self.HYPERV_HOST_POOL_IMAGE_PATH = parser.get(config_section, "HYPERV_HOST_POOL_IMAGE_PATH")
        self.NGINX_CONF_PATH = parser.get(config_section, "NGINX_CONF_PATH")
        self.AGENT_PORT = parser.get(config_section, "AGENT_PORT")

local_custom_file = os.environ.get('CONFIG_FILE_PATH')
if local_custom_file is None:
    config = Config()
else:
    config = Config(local_custom_file)

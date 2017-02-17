# -*- coding: utf-8 -*-
__author__ = 'yhk'
import os
import logging
import logging.handlers

from flask import request, session

logger = logging.getLogger(__name__)

# 로그 설정 (초기 테스트용)
formatter = logging.Formatter('[%(asctime)s %(levelname)s] (%(filename)s:%(lineno)s) %(message)s')

LOG_FILENAME = '../kvm.log'

fileHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=2000000, backupCount=7)
streamHandler = logging.StreamHandler()

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

logger.setLevel(logging.ERROR)


def logger_error(err):
        logger.error("%s -- %s", request.remote_addr, err)


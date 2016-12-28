# -*- coding: utf-8 -*-
__author__ = 'yhk'
import os
import logging
import logging.handlers


logger = logging.getLogger(__name__)
# 로그 설정 (초기 테스트용)
formatter = logging.Formatter('[%(asctime)s %(levelname)s] (%(filename)s:%(lineno)s) %(message)s')
# if not os.path.exists("./log/"):
#     os.makedirs("./log/", 777)
# logfile = open("./log/system.log", 'w')
# logfile.close()
#
# LOG_FILENAME = './log/system.log'
#
# fileHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=2000000, backupCount=7)
# fileHandler.setFormatter(formatter)
# logger.addHandler(fileHandler)

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

logger.setLevel(logging.DEBUG)



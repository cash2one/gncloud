# -*- coding: utf-8 -*-
__author__ = 'yhk'

import logging
from logging import handlers
from config import config
from Scheduler.util.config import config

log_file = ('%s/scheduler.log') % config.LOG_DIR

logger = logging.getLogger(__name__)
# 로그 설정 (초기 테스트용)
formatter = logging.Formatter('[%(asctime)s %(levelname)s] (%(filename)s:%(lineno)s) %(message)s')
file_handler = handlers.RotatingFileHandler(
    log_file,
    maxBytes= (1024 * 1024 * 512), # 512GB
    backupCount=3
)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)



# -*- coding: utf-8 -*-
import datetime
import time

from util.logger import logger

from util.config import config
from db.database import db_session
from db.models import GnSystemSetting
from service.service import Monitoring


class ScheduleController:
    def __init__(self):
        self.sql_session = db_session
        self.monitor_period = self.get_monitoring_period()
        self.quit = False
        self.monitor = Monitoring(self.sql_session, self.monitor_period)

    def run(self):
        self.monitor.run()
        while not self.quit:
            self.check_change_monitor_period()
            time.sleep(20)
        return

    def check_change_monitor_period(self):
        get_period = self.get_monitoring_period()
        if self.monitor_period != get_period:
            self.monitor_period = get_period
            self.monitor.shutdown()
            self.monitor.set_period(self.monitor_period)
            self.monitor.run()
            print 'change period'
        return

    def get_monitoring_period(self):
        period = config.MONITOR_CYCLE_SEC
        sql_session = self.sql_session

        try:
            get_val= sql_session.query(GnSystemSetting).all()
            for first in get_val:
                period = first.monitor_period
                break
            sql_session.commit()
        except Exception as message:
            logger.error(message)
        return period


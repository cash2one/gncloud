# -*- coding: utf-8 -*-
from util.config import config
from db.database import db_session
from db.models import GnSystemSetting
from service.monitor_service import Monitoring
from service.invoice_service import Invoice


class ScheduleController:
    def __init__(self):
        self.sql_session = db_session
        self.monitor_period = self.get_monitoring_period()
        self.quit = False
        self.monitor = Monitoring(self.sql_session, self.monitor_period)
        self.invoice = Invoice(self.sql_session)

    def run(self):
        self.invoice.run()
        self.monitor.run()

        #while not self.quit:
        #    self.check_change_monitor_period()
        #    time.sleep(20)

    def check_change_monitor_period(self):
        get_period = self.get_monitoring_period()
        if self.monitor_period != get_period:
            self.monitor_period = get_period
            self.monitor.shutdown()
            self.monitor.set_period(self.monitor_period)
            self.monitor.run()
            print 'change period'

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
            print (message)
        return period


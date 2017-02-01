# -*- coding: utf-8 -*-

from db.database import db_session
from service.monitor_service import Monitoring
from service.invoice_service import Invoice
from service.backup_service import Backup


class ScheduleController:
    def __init__(self):
        self.sql_session = db_session
        self.quit = False
        self.monitor = Monitoring(self.sql_session)
        self.invoice = Invoice(self.sql_session)
        self.backup = Backup(self.sql_session)

    def run(self):
        self.invoice.run()
        self.monitor.run()
        self.backup.run()
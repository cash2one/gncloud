# -*- coding: utf-8 -*-

from Scheduler.db.database import db_session
from Scheduler.service.monitor_service import Monitoring
from Scheduler.service.invoice_service import Invoice
from Scheduler.service.backup_service import Backup
from Scheduler.service.backup_delete_service import BackupDelete


class ScheduleController:
    def __init__(self):
        self.sql_session = db_session
        self.quit = False
        self.monitor = Monitoring(self.sql_session)
        self.invoice = Invoice(self.sql_session)
        self.backup = Backup(self.sql_session)
        self.backup_delete = BackupDelete(self.sql_session)

    def run(self):
        self.invoice.run()
        self.monitor.run()
        self.backup.run()
        self.backup_delete.run()
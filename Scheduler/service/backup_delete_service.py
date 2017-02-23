# -*- coding: utf-8 -*-
import datetime
from flask import jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from sqlalchemy import and_

from Scheduler.db.database import init_db, db_session
from Scheduler.db.models import GnSystemSetting, GnBackup, GnBackupHist
from Scheduler.util.config import config
from Scheduler.service.powershell import BackupPowerShell
from Scheduler.service.kvmshell import KvmShell


class BackupDelete:
    def __init__(self, db_session=None):
        self.sql_session = db_session
        self.scheduler = None

    def run(self):
        executors = {
            'default': {'type': 'threadpool', 'max_workers': 20},
            'processpool': ProcessPoolExecutor(max_workers=5)
        }
        job_defaults = { 'coalesce': False, 'max_instances': 3 }
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(executors=executors, job_defaults=job_defaults)
        self.scheduler.add_job(lambda : self.backup_delete(), trigger='cron', hour=0, minute=0)
        self.scheduler.start()

    def backup_delete(self):
        sql_session = self.sql_session
        if sql_session is None:
            init_db()
            sql_session = db_session
        try:
            settings = sql_session.query(GnSystemSetting).first()
            period = int(settings.backup_day)

            backup_delta = datetime.date.today() - datetime.timedelta(days=period)

            backup_hist_list = sql_session.query(GnBackupHist).all()
            for hist in backup_hist_list:
                backup_date = hist.backup_time.date()
                if backup_date <= backup_delta:
                    #delete backup history
                    if hist.vm_type == 'kvm' :
                        if self.kvm_delete_backup_hist(hist):
                            sql_session.query(GnBackupHist).filter(and_(GnBackupHist.vm_id == hist.vm_id,
                                                                        GnBackupHist.backup_time == hist.backup_time)).delete()
                            backup_org = sql_session.query(GnBackup).filter(and_(GnBackup.vm_id == hist.vm_id,
                                                                                 GnBackup.backup_time == hist.backup_time)).first()
                            if backup_org is not None:
                                sql_session.query(GnBackup).filter(GnBackup.vm_id == hist.vm_id).delete()
                        else:
                            print 'kvm_delete_backup_hist error'
                            sql_session.rollback()
                            return jsonify(status=False, message='failure backup delete')
                    elif hist.vm_type == 'hyperv':
                        if self.hyperv_delete_backup_hist(hist):
                            sql_session.query(GnBackupHist).filter(and_(GnBackupHist.vm_id == hist.vm_id,
                                                                        GnBackupHist.backup_time == hist.backup_time)).delete()
                            backup_org = sql_session.query(GnBackup).filter(and_(GnBackup.vm_id == hist.vm_id,
                                                                                 GnBackup.backup_time == hist.backup_time)).first()
                            if backup_org is not None:
                                sql_session.query(GnBackup).filter(GnBackup.vm_id == hist.vm_id).delete()
                        else:
                            print 'hyperv_delete_backup_hist error'
                            sql_session.rollback()
                            return jsonify(status=False, message='failure backup delete')
                    else:
                        continue

            sql_session.commit()
            return jsonify(status=True, message='success backup delete')
        except Exception as Message:
            print 'backup_delete %s : ' % Message
            sql_session.rollback()
            return jsonify(status=False, message='failure backup delete')

    def kvm_delete_backup_hist(self, hist):
        print ('kvm_backup_delete')
        kvm = KvmShell()
        return kvm.backup_delete_send(hist.host_ip, hist.filename, config.LIVERT_IMAGE_BACKUP_PATH)

    def hyperv_delete_backup_hist(self, hist):
        print ('hyper_backup_delete')
        ps_exec = 'powershell/execute'
        ps = BackupPowerShell(hist.host_ip, ps_exec)
        json_result = ps.delete_backup(hist.filename, config.BACKUP_PATH)
        # print json_result
        return True



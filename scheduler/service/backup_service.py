# -*- coding: utf-8 -*-
import sys
import datetime
from flask import jsonify
from db.models import *
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from db.models import GnHostMachines, GnVmMachines
from util.config import config
from service.powershell import BackupPowerShell
from service.kvmshell import KvmShell

reload(sys)
sys.setdefaultencoding('utf-8')

class Backup:
    def __init__(self, db_session=None):
        self.sql_session = db_session
        self.period = None
        self.scheduler = None

    def run(self):
        executors = {
            'default': {'type': 'threadpool', 'max_workers': 20},
            'processpool': ProcessPoolExecutor(max_workers=5)
        }
        job_defaults = { 'coalesce': False, 'max_instances': 3 }
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(executors=executors, job_defaults=job_defaults)
        self.scheduler.add_job(lambda : self.backup(), trigger='cron', hour=0, minute=10)
        self.scheduler.start()

    def backup(self):
        try:
            sql_session = self.sql_session
            backup_settings = sql_session.query(GnSystemSetting).first()
            if backup_settings.backup_schedule_type == 'W':
                week_day = 0;
                week_today = datetime.date.today().weekday()
                for week in backup_settings.backup_schedule_period:
                    # if week_day is 1, weekday is monday. 0 is sunday
                    if week == '1':
                        if week_day == week_today:
                            return self.week_backup_process()
                        else:
                            week_day += 1
                    elif week == '0':
                        week_day += 1
            elif backup_settings.backup_schedule_type == 'D':
                return self.day_backup_process(backup_settings.backup_schedule_period)

        except Exception as message:
            print(message)
            return jsonify(status=False, message='failure backup')

    def week_backup_process(self):
        try:
            sql_session = self.sql_session
            vm_list = sql_session.query(GnVmMachines).filter(GnVmMachines.status == 'Running').all()
            for vm_info in vm_list :
                if vm_info.backup_confirm == 'false' or vm_info.backup_confirm is None:
                    continue
                if vm_info.type == 'kvm':
                    self.kvm_backup(vm_info)
                elif vm_info.type == 'hyperv':
                    self.hyperv_backup(vm_info)
            sql_session.commit()
            return jsonify(status=True, message='success backup')
        except Exception as message:
            print(message)
            return jsonify(status=False, message='failure backup')

    def day_backup_process(self, period):
        try:
            sql_session = self.sql_session
            vm_list = sql_session.query(GnVmMachines).filter(GnVmMachines.status == 'Running').all()
            for vm_info in vm_list :
                if vm_info.backup_confirm == 'false' or vm_info.backup_confirm is None:
                    continue

                backup_delta = datetime.date.today() - datetime.timedelta(days=period)
                create_time = None
                latest_backup = sql_session.query(GnBackup).filter(GnBackup.vm_id == vm_info.id).first()
                if latest_backup is None:
                    create_time = vm_info.create_time.date()
                else:
                    create_time = latest_backup.backup_time.date()

                backup_condition = backup_delta - create_time

                if backup_condition.days == 0:
                    if vm_info.type == 'kvm':
                        self.kvm_backup(vm_info)
                    elif vm_info.type == 'hyperv':
                        self.hyperv_backup(vm_info)
                        print ('Hyper V backup')

            return jsonify(status=True, message='success backup')
        except Exception as message:
            print(message)
            return jsonify(status=False, message='failure backup')

    def kvm_backup(self, vm_info):
        sql_session = self.sql_session
        guest_info = sql_session.query(GnVmMachines).filter(GnVmMachines.id == vm_info.id).one()
        host_info = sql_session.query(GnHostMachines).filter(GnHostMachines.id == vm_info.host_id).one()
        try:
            # new_image_name = guest_info.internal_name + "_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            # 디스크 복사
            kvm = KvmShell()
            filename = kvm.backup_send(guest_info, host_info.ip, config.LIVERT_IMAGE_BACKUP_PATH)
            if filename == 'error':
                print 'backup error'
                sql_session.rollback()
                return jsonify(status=False, message='failure backup')

            create_time = filename.split('_')[1]
            filename = '%s%s' % (filename, '.img')
            date_create_time = datetime.datetime.strptime(create_time,'%Y%m%d%H%M%S')

            team = sql_session.query(GnTeam).filter(GnTeam.team_code == vm_info.team_code).one()
            user = sql_session.query(GnUsers).filter(GnUsers.user_id == vm_info.author_id).one()
            # insert into GN_BACKUP_HIST, update or insert into GN_BACKUP
            backup = sql_session.query(GnBackup).filter(GnBackup.vm_id == vm_info.id).first()
            if backup is None:
                backup_insert = GnBackup(vm_info.id, date_create_time, vm_info.team_code,
                                         vm_info.author_id, vm_info.type, guest_info.name,
                                         team.team_name, user.user_name)
                sql_session.add(backup_insert)
            else:
                backup.backup_time = date_create_time

            backup_hist = GnBackupHist(vm_info.id, filename, date_create_time, vm_info.type, host_info.ip)
            sql_session.add(backup_hist)
            sql_session.commit()

            return jsonify(status=True, message='success backup')
        except Exception as e:
            print 'kvm backup error : %s' % e
            sql_session.rollback()
            return jsonify(status=False, message='failure backup')

    def hyperv_backup(self, vm_info):
        # In case of vm status is running or suspend, it will be started backup
        ps_exec = 'powershell/execute'
        sql_session = self.sql_session
        host_machine = sql_session.query(GnHostMachines).filter(GnHostMachines.id == vm_info.host_id).first()
        host_ip= '%s:%d' % (host_machine.ip, host_machine.host_agent_port)
        ps = BackupPowerShell(host_ip, ps_exec)
        backup_info = ps.create_backup(vm_info.internal_id, config.MANAGER_PATH, config.BACKUP_PATH)
        try:
            if backup_info['Name'] is not None:
                filename = backup_info['Name']
                info = filename.split('_')
                ver=info[0]
                sub_ver=info[1]
                bit=info[2]
                org_vm_id=info[3]
                create_time=(info[4]).split('.')[0]
                date_create_time = datetime.datetime.strptime(create_time,'%Y%m%d%H%M%S')

                team = sql_session.query(GnTeam).filter(GnTeam.team_code == vm_info.team_code).one()
                user = sql_session.query(GnUsers).filter(GnUsers.user_id == vm_info.author_id).one()
                # insert into GN_BACKUP_HIST, update or insert into GN_BACKUP
                backup = sql_session.query(GnBackup).filter(GnBackup.vm_id == org_vm_id).first()
                if backup is None:
                    backup_insert = GnBackup(org_vm_id, date_create_time,
                                             vm_info.team_code, vm_info.author_id, vm_info.type, host_machine.name,
                                             team.team_name, user.user_name)
                    sql_session.add(backup_insert)
                else:
                    backup.backup_time = date_create_time

                backup_hist = GnBackupHist(org_vm_id, filename, date_create_time, vm_info.type, host_ip)
                sql_session.add(backup_hist)
                sql_session.commit()
                return jsonify(status=True, message='success backup')
        except Exception as e:
            print 'hyperv backup error : %s' % e
            sql_session.rollback()
            return jsonify(status=False, message='failure backup')
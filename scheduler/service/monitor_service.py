# -*- coding: utf-8 -*-
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from scheduler.db.models import *
from scheduler.db.models import GnCluster

__author__ = 'nhcho'

import requests


class Monitoring:
    def __init__(self, db_session=None, period=None):
        self.sql_session = db_session
        self.period = period
        self.scheduler = None

    def run(self):
        sql_session = self.sql_session

        executors = {
            'default': {'type': 'threadpool', 'max_workers': 20},
            'processpool': ProcessPoolExecutor(max_workers=5)
        }
        job_defaults = { 'coalesce': False, 'max_instances': 3 }
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(executors=executors, job_defaults=job_defaults)

        clusters = sql_session.query(GnCluster).filter(GnCluster.status=='Running').all()
        for cluster in clusters:
            if cluster.type == 'docker':
                docker_url = 'http://%s/monitor' % (str(cluster.ip))
                self.scheduler.add_job(lambda : self.docker_monitor(docker_url), trigger='interval', seconds=int(self.period))
            elif cluster.type == 'kvm':
                kvm_url = 'http://%s/monitor' % (str(cluster.ip))
                self.scheduler.add_job(lambda : self.kvm_monitor(kvm_url), trigger='interval', seconds=int(self.period))
            elif cluster.type == 'hyperv':
                hyperv_url = 'http://%s/monitor' % (str(cluster.ip))
                self.scheduler.add_job(lambda : self.hyperv_monitor(hyperv_url), trigger='interval', seconds=int(self.period))
            else:
                print 'type is error = %s' % cluster.type
        self.scheduler.start()
        sql_session.commit()

    def set_period(self, arg_period):
        self.period = arg_period

    def shutdown(self):
        self.scheduler.shutdown()

    def hyperv_monitor(self, hyperv_url):
        try:
            response = requests.get(hyperv_url, data=None)
        except Exception as message:
            print('hyperv:%s' % message)
            errno = message.args[0].args[1].errno
            self.alert_monitor('controller', 'hyperv', errno, message)
        print 'hyperv:%s:url=%s, period=%s:%s' % (datetime.datetime.now(), hyperv_url, self.period, response.json())

    def kvm_monitor(self, kvm_url):
        try:
            response = requests.get(kvm_url, data=None)
        except Exception as message:
            print('kvm:%s') % message
            errno = message.args[0].args[1].errno
            self.alert_monitor('controller', 'kvm', errno, message)
        print 'kvm   :%s:url=%s, period=%s:%s' % (datetime.datetime.now(), kvm_url, self.period, response.json())

    def docker_monitor(self, docker_url):
        try:
            response = requests.get(docker_url, data=None)
        except Exception as message:
            print('docker:%s') % message
            errno = message.args[0].args[1].errno
            self.alert_monitor('controller', 'docker', errno, message)
        print 'docker:%s:url=%s, period=%s:%s' % (datetime.datetime.now(), docker_url, self.period, response.json())

    def alert_monitor(self, type, sub_type, status, msg):
        sql_session = self.sql_session
        insert_alert = GnAlert(datetime.datetime.now().strftime('%Y%m%d%H%M%S'), type, sub_type, status, msg)
        sql_session.add(insert_alert)
        sql_session.commit()
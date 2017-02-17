# -*- coding: utf-8 -*-
from datetime import *
from flask import jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from Scheduler.db.models import *
from Scheduler.db.models import GnCluster
from Scheduler.util.config import config

__author__ = 'nhcho'

import requests


class Monitoring:
    def __init__(self, db_session=None, period=None):
        self.sql_session = db_session
        self.period = period
        self.scheduler = None

    def run(self):
        sql_session = self.sql_session
        self.period = self.get_monitoring_period()

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
                print 'type = %s is not scheduling' % cluster.type
        self.scheduler.start()
        sql_session.commit()

    def set_period(self, arg_period):
        self.period = arg_period

    def shutdown(self):
        self.scheduler.shutdown()

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

    def hyperv_monitor(self, hyperv_url):
        try:
            response = requests.get(hyperv_url, data=None)
            print 'hyperv:%s:url=%s, period=%s:%s' % (datetime.datetime.now(), hyperv_url, self.period, response.json())
        except Exception as message:
            print 'hyperv:%s' % message

    def kvm_monitor(self, kvm_url):
        try:
            response = requests.get(kvm_url, data=None)
            print 'kvm   :%s:url=%s, period=%s:%s' % (datetime.datetime.now(), kvm_url, self.period, response.json())
        except Exception as message:
            print 'kvm:%s' % message

    def docker_monitor(self, docker_url):
        try:
            response = requests.get(docker_url, data=None)
            print 'docker:%s:url=%s, period=%s:%s' % (datetime.datetime.now(), docker_url, self.period, response.json())
        except Exception as message:
            print 'docker:%s' % message


    def restart_monitor(self):
        self.shutdown()
        self.run()
        return jsonify(status=True, message='success changing monitoring')
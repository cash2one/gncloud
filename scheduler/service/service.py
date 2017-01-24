# -*- coding: utf-8 -*-
import datetime
from util.config import config
from db.models import *
from util.logger import logger
from apscheduler.scheduler import Scheduler
from db.models import GnCluster

__author__ = 'nhcho'

import json
import requests

class Monitoring:
    def __init__(self, db_session=None, period=None):
        self.sql_session = db_session
        self.period = period

    def run(self):
        sql_session = self.sql_session
        self.sched = Scheduler()

        clusters = sql_session.query(GnCluster).filter(GnCluster.status=='Running').all()
        for cluster in clusters:
            if cluster.type == 'docker':
                docker_url = 'http://%s:%s/monitor' % (str(cluster.ip), str(cluster.port))
                self.sched.add_interval_job(lambda : self.docker_monitor(docker_url), seconds=int(self.period))
            elif cluster.type == 'kvm':
                kvm_url = 'http://%s:%s/monitor' % (str(cluster.ip), str(cluster.port))
                self.sched.add_interval_job(lambda : self.kvm_monitor(kvm_url), seconds=int(self.period))
            elif cluster.type == 'hyperv':
                hyperv_url = 'http://%s:%s/monitor' % (str(cluster.ip), str(cluster.port))
                self.sched.add_interval_job(lambda : self.hyperv_monitor(hyperv_url), seconds=int(self.period))
            else:
                print 'type is error = %s' % cluster.type
        self.sched.start()
        sql_session.commit()

    def set_period(self, arg_period):
        self.period = arg_period

    def shutdown(self):
        self.sched.shutdown()

    def hyperv_monitor(self, hyperv_url):
        try:
            response = requests.get(hyperv_url, data=None)
        except Exception as message:
            logger.error(message)
        print 'hyperv:%s:url=%s, period=%s:%s' % (datetime.datetime.now(), hyperv_url, self.period, response.json())

    def kvm_monitor(self, kvm_url):
        try:
            response = requests.get(kvm_url, data=None)
        except Exception as message:
            logger.error(message)
        print 'kvm   :%s:url=%s, period=%s:%s' % (datetime.datetime.now(), kvm_url, self.period, response.json())
    def docker_monitor(self, docker_url):
        try:
            response = requests.get(docker_url, data=None)
        except Exception as message:
            logger.error(message)
        print 'cokder:%s:url=%s, period=%s:%s' % (datetime.datetime.now(), docker_url, self.period, response.json())



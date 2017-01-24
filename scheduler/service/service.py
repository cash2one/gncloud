# -*- coding: utf-8 -*-
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
            url = 'http://%s:%s/monitor' % (str(cluster.ip), str(cluster.port))
            print 'url=%s, type=%s. period=%s' % (url, cluster.type, self.period)
            if cluster.type == 'docker':
                self.sched.add_interval_job(lambda : self.docker_monitor(url), seconds=int(self.period))
            elif cluster.type == 'kvm':
                self.sched.add_interval_job(lambda : self.kvm_monitor(url), seconds=int(self.period))
            elif cluster.type == 'hyperv':
                self.sched.add_interval_job(lambda : self.hyperv_monitor(url), seconds=int(self.period))
            else:
                print 'type is error = %s' % cluster.type
        self.sched.start()
        sql_session.commit()

    def set_period(self, arg_period):
        self.period = arg_period

    def shutdown(self):
        self.sched.shutdown()

    def hyperv_monitor(self, url):
        try:
            response = requests.get(url, data=None)
        except Exception as message:
            logger.error(message)
        print 'hyperv:%s:%s' % (datetime.datetime.now(), response.json())

    def kvm_monitor(self, url):
        try:
            response = requests.get(url, data=None)
        except Exception as message:
            logger.error(message)
        print 'kvm   :%s:%s' % (datetime.datetime.now(), response.json())
    def docker_monitor(self, url):
        try:
            response = requests.get(url, data=None)
        except Exception as message:
            logger.error(message)
        print 'docker:%s:%s' % (datetime.datetime.now(), response.json())



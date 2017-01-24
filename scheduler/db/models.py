# -*- coding: utf-8 -*-
__author__ = 'nhcho'

import datetime
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Numeric, BigInteger

from db.database import Base


class GnCluster(Base):
    __tablename__ = "GN_CLUSTER"

    id = Column(String(8), primary_key=True, nullable=False, default='')
    name = Column(String(50), nullable=True, default='')
    ip = Column(String(20), nullable=True, default='')
    port = Column(String(5), nullable=True, default='')
    type = Column(String(10), nullable=True, default='')
    swarm_join = Column(String(200), nullable=True, default='')
    create_time = Column(DateTime, nullable=True, default='')
    status = Column(String(10), nullable=True, default='')


    def __init__(self, id, name=None, ip=None, port=None, type=None, swarm_join=None, create_time=None, status=None):
        self.id = id
        self.name = name
        self.ip = ip
        self.port = port
        self.type = type
        self.swarm_join = swarm_join
        self.create_time = create_time
        self.status = status

    def __repr__(self):
        return '<GnHostMachines %r>' % self.id

    def _json__(self):
        return ['id', 'name', 'ip', 'port', 'type', 'swarm_join', 'create_time', 'status']

class GnSystemSetting(Base):
    __tablename__ = 'GN_SYSTEM_SETTING'
    billing_type = Column(String(2), primary_key=True, nullable=False, default='')
    backup_schedule_type = Column(String(2), nullable=True, default='')
    backup_schedule_period = Column(String(13), nullable=True, default='')
    monitor_period = Column(String(4), nullable=True, default='')

    def __init__(self, billing_type=None, backup_schedule_type=None, backup_schedule_period=None, monitor_period=None):
        self.billing_type=billing_type
        self.backup_schedule_type=backup_schedule_type
        self.backup_schedule_period=backup_schedule_period
        self.monitor_period=monitor_period

    def __repr__(self):
        return '<GnSystemSetting %r>' % self.billing_type

    def __json__(self):
        return ['billing_type','backup_schedule_type','backup_schedule_period','monitor_period']

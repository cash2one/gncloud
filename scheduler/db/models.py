# -*- coding: utf-8 -*-
__author__ = 'nhcho'

import datetime
from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Numeric


class GnCluster(Base):
    __tablename__ = "GN_CLUSTER"

    id = Column(String(8), primary_key=True, nullable=False, default='')
    name = Column(String(50), nullable=True, default='')
    ip = Column(String(20), nullable=True, default='')
    type = Column(String(10), nullable=True, default='')
    swarm_join = Column(String(200), nullable=True, default='')
    create_time = Column(DateTime, nullable=True, default='')
    status = Column(String(10), nullable=True, default='')

    def __init__(self, id, name=None, ip=None, type=None, swarm_join=None, create_time=None, status=None):
        self.id = id
        self.name = name
        self.ip = ip
        self.type = type
        self.swarm_join = swarm_join
        self.create_time = create_time
        self.status = status

    def __repr__(self):
        return '<GnHostMachines %r>' % self.id

    def _json__(self):
        return ['id', 'name', 'ip', 'type', 'swarm_join', 'create_time', 'status']

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


class GnInstanceStatus(Base):
    __tablename__ = 'GN_INSTANCE_STATUS'
    vm_id = Column(String(8), primary_key=True, nullable=False, default='')
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    delete_time = Column(DateTime, nullable=True, default='')
    author_id = Column(String(50), nullable=False, default='')
    team_code = Column(String(10), nullable=True, default='')
    price = Column(Integer, nullable=True, default='')
    price_type = Column(String(2), nullable=True, default='')
    cpu = Column( nullable=True, default='')
    memory = Column( nullable=True, default='')
    disk = Column( nullable=True, default='')

    def __init__(self, vm_id, create_time, delete_time=None, author_id=None, team_code=None, price=None, price_type=None, cpu=None, memory=None, disk=None):
        self.vm_id = vm_id
        self.create_time = create_time
        self.delete_time = delete_time
        self.author_id = author_id
        self.team_code = team_code
        self.price = price
        self.price_type = price_type
        self.cpu = cpu
        self.memory = memory
        self.disk = disk

    def __repr__(self):
        return "<GnInstanceStatus(vm_id='%r', create_time='%r', delete_time='%r', author_id='%r', team_code='%r'," \
               "price='%r', price_type='%r', cpu='%r', memory='%r', disk='%r')>" \
               % (self.vm_id, self.create_time, self.delete_time, self.author_id, self.team_code, self.price,
                  self.price_type, self.cpu, self.memory, self.disk)


class GnInvoiceResult(Base):
    __tablename__='GN_INVOICE_RESULT'
    year = Column(String(4), primary_key=True, nullable=False, default='')
    month = Column(String(2), primary_key=True, nullable=False, default='')
    team_code = Column(String(10), primary_key=True, nullable=False, default='')
    invoice_data = Column(String(15000), nullable=True, default='')

    def __init__(self, year, month, team_code, invoice_data):
        self.year = year
        self.month = month
        self.team_code = team_code
        self.invoice_data = invoice_data

    def __repr__(self):
        return "<GnInvoiceResult(year='%r', month='%r', team_code='%r', invoice_data='%r')>" \
            % (self.year, self.month, self.team_code, self.invoice_data)

class GnUsers(Base):
    __tablename__ = 'GN_USERS'
    user_id = Column(String(50), primary_key=True, nullable=False)
    user_name = Column(String(20), primary_key=True, nullable=False)
    privilege = Column(String(4), nullable=True, default=None)
    dept_code = Column(String(3), nullable=True, default=None)
    tel = Column(String(15), nullable=True, default=None)
    email = Column(String(15), nullable=True, default=None)
    start_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    end_date = Column(DateTime, nullable=True, default=None)

    def __init__(self, user_id, user_name, privilege=None, dept_code=None, tel=None, email=None, start_date=datetime.datetime.now(), end_date=None):
        self.user_id = user_id
        self.user_name = user_name
        self.privilege = privilege
        self.dept_code = dept_code
        self.tel = tel
        self.email = email
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return "<GnUsers(user_id='%r', user_name='%r', privilege='%r', dept_code='%r', tel='%r', email='%r', start_date='%r', end_date='%r')>" \
               % (self.user_id, self.user_name, self.privilege, self.dept_code, self.tel, self.email, self.start_date, self.end_date)


class GnTeam(Base):
    __tablename__ = 'GN_TEAM'
    team_code = Column(String(10), primary_key=True, nullable=False)
    team_name = Column(String(50), nullable=True, default=None)
    author_id = Column(String(50), nullable=True, default=None)
    cpu_quota = Column(Integer, nullable=True, default=None)
    mem_quota = Column(Integer, nullable=True, default=None)
    disk_quota = Column(Integer, nullable=True, default=None)

    def __init__(self, team_code, team_name, author_id, cpu_quota, mem_quota, disk_quota):
        self.team_code = team_code
        self.team_name = team_name
        self.author_id = author_id
        self.cpu_quota = cpu_quota
        self.mem_quota = mem_quota
        self.disk_quota = disk_quota

    def __repr__(self):
        return "<GnTeam(team_code='%r', team_name='%r', author_id='%r', cpu_quota='%r'," \
               " mem_quota='%r', disk_quota='%r')>" \
               % (self.team_code, self.team_name, self.author_id, self.cpu_quota, self.mem_quota , self.disk_quota)


class GnMonitor(Base):
    __tablename__ = "GN_MONITOR"
    id = Column(String(8), primary_key=True, nullable=False)
    type = Column(String(6), primary_key=False, nullable=False)
    cpu_usage = Column(Numeric, primary_key=False, nullable=False)
    mem_usage = Column(Numeric, primary_key=False, nullable=False)
    disk_usage = Column(Numeric, primary_key=False, nullable=False)
    net_usage = Column(Numeric, primary_key=False, nullable=False)

    def __init__(self, id=id, type=type, cpu_usage=None, mem_usage=None, disk_usage=None, net_usage=None):
        self.id = id
        self.type = type
        self.cpu_usage = cpu_usage
        self.mem_usage = mem_usage
        self.disk_usage = disk_usage
        self.net_usage = net_usage

    def __repr__(self):
        return "<GnMonitor( id='%r', type='%r', cpu_usage='%r', mem_usage='%r', disk_usage='%r'," \
               "net_usage='%r')>" \
               % (self.id, self.type, self.cpu_usage, self.mem_usage, self.disk_usage, self.net_usage)

class GnAlert(Base):
    __tablename__ = "GN_ALERT"
    create_time = Column(DateTime, primary_key=True, nullable=False, default=datetime.datetime.now())
    type = Column(String(10), primary_key=True, nullable=False, default='')
    sub_type = Column(String(50), primary_key=True, nullable=False, default='')
    status = Column(String(15), nullable=True, default='')
    description = Column(String(15000), nullable=True, default='')

    def __init__(self, create_time, type, sub_type, status, description):
        self.create_time = create_time
        self.type = type
        self.sub_type = sub_type
        self.status = status
        self.description = description

    def __repr__(self):
        return "<GnAlert(create_time='%r', type='%r', sub_type='%r', status='%r', description='%r')>" \
            % (self.create_time, self.type, self.sub_type, self.status, self.description)


class GnVmMachines(Base):
    __tablename__ = 'GN_VM_MACHINES'
    id = Column(String(30), primary_key=True, nullable=False)
    name = Column(String(50), primary_key=True, nullable=False)
    type = Column(String(50), primary_key=False, nullable=False)
    internal_id = Column(String(100), primary_key=False, nullable=False)
    internal_name = Column(String(100), primary_key=False, nullable=False)
    cpu = Column(Integer, primary_key=False, nullable=False)
    memory = Column(Integer, primary_key=False, nullable=False)
    disk = Column(Integer, primary_key=False, nullable=False)
    ip = Column(String(20), primary_key=False, nullable=False)
    host_id = Column(String(8), primary_key=False, nullable=False)
    os = Column(String(10), primary_key=False, nullable=True)
    os_ver = Column(String(20), primary_key=False, nullable=True)
    os_sub_ver = Column(String(20), primary_key=False, nullable=True)
    os_bit = Column(String(2), primary_key=False, nullable=True)
    team_code = Column(String(50), primary_key=False, nullable=False)
    author_id = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now())
    start_time = Column(DateTime, default=datetime.datetime.now())
    stop_time = Column(DateTime, default=datetime.datetime.now())
    status = Column(String(10), primary_key=False, nullable=False)
    tag = Column(String(100), primary_key=False, nullable=False)
    image_id = Column(String(8), primary_key=False, nullable=False)
    ssh_key_id = Column(Integer, primary_key=False, nullable=False)
    hyperv_pass= Column(String(50), primary_key=False, nullable=False)
    backup_confirm =Column(String(5), primary_key=False, nullable=False)
    size_id = Column(String(8), primary_key=False, nullable=False)

    def __init__(self, id=id, name=None, type=None, internal_id=None, internal_name=None
                 , cpu=None, memory=None, disk=None, ip=None, host_id=None
                 , os=None, os_ver=None, os_sub_ver=None, os_bit=None, team_code=None
                 , author_id=None, status=None, tag=None, image_id=None, ssh_key_id=None, hyperv_pass=None, create_time=None, backup_confirm=None, size_id=None):
        self.id = id
        self.name = name
        self.type = type
        self.internal_id = internal_id
        self.internal_name = internal_name
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.ip = ip
        self.host_id = host_id
        self.os = os
        self.os_ver = os_ver
        self.os_sub_ver = os_sub_ver
        self.os_bit = os_bit
        self.team_code = team_code
        self.author_id = author_id
        self.status = status
        self.tag = tag
        self.image_id = image_id
        self.ssh_key_id = ssh_key_id
        self.hyperv_pass = hyperv_pass
        self.create_time = create_time
        self.backup_confirm = backup_confirm
        self.size_id = size_id
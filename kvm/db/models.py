# -*- coding: utf-8 -*-
import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship

from kvm.db.database import Base


class GnHostMachines(Base):
    __tablename__ = "GN_HOST_MACHINES"
    id = Column(String(100), primary_key=True, nullable=False)
    name = Column(String(100), primary_key=False, nullable=False)
    ip = Column(String(50), primary_key=False, nullable=False)
    type = Column(String(10), primary_key=False, nullable=False)
    cpu = Column(Integer, primary_key=False, nullable=False)
    mem = Column(Integer, primary_key=False, nullable=False)
    disk = Column(Integer, primary_key=False, nullable=False)
    host_agent_port = Column(Integer, primary_key=False, nullable=False)

    def __init__(self, id=None, type=None):
        self.id = id
        self.type = type

    def __repr__(self):
        return '<Id %r / Ip %r / Type %r>' \
               % (self.id, self.ip, self.type)

    def __json__(self):
        return ['host_id', 'host_ip', 'host_type']

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
    host_id = Column(String(8), ForeignKey('GN_HOST_MACHINES.id'))
    os = Column(String(10), primary_key=False, nullable=True)
    os_ver = Column(String(20), primary_key=False, nullable=True)
    os_sub_ver = Column(String(20), primary_key=False, nullable=True)
    os_bit = Column(String(2), primary_key=False, nullable=True)
    team_code = Column(String(50), primary_key=False, nullable=True)
    author_id = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now())
    start_time = Column(DateTime, default=datetime.datetime.now())
    stop_time = Column(DateTime, default=datetime.datetime.now())
    status = Column(String(10), primary_key=False, nullable=False)
    tag = Column(String(100), primary_key=False, nullable=False)
    image_id = Column(String(8), primary_key=False, nullable=False)
    ssh_key_id = Column(Integer, ForeignKey('GN_SSH_KEYS.id'))
    size_id = Column(String(8), primary_key=False, nullable=False)
    gnHostMachines = relationship('GnHostMachines')

    def __init__(self, id=id, name=None, type=None, internal_id=None, internal_name=None, cpu=None
                 , memory=None, disk=None, ip=None, host_id=None
                 , os=None, os_ver=None, os_sub_ver=None, os_bit=None, team_code=None
                 , author_id=None, status=None, tag=None, image_id=None, ssh_key_id=None, size_id=None):
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
        self.size_id = size_id


    def __repr__(self):
        return '<Id %r / Name %r / Type %r / Internal_id %r / Internal_name %r / Cpu %r / Memory %r / Disk %r / Ip %r / Status %r / Tag %r / Create_time %r / Host_id %r>' \
               % (self.id, self.name, self.type, self.internal_id, self.internal_name, self.cpu, self.memory, self.disk,
                  self.ip, self.status, self.tag, self.create_time, self.host_id)

    def __json__(self):
        return ['id', 'name', 'type', 'internal_id', 'internal_name', 'cpu', 'memory', 'disk', 'ip', 'status', 'tag', 'create_time', 'num', 'day1']


class GnVmImages(Base):
    __tablename__ = 'GN_VM_IMAGES'
    id = Column(String(100), primary_key=True, nullable=False)
    name = Column(String(50), primary_key=False, nullable=True)
    filename = Column(String(100), primary_key=False, nullable=True)
    type = Column(String(10), primary_key=False, nullable=False)
    sub_type = Column(String(10), primary_key=False, nullable=True)
    icon = Column(String(100), primary_key=False, nullable=True)
    os = Column(String(10), primary_key=False, nullable=True)
    os_ver = Column(String(20), primary_key=False, nullable=True)
    os_subver = Column(String(20), primary_key=False, nullable=True)
    os_bit = Column(String(2), primary_key=False, nullable=True)
    team_code = Column(String(10), primary_key=False, nullable=False)
    author_id = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now())
    ssh_id = Column(String(10), primary_key=False, nullable=True)
    status = Column(String(10), primary_key=False, nullable=True)
    pool_id = Column(String(8), primary_key=False, nullable=True)
    host_id = Column(Integer, ForeignKey('GN_HOST_MACHINES.id'))
    gnHostMachines = relationship('GnHostMachines')

    def __init__(self,id=None, name=None, filename=None, type=None
                 , sub_type=None, icon=None, os=None, os_ver=None, os_subver=None
                 , os_bit=None, team_code=None, author_id=None, ssh_id=None, status=None
                 , pool_id=None, host_id=None):
        self.id = id
        self.name = name
        self.filename = filename
        self.type = type
        self.sub_type = sub_type
        self.icon = icon
        self.os = os
        self.os_ver = os_ver
        self.os_subver = os_subver
        self.os_bit = os_bit
        self.team_code = team_code
        self.author_id = author_id
        self.ssh_id = ssh_id
        self.status = status
        self.pool_id = pool_id
        self.host_id = host_id



    def __repr__(self):
        return '<Id %r / Name %r / File_name %r / Type %r / Sub_type %r / Icon %r / Os %r / Os_ver %r / Os_subver %r / Team_code %r /Author_id %r / Create_time %r / Create_time %r / Ssh_id %r>' \
               % (self.id, self.name, self.file_name, self.type, self.sub_type
                  , self.icon, self.os, self.os_ver, self.os_subver, self.os_bit
                  , self.team_code, self.author_id, self.create_time, self.ssh_id)

    def __json__(self):
        return ['id', 'name', 'filename', 'type', 'sub_type'
            , 'icon', 'os', 'os_ver', 'os_subver', 'os_bit'
            , 'team_code', 'author_id', 'create_time', 'ssh_id', 'status']


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
        return '<ID %r / Type %r / Cpu_usage %r / Mem_usage %r / Disk_usage %r / Net_usage %r>' \
               % (self.id, self.type, self.cpu_usage, self.mem_usage, self.disk_usage, self.net_usage)

    def __json__(self):
        return ['id', 'type', 'cpu_usage', 'mem_usage', 'disk_usage', 'net_usage']


class GnMonitorHist(Base):
    __tablename__ = "GN_MONITOR_HIST"
    seq = Column(Integer, primary_key=True, nullable=False)
    id = Column(String(8), primary_key=False, nullable=False)
    type = Column(String(6), primary_key=False, nullable=False)
    cur_time = Column(DateTime, primary_key=False, nullable=False)
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
        return '<ID %r / Type %r / Cpu_usage %r / Mem_usage %r / Disk_usage %r / Net_usage %r>' \
               % (self.id, self.type, self.cpu_usage, self.mem_usage, self.disk_usage, self.net_usage)

    def __json__(self):
        return ['id', 'type', 'cpu_usage', 'mem_usage', 'disk_usage', 'net_usage']


class GnSshKeys(Base):
    __tablename__ = "GN_SSH_KEYS"
    id = Column(Integer, primary_key=True, nullable=False)
    team_code = Column(String(50), primary_key=False, nullable=False)
    name = Column(String(100), primary_key=False, nullable=False)
    fingerprint = Column(String(50), primary_key=False, nullable=False)
    path = Column(String(100), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, team_code=None, name=None, fingerprint=None, path=None):
        self.team_code = team_code
        self.name = name
        self.fingerprint = fingerprint
        self.path = path

    def __repr__(self):
        return '<Id %r /Team_code %r / name %r / fingerprint %r / path %r >' \
               % (self.id, self.team_code, self.name, self.fingerprint, self.path)

    def __json__(self):
        return ['id', 'name', 'fingerprint', 'create_time']

class GnId(Base):
    __tablename__ = "GN_ID"
    id = Column(String(8), primary_key=True, nullable=False)
    type = Column(String(20), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, id=None, type=None):
        self.id = id
        self.type = type

    def __repr__(self):
        return '<Id %r / Type %r >' \
               % (self.id, self.type)


class GnInstanceStatus(Base):
    __tablename__ = 'GN_INSTANCE_STATUS'
    vm_id = Column(String(8), primary_key=True, nullable=False, default='')
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    delete_time = Column(DateTime, nullable=True)
    author_id = Column(String(50), nullable=False, default='')
    team_code = Column(String(10), nullable=True, default='')
    price = Column(Integer, nullable=True, default='')
    price_type = Column(String(2), nullable=True, default='')
    cpu = Column( nullable=True, default='')
    memory = Column( nullable=True, default='')
    disk = Column( nullable=True, default='')

    def __init__(self, vm_id=None, create_time=None, delete_time=None, author_id=None, team_code=None
                 , price=None, price_type=None, cpu=None, memory=None, disk=None):
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
               "price='%r', price_type='%r', cpu='%r', memory='%r', disk='%r')" \
               % (self.vm_id, self.create_time, self.delete_time, self.author_id, self.team_code, self.price,
                  self.price_type, self.cpu, self.memory, self.disk)

class GnVmSize(Base):
    __tablename__ = 'GN_VM_SIZE'
    id = Column(String(8), primary_key=True, nullable=False)
    cpu = Column(Numeric, primary_key=False, nullable=False)
    mem = Column(Numeric, primary_key=False, nullable=False)
    disk = Column(Numeric, primary_key=False, nullable=False)
    hour_price = Column(Integer, primary_key=False, nullable=False)
    day_price= Column(Integer, primary_key=False, nullable=False)

    def __init__(self,id=id, cpu=None, mem=None, disk=None, hour_price=None, day_price=None):
        self.id=id
        self.cpu = cpu
        self.mem = mem
        self.disk = disk
        self.hour_price = hour_price
        self.day_price = day_price

    def __repr__(self):
        return '< ID %r / Cpu %r / Mem %r / Disk %r / Hour_price %r / day_price %r/>' \
               %(self.id, self.cpu, self.mem, self.disk, self.hour_price, self.day_price)

    def __json__(self):
        return ['id', 'cpu', 'mem', 'disk', 'hour_price', 'day_price']


class GnSystemSetting(Base):
    __tablename__='GN_SYSTEM_SETTING'
    billing_type = Column(String(2), primary_key=True, nullable=False, default='')
    backup_schedule_type = Column(String(2), nullable=True, default='')
    backup_schedule_period = Column(String(13), nullable=True, default='')
    monitor_period = Column(String(4), nullable=True, default='')

    def __init__(self, billing_type = billing_type, backup_schedule_type =None, backup_schedule_period= None, monitor_period=None):
        self.billing_type = billing_type
        self.backup_schedule_type = backup_schedule_type
        self.backup_schedule_period = backup_schedule_period
        self.monitor_period = monitor_period

    def __repr__(self):
        return '<Billing_type %r / Backup_schedule_type %r / Backup_schedule_period %r / Monitor_period %r/ >' \
               %(self.billing_type, self.backup_schedule_type, self.backup_schedule_period, self.monitor_period)

    def __json__(self):
        return ['billing_type', 'backup_schedule_type', 'backup_schedule_period', 'monitor_period']

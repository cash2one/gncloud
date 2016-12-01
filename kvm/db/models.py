# -*- coding: utf-8 -*-
import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.orm import relationship, backref
from kvm.db.database import Base


class GnHostMachines(Base):
    __tablename__ = "GN_HOST_MACHINES"
    id = Column(Integer, primary_key=True, nullable=False)
    ip = Column(String(20), primary_key=False, nullable=False)
    type = Column(String(50), primary_key=False, nullable=False)

    def __init__(self, ip=None, type=None):
        self.ip = ip
        self.type = type

    def __repr__(self):
        return '<ID %r / Ip %r / Type %r>' \
               % (self.id, self.ip, self.type)

    def __json__(self):
        return ['id', 'ip', 'type']

class GnVmMachines(Base):
    __tablename__ = 'GN_VM_MACHINES'
    id = Column(String(30), primary_key=True, nullable=False)
    name = Column(String(50), primary_key=True, nullable=False)
    type = Column(String(50), primary_key=False, nullable=False)
    cpu = Column(Integer, primary_key=False, nullable=False)
    memory = Column(Integer, primary_key=False, nullable=False)
    hdd = Column(Integer, primary_key=False, nullable=False)
    ip = Column(String(20), primary_key=False, nullable=False)
    host_id = Column(Integer, ForeignKey('GN_HOST_MACHINES.id'))
    os = Column(String(10), primary_key=False, nullable=True)
    os_ver = Column(String(20), primary_key=False, nullable=True)
    os_sub_ver = Column(String(20), primary_key=False, nullable=True)
    os_bit = Column(String(2), primary_key=False, nullable=True)
    author = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.utcnow)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    stop_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(10), primary_key=False, nullable=False)
    gnHostMachines = relationship('GnHostMachines')

    def __init__(self, id=id, name=None, type=None, cpu=None, memory=None, hdd=None, ip=None, host_id=None, os=None,
                 os_ver=None, os_sub_ver=None, os_bit=None, author=None, status=None):
        self.id = id
        self.name = name
        self.type = type
        self.cpu = cpu
        self.memory = memory
        self.hdd = hdd
        self.ip = ip
        self.host_id = host_id
        self.os = os
        self.os_ver = os_ver
        self.os_sub_ver = os_sub_ver
        self.os_bit = os_bit
        self.author = author
        self.status = status


    def __repr__(self):
        return '<ID %r / Name %r / Type %r / Cpu %r / Memory %r / Hdd %r / Ip %r / Status %r>' \
               % (self.id, self.name, self.type, self.cpu, self.memory, self.hdd, self.ip, self.status)

    def __json__(self):
        return ['id', 'name', 'type', 'cpu', 'memory', 'hdd', 'ip', 'status']


class GnVmImages(Base):
    __tablename__ = 'GN_VM_IMAGES'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), primary_key=False, nullable=False)
    type = Column(String(20), primary_key=False, nullable=False)
    reg_dt = Column(DateTime, primary_key=False, nullable=False)

    def __init__(self, name=None, type=None, reg_dt=None):
        self.name = name
        self.type = type
        self.reg_dt = reg_dt


    def __repr__(self):
        return '<ID %r / Name %r / Type %r / Reg_dt %r>' \
               % (self.id, self.name, self.type, self.reg_dt)

    def __json__(self):
        return ['id', 'name', 'type', 'reg_dt']


class GnVmMonitor(Base):
    __tablename__ = "GN_VM_MONITOR"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(20), primary_key=False, nullable=False)
    cpu_use = Column(Numeric, primary_key=False, nullable=False)
    mem_use = Column(Numeric, primary_key=False, nullable=False)

    def __init__(self, name=None, cpu_use=None, mem_use=None):
        self.name = name
        self.cpu_use = cpu_use
        self.mem_use = mem_use

    def __repr__(self):
        return '<ID %r / Name %r / Cpu_use %r / Mem_use %r>' \
               % (self.id, self.name, self.cpu_use, self.mem_use)

    def __json__(self):
        return ['id', 'name', 'cpu_use', 'mem_use']

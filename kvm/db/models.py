# -*- coding: utf-8 -*-
import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, backref
from kvm.db.database import Base


class GnVmMachines(Base):
    __tablename__ = 'GN_VM_MACHINES'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), primary_key=False, nullable=False)
    type = Column(String(50), primary_key=False, nullable=False)
    cpu = Column(Integer, primary_key=False, nullable=False)
    memory = Column(Integer, primary_key=False, nullable=False)
    hdd = Column(Integer, primary_key=False, nullable=False)
    ip = Column(String(20), primary_key=False, nullable=False)
    host_id = Column(Integer, primary_key=False, nullable=False)
    os = Column(String(10), primary_key=False, nullable=True)
    os_ver = Column(String(20), primary_key=False, nullable=True)
    os_sub_ver = Column(String(20), primary_key=False, nullable=True)
    bit = Column(String(2), primary_key=False, nullable=True)
    author = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.utcnow)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    stop_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(10), primary_key=False, nullable=False)

    def __init__(self, name=None, type=None, cpu=None, memory=None, hdd=None, ip=None, host_id=None, os=None,
                 os_ver=None, os_sub_ver=None, bit=None, author=None, status=None):
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
        self.bit = bit
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

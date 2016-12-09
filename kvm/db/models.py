# -*- coding: utf-8 -*-
import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.orm import relationship, backref
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
    max_cpu = Column(Integer, primary_key=False, nullable=False)
    max_mem = Column(Integer, primary_key=False, nullable=False)
    max_disk = Column(Integer, primary_key=False, nullable=False)
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
    host_id = Column(Integer, ForeignKey('GN_HOST_MACHINES.id'))
    os = Column(String(10), primary_key=False, nullable=True)
    os_ver = Column(String(20), primary_key=False, nullable=True)
    os_sub_ver = Column(String(20), primary_key=False, nullable=True)
    os_bit = Column(String(2), primary_key=False, nullable=True)
    team_code = Column(String(50), primary_key=False, nullable=True)
    author_id = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.utcnow)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    stop_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(10), primary_key=False, nullable=False)
    gnHostMachines = relationship('GnHostMachines')

    def __init__(self, id=id, name=None, type=None, internal_id=None, internal_name=None, cpu=None
                 , memory=None, disk=None, ip=None, host_id=None
                 , os=None, os_ver=None, os_sub_ver=None, os_bit=None, team_code=None
                 , author_id=None, status=None):
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
        self.team_ = team_code
        self.author_id = author_id
        self.status = status


    def __repr__(self):
        return '<Id %r / Name %r / Type %r / Internal_id %r / Internal_name %r / Cpu %r / Memory %r / Disk %r / Ip %r / Status %r>' \
               % (self.id, self.name, self.type, self.internal_id, self.internal_name, self.cpu, self.memory, self.disk,
                  self.ip, self.status)

    def __json__(self):
        return ['id', 'name', 'type', 'internal_id', 'internal_name', 'cpu', 'memory', 'disk', 'ip', 'status']


class GnVmImages(Base):
    __tablename__ = 'GN_VM_IMAGES'
    id = Column(String(100), primary_key=True, nullable=False)
    name = Column(String(50), primary_key=False, nullable=False)
    filename = Column(String(100), primary_key=False, nullable=False)
    type = Column(String(10), primary_key=False, nullable=False)
    sub_type = Column(String(10), primary_key=False, nullable=False)
    icon = Column(String(100), primary_key=False, nullable=False)
    os = Column(String(10), primary_key=False, nullable=False)
    os_ver = Column(String(20), primary_key=False, nullable=False)
    os_subver = Column(String(20), primary_key=False, nullable=False)
    os_bit = Column(String(2), primary_key=False, nullable=False)
    team_code = Column(String(10), primary_key=False, nullable=False)
    author_id = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, id=None, name=None, filename=None, type=None
                 , sub_type=None, icon=None, os=None, os_ver=None, os_subver=None
                 , os_bit=None, team_code=None, author_id=None):
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


    def __repr__(self):
        return '<Id %r / Name %r / File_name %r / Type %r / Sub_type %r / Icon %r / Os %r / Os_ver %r / Os_subver %r / Team_code %r /Author_id %r / Create_time %r>' \
               % (self.id, self.name, self.file_name, self.type, self.sub_type
                  , self.icon, self.os, self.os_ver, self.os_subver, self.os_bit
                  , self.team_code, self.author_id, self.create_time)

    def __json__(self):
        return ['id', 'name', 'filename', 'type', 'sub_type'
            , 'icon', 'os', 'os_ver', 'os_subver', 'os_bit'
            , 'team_code', 'author_id', 'create_time']


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


class GnSshKeys(Base):
    __tablename__ = "GN_SSH_KEYS"
    id = Column(Integer, primary_key=True, nullable=False)
    team_code = Column(String(50), primary_key=False, nullable=False)
    name = Column(String(100), primary_key=False, nullable=False)
    fingerprint = Column(String(50), primary_key=False, nullable=False)
    path = Column(String(100), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.utcnow)

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
    create_time = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, id=None, type=None):
        self.id = id
        self.type = type

    def __repr__(self):
        return '<Id %r / Type %r >' \
               % (self.id, self.type)

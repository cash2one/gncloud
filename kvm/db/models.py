# -*- coding: utf-8 -*-
import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.orm import relationship, backref
from kvm.db.database import Base


class GnHostMachines(Base):
    __tablename__ = "GN_HOST_MACHINES"
    host_id = Column(String(100), primary_key=True, nullable=False)
    host_name = Column(String(100), primary_key=False, nullable=False)
    host_ip = Column(String(50), primary_key=False, nullable=False)
    host_type = Column(String(10), primary_key=False, nullable=False)
    cpu = Column(Integer, primary_key=False, nullable=False)
    mem = Column(Integer, primary_key=False, nullable=False)
    disk = Column(Integer, primary_key=False, nullable=False)
    max_cpu = Column(Integer, primary_key=False, nullable=False)
    max_mem = Column(Integer, primary_key=False, nullable=False)
    max_disk = Column(Integer, primary_key=False, nullable=False)
    host_agent_port = Column(Integer, primary_key=False, nullable=False)

    def __init__(self, host_id=None, host_type=None):
        self.host_id = host_id
        self.host_type = host_type

    def __repr__(self):
        return '<Host_id %r / Host_ip %r / host_type %r>' \
               % (self.host_id, self.host_ip, self.host_type)

    def __json__(self):
        return ['host_id', 'host_ip', 'host_type']

class GnVmMachines(Base):
    __tablename__ = 'GN_VM_MACHINES'
    vm_id = Column(String(30), primary_key=True, nullable=False)
    vm_name = Column(String(50), primary_key=True, nullable=False)
    vm_type = Column(String(50), primary_key=False, nullable=False)
    cpu = Column(Integer, primary_key=False, nullable=False)
    memory = Column(Integer, primary_key=False, nullable=False)
    disk = Column(Integer, primary_key=False, nullable=False)
    ip = Column(String(20), primary_key=False, nullable=False)
    host_id = Column(Integer, ForeignKey('GN_HOST_MACHINES.host_id'))
    os = Column(String(10), primary_key=False, nullable=True)
    os_ver = Column(String(20), primary_key=False, nullable=True)
    os_sub_ver = Column(String(20), primary_key=False, nullable=True)
    os_bit = Column(String(2), primary_key=False, nullable=True)
    author_id = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.utcnow)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    stop_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(10), primary_key=False, nullable=False)
    gnHostMachines = relationship('GnHostMachines')

    def __init__(self, vm_id=vm_id, vm_name=None, vm_type=None, cpu=None
                 , memory=None, disk=None, ip=None, host_id=None
                 , os=None, os_ver=None, os_sub_ver=None, os_bit=None
                 , author_id=None, status=None):
        self.vm_id = vm_id
        self.vm_name = vm_name
        self.vm_type = vm_type
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.ip = ip
        self.host_id = host_id
        self.os = os
        self.os_ver = os_ver
        self.os_sub_ver = os_sub_ver
        self.os_bit = os_bit
        self.author_id = author_id
        self.status = status


    def __repr__(self):
        return '<Vm_id %r / Vm_name %r / Vm_type %r / Cpu %r / Memory %r / Disk %r / Ip %r / Status %r>' \
               % (self.vm_id, self.vm_name, self.vm_type, self.cpu, self.memory, self.disk, self.ip, self.status)

    def __json__(self):
        return ['vm_id', 'vm_name', 'vm_type', 'cpu', 'memory', 'disk', 'ip', 'status']


class GnVmImages(Base):
    __tablename__ = 'GN_VM_IMAGES'
    image_id = Column(String(100), primary_key=True, nullable=False)
    image_name = Column(String(50), primary_key=False, nullable=False)
    image_filename = Column(String(100), primary_key=False, nullable=False)
    image_type = Column(String(10), primary_key=False, nullable=False)
    image_sub_type = Column(String(10), primary_key=False, nullable=False)
    image_icon = Column(String(100), primary_key=False, nullable=False)
    os = Column(String(10), primary_key=False, nullable=False)
    os_ver = Column(String(20), primary_key=False, nullable=False)
    os_subver = Column(String(20), primary_key=False, nullable=False)
    os_bit = Column(String(2), primary_key=False, nullable=False)
    author_id = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, image_id=None, image_name=None, image_filename=None, image_type=None
                 , image_sub_type=None, image_icon=None, os=None, os_ver=None, os_subver=None
                 , os_bit=None, autor_id=None):
        self.image_id = image_id
        self.image_name = image_name
        self.image_filename = image_filename
        self.image_type = image_type
        self.image_sub_type = image_sub_type
        self.image_icon = image_icon
        self.os = os
        self.os_ver = os_ver
        self.os_subver = os_subver
        self.os_bit = os_bit
        self.author_id = autor_id


    def __repr__(self):
        return '<Image_id %r / Image_name %r / Image_file_name %r / Image_type %r / Image_sub_type %r >' \
               '<Image_icon %r / Os %r / Os_ver %r / Os_subver %r />' \
               '<Author_id %r / Create_time %r>' \
               % (self.image_id, self.image_name, self.image_file_name, self.image_type, self.image_sub_type
                  , self.image_icon, self.os, self.os_ver, self.os_subver, self.os_bit
                  , self.author_id, self.create_time)

    def __json__(self):
        return ['image_id', 'image_name', 'image_filename', 'image_type', 'image_sub_type'
            , 'image_icon', 'os', 'os_ver', 'os_subver', 'os_bit'
            , 'author_id', 'create_time']


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
    team_name = Column(String(50), primary_key=False, nullable=False)
    key_name = Column(String(100), primary_key=False, nullable=False)
    key_fingerprint = Column(String(50), primary_key=False, nullable=False)
    key_content = Column(Text, primary_key=False, nullable=False)

    def __init__(self, team_name=None, key_name=None, key_fingerprint=None, key_content=None):
        self.team_name = team_name
        self.key_name = key_name
        self.key_fingerprint = key_fingerprint
        self.key_content = key_content

    def __repr__(self):
        return '<Team_name %r / Key_name %r / Key_fingerprint %r / Key_content %r>' \
               % (self.team_name, self.key_name, self.key_fingerprint, self.key_content)

    def __json__(self):
        return ['team_name', 'key_name', 'key_fingerprint', 'key_content']

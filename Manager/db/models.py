__author__ = 'NaDa'
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from Manager.db.database import Base
import datetime

class GnVmMachines(Base):
    __tablename__ = 'GN_VM_MACHINES'
    vm_id = Column(String(30), primary_key=True, nullable=False)
    vm_name = Column(String(50), primary_key=True, nullable=False)
    vm_type = Column(String(50), primary_key=False, nullable=False)
    cpu = Column(Integer, primary_key=False, nullable=False)
    memory = Column(Integer, primary_key=False, nullable=False)
    disk = Column(Integer, primary_key=False, nullable=False)
    ip = Column(String(20), primary_key=False, nullable=False)
    host_id = Column(Integer, ForeignKey('GN_HOST_MACHINES.id'))
    os = Column(String(10), primary_key=False, nullable=True)
    os_ver = Column(String(20), primary_key=False, nullable=True)
    os_sub_ver = Column(String(20), primary_key=False, nullable=True)
    os_bit = Column(String(2), primary_key=False, nullable=True)
    author_id = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.utcnow)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    stop_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(10), primary_key=False, nullable=False)


    def __init__(self, id=vm_id, name=None, type=None, cpu=None, memory=None, disk=None, ip=None, host_id=None, os=None, os_ver=None, os_sub_ver=None, os_bit=None, author=None, status=None):

        self.vm_id = id
        self.vm_name = name
        self.vm_type = type
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.ip = ip
        self.host_id = host_id
        self.os = os
        self.os_ver = os_ver
        self.os_sub_ver = os_sub_ver
        self.os_bit = os_bit
        self.author_id = author
        self.status = status


    def __repr__(self):
        return '<ID %r / Name %r / Type %r / Cpu %r / Memory %r / Disk %r / Ip %r / Status %r>' \
               % (self.vm_id, self.vm_name, self.vm_type, self.cpu, self.memory, self.disk, self.ip, self.status)

    def __json__(self):
        return ['vm_id', 'vm_name', 'vm_type', 'cpu', 'memory', 'disk', 'ip', 'status']


class GnUser(Base):
    __tablename__ = 'GN_USERS'
    user_id = Column(String(50), primary_key= True, nullable=False)
    password = Column(String(50), primary_key= False, nullable= False)

    def __init__(self, id = user_id, password= None):

        self.user_id = id
        self.password= password

    def __repr__(self):
        return '<ID %r / Password %r>'\
                %(self.user_id, self.password)

    def __json__(self):
        return ['user_id', 'password']

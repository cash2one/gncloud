# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, backref
from kvm.db.database import Base



class GnGuestMachines(Base):
    __tablename__ = 'GN_GUEST_MACHINES'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), primary_key=False, nullable=False)
    type = Column(String(50), primary_key=False, nullable=False)
    cpu = Column(Integer, primary_key=False, nullable=False)
    memory = Column(Integer, primary_key=False, nullable=False)
    hdd = Column(Integer, primary_key=False, nullable=False)
    ip = Column(String(20), primary_key=False, nullable=False)
    status = Column(String(20), primary_key=False, nullable=False)

    def __init__(self, name=None, type=None, cpu=None, memory=None, hdd=None, ip=None, status=None):
        self.name = name
        self.type = type
        self.cpu = cpu
        self.memory = memory
        self.hdd = hdd
        self.ip = ip


    def __repr__(self):
        return '<ID %r / Name %r / Type %r / Cpu %r / Memory %r / Hdd %r / Ip %r / Status %r>' \
               % (self.id, self.name, self.type, self.cpu, self.memory, self.hdd, self.ip, self.status)

    def __json__(self):
        return ['id', 'name', 'type', 'cpu', 'memory', 'hdd', 'ip', 'status']


class GnGuestImages(Base):
    __tablename__ = 'GN_GUEST_IMAGES'
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

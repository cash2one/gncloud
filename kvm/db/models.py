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

    def __init__(self, name=None, type=None , cpu=None, memory=None, hdd=None, ip =None):
        self.name = name
        self.type = type
        self.cpu = cpu
        self.memory = memory
        self.hdd = hdd
        self.ip = ip


    def __repr__(self):
        return '<ID %r / Name %r / Type %r / Cpu %r / Memory %r / Hdd %r / Ip %r>' \
               % (self.id, self.name, self.type, self.cpu, self.memory, self.hdd, self.ip)

    def __json__(self):
        return ['id', 'name', 'type', 'cpu', 'memory', 'hdd', 'ip']


class GnGuestImages(Base):
    __tablename__ = 'GN_GUEST_IMAGES'
    name = Column(String(50), primary_key=True, nullable=False)
    type = Column(String(10), primary_key=False, nullable=False)
    source_dist = Column(String(100), primary_key=False, nullable=True)
    reg_dt = Column(DateTime, primary_key=False, nullable=False)
    os = Column(String(20), primary_key=False, nullable=True)

    def __init__(self, name=None, type=None , source_dist=None, reg_dt=None, os=None):
        self.name = name
        self.type = type
        self.source_dist = source_dist
        self.reg_dt = reg_dt
        self.os = os


    def __repr__(self):
        return '<Name %r / Type %r / Source_dist %r / Reg_dt %r / Os %r>' \
               % (self.name, self.type, self.source_dist, self.reg_dt, self.os)

    def __json__(self):
        return ['name', 'type', 'source_dist', 'reg_dt', 'os']
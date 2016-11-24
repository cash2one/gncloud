# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, backref
from kvm.db.database import Base



class GnGuestMachine(Base):
    __tablename__ = 'GN_GUEST_MACHINE'
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), primary_key=False, nullable=False)
    kind = Column(String(10), primary_key=False, nullable=False)
    cpu = Column(Integer, primary_key=False, nullable=False)
    memory = Column(Integer, primary_key=False, nullable=False)
    hdd = Column(Integer, primary_key=False, nullable=False)
    ip = Column(String(20), primary_key=False, nullable=False)

    def __init__(self, name=None, kind=None , cpu=None, memory=None, hdd=None, ip =None):
        self.name = name
        self.kind = kind
        self.cpu = cpu
        self.memory = memory
        self.hdd = hdd
        self.ip = ip


    def __repr__(self):
        return '<ID %r / Name %r / Kind %r / Cpu %r / Memory %r / Hdd %r / Ip %r>' \
               % (self.id, self.name, self.kind, self.cpu, self.memory, self.hdd, self.ip)

    def __json__(self):
        return ['id', 'name', 'kind', 'cpu', 'memory', 'hdd', 'ip']
# -*- coding: utf-8 -*-
__author__ = 'gncloud'

import json
import datetime
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, backref
from db.database import Base


class GnContainers(Base):
    __tablename__ = 'GN_CONTAINERS'
    id = Column(String(8), primary_key=True, nullable=False, default="")
    name = Column(String(50), nullable=True, default="")
    tag = Column(String(100), nullable=True, default="")
    internal_id = Column(String(100), nullable=True, default="")
    internal_name = Column(String(100), nullable=True, default="")
    host_id = Column(String(100), nullable=False, default="")
    cpu = Column(Integer, nullable=True, default="")
    memory = Column(Integer, nullable=True, default="")
    disk = Column(Integer, nullable=True, default="")
    team_code = Column(String(10), nullable=True, default="")
    author_id = Column(String(50), nullable=False, default="")
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    start_time = Column(DateTime, nullable=True, default=datetime.datetime.now())
    stop_time = Column(DateTime, nullable=True, default=datetime.datetime.now())
    status = Column(String(10), nullable=True, default="")

    def __init__(
        self,
        id, name, tag, internal_id, internal_name,
        host_id, cpu, memory, disk, team_code,
        author_id, create_time, start_time=create_time, stop_time=create_time, status=""
    ):
        self.id = id
        self.name = name
        self.tag = tag
        self.internal_id = internal_id
        self.internal_name = internal_name
        self.host_id = host_id
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.team_code = team_code
        self.author_id = author_id
        self.create_time = create_time
        self.start_time = start_time
        self.stop_time = stop_time
        self.status = status

    def __repr__(self):
        return "<GnContainers(id=%r, name=%r, tag=%r, internal_id=%r, internal_name=%r, host_id=%r, cpu=%r, memory=%r, disk=%r, team_code=%r, author_id=%r, create_time=%r, start_time=%r, stop_time=%r, status=%r, )>" \
               % (self.id, self.name, self.tag, self.internal_id, self.internal_name, self.host_id, self.cpu, self.memory, self.disk, self.team_code, self.author_id, self.create_time, self.start_time, self.stop_time, self.status,)

    def to_json(self):
        return dict(id=self.id, name=self.name, tag=self.tag, internal_id=self.internal_id,
                    internal_name=self.internal_name, host_id=self.host_id, cpu=self.cpu, memory=self.memory,
                    disk=self.disk, team_code=self.team_code, author_id=self.author_id, create_time=self.create_time,
                    start_time=self.start_time, stop_time=self.stop_time, status=self.status)


class GnContainers(Base):
    __tablename__ = 'GN_CONTAINERS'
    id = Column(String(8), primary_key=True, nullable=False, default="")
    name = Column(String(50), nullable=True, default="")
    tag = Column(String(100), nullable=True, default="")
    internal_id = Column(String(100), nullable=True, default="")
    internal_name = Column(String(100), nullable=True, default="")
    host_id = Column(String(100), nullable=False, default="")
    cpu = Column(Integer, nullable=True, default="")
    memory = Column(Integer, nullable=True, default="")
    disk = Column(Integer, nullable=True, default="")
    team_code = Column(String(10), nullable=True, default="")
    author_id = Column(String(50), nullable=False, default="")
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    start_time = Column(DateTime, nullable=True, default=datetime.datetime.now())
    stop_time = Column(DateTime, nullable=True, default=datetime.datetime.now())
    status = Column(String(10), nullable=True, default="")

    def __init__(
            self,
            id, name, tag, internal_id, internal_name,
            host_id, cpu, memory, disk, team_code,
            author_id, create_time, start_time=create_time, stop_time=create_time, status=""
    ):
        self.id = id
        self.name = name
        self.tag = tag
        self.internal_id = internal_id
        self.internal_name = internal_name
        self.host_id = host_id
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.team_code = team_code
        self.author_id = author_id
        self.create_time = create_time
        self.start_time = start_time
        self.stop_time = stop_time
        self.status = status

    def __repr__(self):
        return "<GnContainers(id=%r, name=%r, tag=%r, internal_id=%r, internal_name=%r, host_id=%r, cpu=%r, memory=%r, disk=%r, team_code=%r, author_id=%r, create_time=%r, start_time=%r, stop_time=%r, status=%r, )>" \
               % (self.id, self.name, self.tag, self.internal_id, self.internal_name, self.host_id, self.cpu, self.memory, self.disk, self.team_code, self.author_id, self.create_time, self.start_time, self.stop_time, self.status,)

    def to_json(self):
        return dict(id=self.id, name=self.name, tag=self.tag, internal_id=self.internal_id,
                    internal_name=self.internal_name, host_id=self.host_id, cpu=self.cpu, memory=self.memory,
                    disk=self.disk, team_code=self.team_code, author_id=self.author_id, create_time=self.create_time,
                    start_time=self.start_time, stop_time=self.stop_time, status=self.status)

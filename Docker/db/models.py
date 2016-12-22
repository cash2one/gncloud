# -*- coding: utf-8 -*-
__author__ = 'gncloud'

import json
import datetime
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, backref
from db.database import Base


class GnHostDocker(Base):
    __tablename__ = 'GN_HOST_DOCKER'
    id = Column(String(8), primary_key=True, nullable=False, default='')
    name = Column(String(100), nullable=True, default='')
    ip = Column(String(50), nullable=True, default='')
    type = Column(String(10), nullable=True, default='')
    cpu = Column(Integer, nullable=True, default='')
    mem = Column(Integer, nullable=True, default='')
    disk = Column(Integer, nullable=True, default='')
    max_cpu = Column(Integer, nullable=True, default='')
    max_mem = Column(Integer, nullable=True, default='')
    max_disk = Column(Integer, nullable=True, default='')
    host_agent_port = Column(Integer, nullable=True, default='')

    def __init__(
            self,
            id, name, ip, type, cpu, mem,
            disk, max_cpu, max_mem, max_disk, host_agent_port
    ):
        self.id = id
        self.name = name
        self.ip = ip
        self.type = type
        self.cpu = cpu
        self.mem = mem
        self.disk = disk
        self.max_cpu = max_cpu
        self.max_mem = max_mem
        self.max_disk = max_disk
        self.host_agent_port = host_agent_port

    def __repr__(self):
        return "<GnHostDocker %r>" % self.id

    def to_json(self):
        return dict(id=self.id, name=self.name, ip=self.ip, type=self.type, cpu=self.cpu, mem=self.mem,
                    disk=self.disk, max_cpu=self.max_cpu, max_mem=self.max_mem, max_disk=self.max_disk,
                    host_agent_port=self.host_agent_port)


class GnDockerServices(Base):
    __tablename__ = 'GN_DOCKER_SERVICES'
    id = Column(String(8), primary_key=True, nullable=False, default='')
    name = Column(String(50), nullable=True, default='')
    tag = Column(String(100), nullable=True, default='')
    internal_id = Column(String(100), nullable=True, default='')
    internal_name = Column(String(100), nullable=True, default='')
    cpu = Column(Integer, nullable=True, default='')
    memory = Column(Integer, nullable=True, default='')
    volume = Column(String(8), nullable=True, default='')
    team_code = Column(String(10), nullable=True, default='')
    author_id = Column(String(50), nullable=False, default='')
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    start_time = Column(DateTime, nullable=True, default=datetime.datetime.now())
    stop_time = Column(DateTime, nullable=True, default=datetime.datetime.now())
    status = Column(String(10), nullable=True, default='')

    def __init__(
        self,
        id, name, tag, internal_id, internal_name,
        cpu, memory, volume, team_code,
        author_id, create_time, start_time=create_time, stop_time=create_time, status=''
    ):
        self.id = id
        self.name = name
        self.tag = tag
        self.internal_id = internal_id
        self.internal_name = internal_name
        self.cpu = cpu
        self.memory = memory
        self.volume = volume
        self.team_code = team_code
        self.author_id = author_id
        self.create_time = create_time
        self.start_time = start_time
        self.stop_time = stop_time
        self.status = status

    def __repr__(self):
        return "<GnDockerServices %r>" % self.id

    def to_json(self):
        return dict(id=self.id, name=self.name, tag=self.tag, internal_id=self.internal_id,
                    internal_name=self.internal_name, cpu=self.cpu, memory=self.memory, volume=self.volume,
                    team_code=self.team_code, author_id=self.author_id, create_time=self.create_time,
                    start_time=self.start_time, stop_time=self.stop_time, status=self.status)


class GnDockerContainers(Base):
    __tablename__ = 'GN_DOCKER_CONTAINERS'
    service_id = Column(String(8), primary_key=True, nullable=False, default='')
    internal_id = Column(String(100), primary_key=True, nullable=True, default='')
    internal_name = Column(String(100), primary_key=True, nullable=True, default='')
    host_id = Column(String(100), nullable=False, default='')
    status = Column(String(10), nullable=True, default='')

    def __init__(self, service_id, internal_id, internal_name, host_id, status=""):
        self.service_id = service_id
        self.internal_id = internal_id
        self.internal_name = internal_name
        self.host_id = host_id
        self.status = status

    def __repr__(self):
        return "<GnDockerContainers %r_%r_%r>" % (self.service_id, self.internal_id, self.internal_name)

    def to_json(self):
        return dict(service_id=self.service_id, internal_id=self.internal_id,
                    internal_name=self.internal_name, host_id=self.host_id, status=self.status)


class GnDockerVolumes(Base):
    __tablename__ = 'GN_DOCKER_VOLUMES'
    service_id = Column(String(8), primary_key=True, nullable=False, default='')
    name = Column(String(200), primary_key=True, nullable=False, default='')
    path = Column(String(200), nullable=False, default='')
    status = Column(String(10), nullable=True, default='')

    def __init__(self, service_id, name, path, status=""):
        self.service_id = service_id
        self.name = name
        self.path = path
        self.status = status

    def __repr__(self):
        return "<GnDockerVolumes %r_%r>" % (self.service_id, self.name)

    def to_json(self):
        return dict(id=self.id, name=self.name, mountpoint=self.mountpoint, status=self.status)


class GnDockerImage(Base):
    __tablename__ = 'GN_DOCKER_IMAGES'
    id = Column(String(8), primary_key=True, nullable=False, default='')
    name = Column(String(50), nullable=False, default='')
    filename = Column(String(100), nullable=True, default='')
    team_code = Column(String(10), nullable=True, default='')
    author_id = Column(String(15), nullable=True, default='')
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    status = Column(String(10), nullable=True, default='')

    def __init__(self, id, name, filename, team_code, author_id, create_time, status):
        self.id = id
        self.name = name
        self.filename = filename
        self.team_code = team_code
        self.author_id = author_id
        self.create_time = create_time
        self.status = status

    def __repr__(self):
        return "<GnDockerImage %r>" % self

    def to_json(self):
        return dict(id=self.id, name=self.name, filename=self.filename, team_code=self.team_code,
                    author_id=self.author_id, create_time=self.create_time, status=self.status)


class GnDockerImageDetail(Base):
    __tablename__ = 'GN_DOCKER_IMAGES_DETAIL'
    id = Column(String(8), primary_key=True, nullable=False, default='')
    arg_type = Column(String(10), primary_key=True, nullable=False, default='')
    argument = Column(String(200), primary_key=True, nullable=False, default='')
    description = Column(String(300), nullable=True, default='')

    def __init__(self, id, arg_type, argument, description):
        self.id = id
        self.arg_type = arg_type
        self.argument = argument
        self.description = description

    def __repr__(self):
        return "<GnDockerImageDetail %r_%r_%r)>" % (self.id, self.arg_type, self.argument)

    def to_json(self):
        return dict(id=self.id, arg_type=self.arg_type, argument=self.argument, description=self.description)

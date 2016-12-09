__author__ = 'NaDa'
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

from manager.db.database import Base


class GnVmMachines(Base):
    __tablename__ = 'GN_VM_MACHINES'
    id = Column(String(30), primary_key=True, nullable=False)
    name = Column(String(50), primary_key=True, nullable=False)
    type = Column(String(50), primary_key=False, nullable=False)
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


    def __init__(self, id=id, name=None, type=None, cpu=None, memory=None, disk=None, ip=None, host_id=None, os=None, os_ver=None, os_sub_ver=None, os_bit=None, author=None, status=None):

        self.id = id
        self.name = name
        self.type = type
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
               % (self.id, self.name, self.type, self.cpu, self.memory, self.disk, self.ip, self.status)

    def __json__(self):
        return ['id', 'name', 'type', 'cpu', 'memory', 'disk', 'ip', 'status']


class GnUser(Base):
    __tablename__ = 'GN_USERS'
    user_id = Column(String(50), primary_key= True, nullable=False)
    password = Column(String(50), primary_key= False, nullable= False)
    user_name = Column(String(20), primary_key= False, nullable= False)
    team_code = Column(String(10), ForeignKey('GN_TEAM.team_code'))
    tel= Column(String(15), primary_key= False, nullable= False)
    email= Column(String(30), primary_key= False, nullable= False)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    gnTeam=relationship('GnTeam')



    def __init__(self, user_id = user_id, password= None, team_code=None, user_name=None, tel=None, email=None, start_date=None):

        self.user_id = user_id
        self.password= password
        self.team_code = team_code
        self.user_name = user_name
        self.tel = tel
        self.email = email
        self.start_date = start_date

    def __repr__(self):
        return '< ID %r / Password %r / Team_code %r / User_name %r / Tel %r / Eamil %r / Team_name %r >' \
                % (self.user_id, self.password, self.team_code, self.user_name, self.tel, self.email, self.gnTeam.team_name)

    def __json__(self):
        return ['user_id', 'password', 'team_code', 'user_name', 'tel' , 'email', 'gnTeam']

# class GnMonitor(Base):
#     __tablename__ = 'GN_MONITIOR'
#     id = Column(Integer, primary_key=True, nullable= False)
#     cpu_usage = Column(Integer, primary_key=False, nullable=False)
#     mem_usage = Column(Integer, primary_key=False, nullable=False)
#
#     def __init__(self,id = id, cpu_usage =None, mem_usage=None):
#         self.id = id
#         self.cpu_usage = cpu_usage
#         self.mem_usage = mem_usage
#
#     def __repr__(self):
#         return '<ID %r / cpu_usage %r / mem_usage %r>' \
#                % (self.cpu_usage, self.mem_usage)
#
#     def __json__(self):
#         return  ['id', 'cpu_usage', 'mem_usage']

class GnTeam(Base):
    __tablename__ = 'GN_TEAM'
    team_code = Column(Integer, primary_key=True, nullable=False)
    team_name = Column(String(50), primary_key=False, nullable=False)
    author_id = Column(String(50), primary_key=False, nullable=False)
    cpu_quota = Column(String(50), primary_key=False, nullable=False)
    mem_quota = Column(String(50), primary_key=False, nullable=False)
    disk_quota = Column(String(50), primary_key=False, nullable=False)

    def __init__(self, team_code = team_code, team_name= team_name, author_id =author_id, cpu_quota =cpu_quota, mem_quota = mem_quota, disk_quota = disk_quota):
        self.team_code = team_code
        self.team_name = team_name
        self.author_id = author_id
        self.cpu_quota = cpu_quota
        self.mem_quota = mem_quota
        self.disk_quota = disk_quota


    def __repr__(self):
        return '<TEAM_CODE %r / TEAM_NAME %r / AUTHOR_ID %r / CPU_QUOTA %r / MEM_QUOTA %r / DISK_QUOTA %r>' \
               % (self.team_name, self.team_code, self.author_id, self.cpu_quota, self.mem_quota, self.disk_quota)

    def __json__(self):
        return  ['team_code', 'team_name', 'author_id', 'cpu_quota', 'mem_quota', 'disk_quota']
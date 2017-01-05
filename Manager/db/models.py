__author__ = 'NaDa'
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime,  Numeric
from sqlalchemy.orm import relationship
import datetime

from Manager.db.database import Base


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
    host_id = Column(String(8), ForeignKey('GN_HOST_MACHINES.id'))
    os = Column(String(10), primary_key=False, nullable=True)
    os_ver = Column(String(20), primary_key=False, nullable=True)
    os_sub_ver = Column(String(20), primary_key=False, nullable=True)
    os_bit = Column(String(2), primary_key=False, nullable=True)
    team_code = Column(String(50), primary_key=False, nullable=True)
    author_id = Column(String(15), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now())
    start_time = Column(DateTime, default=datetime.datetime.now())
    stop_time = Column(DateTime, default=datetime.datetime.now())
    status = Column(String(10), primary_key=False, nullable=False)
    tag = Column(String(100), primary_key=False, nullable=False)
    image_id = Column(String(8), primary_key=False, nullable=False)
    ssh_key_id = Column(Integer, primary_key=False, nullable=False)
    gnHostMachines = relationship('GnHostMachines')

    def __init__(self, id=id, name=None, type=None, internal_id=None, internal_name=None
                 , cpu=None, memory=None, disk=None, ip=None, host_id=None
                 , os=None, os_ver=None, os_sub_ver=None, os_bit=None, team_code=None
                 , author_id=None, status=None, tag=None, image_id=None, ssh_key_id=None):
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
        self.team_code = team_code
        self.author_id = author_id
        self.status = status
        self.tag = tag
        self.image_id = image_id
        self.ssh_key_id = ssh_key_id


    def __repr__(self):
        return '<Id %r / Name %r / Type %r / Internal_id %r / Internal_name %r / ' \
               'Cpu %r / Memory %r / Disk %r / Ip %r / Status %r / Tag %r / Create_time %r / ' \
               'Ssh_key_id %r>' \
               % (self.id, self.name, self.type, self.internal_id, self.internal_name, self.cpu, self.memory, self.disk,
                  self.ip, self.status, self.tag, self.create_time, self.ssh_key_id)

    def __json__(self):
        return ['id', 'name', 'type', 'internal_id', 'internal_name', 'cpu'
            , 'memory', 'disk', 'ip', 'status', 'tag', 'create_time', 'os']


class GnUser(Base):
    __tablename__ = 'GN_USERS'
    user_id = Column(String(50), primary_key= True, nullable=False)
    password = Column(String(50), primary_key= False, nullable= False)
    user_name = Column(String(20), primary_key= False, nullable= False)
    tel= Column(String(15), primary_key= False, nullable= False)
    email= Column(String(30), primary_key= False, nullable= False)
    start_date = Column(DateTime, default=datetime.datetime.now())



    def __init__(self, user_id = user_id, password= None, team_code=None, user_name=None, tel=None, email=None, start_date=None):

        self.user_id = user_id
        self.password= password
        self.team_code = team_code
        self.user_name = user_name
        self.tel = tel
        self.email = email
        self.start_date = start_date

    def __repr__(self):
        return '< ID %r / Password %r / User_name %r / Tel %r / Eamil %r/ Start_date %r />' \
                % (self.user_id, self.password, self.user_name, self.tel, self.email, self.start_date)

    def __json__(self):
        return ['user_id', 'password', 'user_name', 'tel' , 'email', 'start_date']

class GnUserTeam(Base):
    __tablename__="GN_USER_TEAMS"
    user_id = Column(String(50),primary_key=True, nullable=False )
    team_code = Column(String(20), primary_key=True, nullable=False)
    comfirm = Column(String(1), primary_key=False, nullable=False)
    apply_date = Column(DateTime, default=datetime.datetime.now())
    approve_date = Column(DateTime, default=datetime.datetime.now())
    team_owner = Column(String(20), primary_key=False, nullable=False)

    def __init__(self, user_id=user_id, team_code=None, comfirm=None, apply_date =None, approve_date=None, team_owner = None):
        self.user_id = user_id
        self.team_code = team_code
        self.comfirm = comfirm
        self.apply_date =apply_date
        self.approve_date = approve_date
        self.team_owner = team_owner

    def __repr__(self):
        return '<Id %r /Team_code %r / Comfirm %r / Apply_date %r / Approve_date %r / Team_Owner %r />' \
               % (self.user_id, self.team_code, self.comfirm, self.apply_date, self.approve_date, self.team_owner)

    def __json__(self):
        return ['user_id', 'team_code', 'comfirm', 'apply_date', 'approve_date', 'team_owner']

class GnTeam(Base):
    __tablename__ = 'GN_TEAM'
    team_code = Column(String(10), primary_key=True, nullable=False)
    team_name = Column(String(50), primary_key=False, nullable=False)
    author_id = Column(String(50), primary_key=False, nullable=False)
    cpu_quota = Column(Integer, primary_key=False, nullable=False)
    mem_quota = Column(Integer, primary_key=False, nullable=False)
    disk_quota = Column(Integer, primary_key=False, nullable=False)
    create_date = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, team_code = team_code, team_name= None, author_id =None, cpu_quota =None, mem_quota = None, disk_quota = None, create_date=None):
        self.team_code = team_code
        self.team_name = team_name
        self.author_id = author_id
        self.cpu_quota = cpu_quota
        self.mem_quota = mem_quota
        self.disk_quota = disk_quota
        self.create_date = create_date

    def __repr__(self):
        return '<TEAM_CODE %r / TEAM_NAME %r / AUTHOR_ID %r / CPU_QUOTA %r / MEM_QUOTA %r / DISK_QUOTA %r / CREATE_DATE %r />' \
               % (self.team_name, self.team_code, self.author_id, self.cpu_quota, self.mem_quota, self.disk_quota, self.create_date)

    def __json__(self):
        return  ['team_code', 'team_name', 'author_id', 'cpu_quota', 'mem_quota', 'disk_quota', 'create_date']

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
    create_time = Column(DateTime, default=datetime.datetime.now())
    pool_id = Column(String(8), primary_key=False, nullable=False)
    status = Column(String(10), primary_key=False, nullable=False)


    def __init__(self, name=None, filename=None, type=None
                 , sub_type=None, icon=None, os=None, os_ver=None, os_subver=None
                 , os_bit=None, team_code=None, author_id=None, pool_id= None, create_time= None, status=None):
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
        self.pool_id = pool_id
        self.create_time = create_time
        self.status = status



    def __repr__(self):
        return '< ID %r / Name %r / Filename %r / Type %r / Sub_type %r / Icon %r / Os %r / Os_Ver %r / Os_subVer %r / Os_bit %r / Team_code %r / Author_id %r / Create_time %r / Pool_id %r/ Status %r / >'\
                % (self.id, self.name, self.filename, self.type, self.sub_type, self.icon, self.os, self.os_ver, self.os_subver, self.os_bit, self.team_code, self.author_id, self.create_time, self.pool_id, self.status)
    def __json__(self):
        return ['id', 'name', 'filename', 'type', 'sub_type', 'icon', 'os', 'os_ver', 'os_subver', 'os_bit','team_code', 'author_id', 'create_time', 'pool_id', 'status']


class GnSshKeys(Base):
    __tablename__ = "GN_SSH_KEYS"
    id = Column(Integer, primary_key=True, nullable=False)
    team_code = Column(String(50), primary_key=False, nullable=False)
    name = Column(String(100), primary_key=False, nullable=False)
    fingerprint = Column(String(50), primary_key=False, nullable=False)
    path = Column(String(100), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now())

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


class GnSshKeysMapping(Base):
    __tablename__ = "GN_SSH_KEYS_MAPPING"
    id = Column(Integer, primary_key=True, nullable=False)
    ssh_key_id = Column(Integer, primary_key=False, nullable=False)
    vm_id = Column(String(8), primary_key=False, nullable=False)

    def __init__(self, ssh_key_id=None, vm_id=None):
        self.ssh_key_id = ssh_key_id
        self.vm_id = vm_id

    def __repr__(self):
        return '<Ssh_key_id %r /Vm_id %r  >' \
               % (self.ssh_key_id, self.vm_id)


class GnDockerImages(Base):
    __tablename__="GN_DOCKER_IMAGES"
    id = Column(String(8), primary_key=True, nullable=False, default='')
    name = Column(String(50), nullable=False, default='')
    view_name = Column(String(50), nullable=False, default='')
    tag = Column(String(200), nullable=True, default='')
    os = Column(String(50), nullable=True, default='')
    os_ver = Column(String(45), nullable=True, default='')
    team_code = Column(String(10), nullable=True, default='')
    sub_type = Column(String(10), nullable=True, default='')
    author_id = Column(String(10), nullable=True, default='')
    create_time = Column( nullable=False, default=datetime.datetime.now())
    status = Column(String(10), primary_key=False, nullable=False)

    def __init__(self, id=id, name= None, tag=None, os=None, os_ver=None, team_code=None, author_id =None, create_time=None, status=None, view_name=None):
        self.id= id
        self.name =name
        self.tag = tag
        self.os= os
        self.os_ver = os_ver
        self.team_code = team_code
        self.author_id =author_id
        self.create_time = create_time
        self.status = status
        self.view_name = view_name
        self.type = type

    def __repr__(self):
        return '<ID %r / Name %r / Tag %r / Os %r / Os_ver %r /Team_code %r / create_time %r / Status %r/ View_name %r />'\
            % (self.id, self.name, self.tag, self.os, self.os_ver, self.team_code, self.create_time, self.Status, self.view_name)

    def __json__(self):
        return ['id', 'name','tag' ,'os','os_ver','team_code', 'create_time','status', 'view_name']

class GnMonitor(Base):
    __tablename__ = "GN_MONITOR"
    id = Column(String(8), primary_key=True, nullable=False)
    type = Column(String(6), primary_key=False, nullable=False)
    cpu_usage = Column(Numeric, primary_key=False, nullable=False)
    mem_usage = Column(Numeric, primary_key=False, nullable=False)
    disk_usage = Column(Numeric, primary_key=False, nullable=False)
    net_usage = Column(Numeric, primary_key=False, nullable=False)

    def __init__(self, id=id, type=type, cpu_usage=None, mem_usage=None, disk_usage=None, net_usage=None):
        self.id = id
        self.type = type
        self.cpu_usage = cpu_usage
        self.mem_usage = mem_usage
        self.disk_usage = disk_usage
        self.net_usage = net_usage

    def __repr__(self):
        return '<ID %r / Type %r / Cpu_usage %r / Mem_usage %r / Disk_usage %r / Net_usage %r>' \
               % (self.id, self.type, self.cpu_usage, self.mem_usage, self.disk_usage, self.net_usage)

    def __json__(self):
        return ['id', 'type', 'cpu_usage', 'mem_usage', 'disk_usage', 'net_usage']

class GnMonitorHist(Base):
    __tablename__ = "GN_MONITOR_HIST"
    seq = Column(Integer, primary_key=True, nullable=False)
    id = Column(String(8), primary_key=False, nullable=False)
    type = Column(String(6), primary_key=False, nullable=False)
    cur_time = Column(DateTime, primary_key=False, nullable=False)
    cpu_usage = Column(Numeric, primary_key=False, nullable=False)
    mem_usage = Column(Numeric, primary_key=False, nullable=False)
    disk_usage = Column(Numeric, primary_key=False, nullable=False)
    net_usage = Column(Numeric, primary_key=False, nullable=False)
    cur_time = Column(DateTime, primary_key=True, default=datetime.datetime.now())

    def __init__(self, id=id, type=type, cpu_usage=None, mem_usage=None, disk_usage=None, net_usage=None):
        self.id = id
        self.type = type
        self.cpu_usage = cpu_usage
        self.mem_usage = mem_usage
        self.disk_usage = disk_usage
        self.net_usage = net_usage

    def __repr__(self):
        return '<ID %r / Type %r / Cpu_usage %r / Mem_usage %r / Disk_usage %r / Net_usage %r>' \
               % (self.id, self.type, self.cpu_usage, self.mem_usage, self.disk_usage, self.net_usage)

    def __json__(self):
        return ['id', 'type', 'cpu_usage', 'mem_usage', 'disk_usage', 'net_usage', 'cur_time']


class GnImagePool(Base):
    __tablename__= "GN_IMAGES_POOL"
    id = Column(String(8), primary_key=True, nullable=False)
    type =Column(String(10), primary_key=False, nullable=False)
    image_path =Column(String(200), primary_key=False,nullable=False)
    host_id =Column(String(8), primary_key=False, nullable=False)

    def __init__(self, id=id, type=None, image_path=None, host_id=None):
        self.id = id
        self.type = type
        self.image_path = image_path
        self.host_id = host_id

    def __repr__(self):
        return '< ID %r / Type %r / Image_path %r / Host_id %r>'\
                %(self.id , self.type, self.image_path, self.host_id)

    def __json__(self):
        return ['id', 'type', 'image_path', 'host_id']


class GnId(Base):
    __tablename__ = "GN_ID"
    id = Column(String(8), primary_key=True, nullable=False)
    type = Column(String(20), primary_key=False, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, id=None, type=None):
        self.id = id
        self.type = type

    def __repr__(self):
        return '<Id %r / Type %r >' \
               % (self.id, self.type)

class GnTeamHist(Base):
    __tablename__="GN_TEAM_HIST"
    team_code = Column(String(10), primary_key=True, nullable=False)
    team_del_code = Column(String(8), primary_key=True,nullable=False )
    team_name = Column(String(50), primary_key=False, nullable=False)
    author_id = Column(String(50), primary_key=False, nullable=False)
    cpu_quota = Column(Numeric, primary_key=False, nullable=False)
    mem_quota = Column(Numeric, primary_key=False, nullable=False)
    disk_quota = Column(Numeric, primary_key=False, nullable=False)
    delete_date = Column(DateTime, primary_key=True, default=datetime.datetime.now())

    def __init__(self, team_code=team_code, team_del_code= team_del_code, team_name=None, author_id= None, cpu_quota=None, mem_quota=None, disk_quota=None, delete_date=None):
        self.team_code = team_code
        self.team_del_code = team_del_code
        self.team_name = team_name
        self.author_id = author_id
        self.cpu_quota = cpu_quota
        self.mem_quota =mem_quota
        self.disk_quota= disk_quota
        self.delete_date = delete_date

    def __repr__(self):
        return '< Tema_code %r / Team_del_code %r / Team_name %r / Author_id %r / Cpu_quota %r / Mem_quota %r / Disk_quota %r / Delete_date %r />' \
                % (self.team_code, self.team_del_code, self.team_name, self.author_id, self.cpu_quota, self.mem_quota, self.disk_quota, self.delete_date)

    def __json__(self):
        return ['team_code', 'team_del_code', 'team_name', 'author_id', 'cpu_quota', 'mem_quota', 'disk_quta', 'delete_date']


class GnUserTeamHist(Base):
    __tablename__='GN_USER_TEAMS_HIST'
    user_id = Column(String(50), primary_key=True, nullable=False)
    team_code= Column(String(0), primary_key=True, nullable=False)
    team_del_code = Column(String(8), primary_key=True, nullable=False)
    comfirm= Column(String(1), primary_key=False, nullable=False)
    apply_date = Column(DateTime, primary_key=True, default=datetime.datetime.now())
    approve_date = Column(DateTime, primary_key=True, default=datetime.datetime.now())
    delete_date = Column(DateTime, primary_key=True, default=datetime.datetime.now())
    team_owner = Column(String(10), primary_key=False, nullable=False)

    def __init__(self, user_id=id, team_code=team_code, team_del_code = team_del_code, comfirm=None, apply_date=None, approve_date=None, delete_date=None, team_owner=None):
        self.user_id =user_id
        self.team_code = team_code
        self.team_del_code = team_del_code
        self.comfirm = comfirm
        self.apply_date = apply_date
        self.approve_date =approve_date
        self.delete_date =delete_date
        self.team_owner = team_owner

    def __repr__(self):
        return '< User_id %r / Team_code %r / Team_del_code %r / Comfirm %r / Apply_date %r / Approve_date %r / Delete_date %r / Team_owner %r />'\
            %(self.user_id, self.team_code, self. team_del_code, self.comfirm, self.apply_date, self.approve_date, self.delete_date, self.team_owner)

    def __json__(self):
        return ['user_id', 'tema_code', 'team_del_code', 'comfirm', 'apply_date', 'approve_date', 'delete_date', 'team_owner']
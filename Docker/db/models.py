# -*- coding: utf-8 -*-
__author__ = 'gncloud'

import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from Docker.db.database import Base


# GnCloud에서 사용하는 각 노드 정보
class GnHostMachines(Base):
    __tablename__ = "GN_HOST_MACHINES"
    id = Column(String(8), primary_key=True, nullable=False)
    name = Column(String(100), primary_key=False, nullable=False)
    ip = Column(String(50), primary_key=False, nullable=False)
    type = Column(String(10), primary_key=False, nullable=False)
    cpu = Column(Integer, primary_key=False, nullable=False)
    mem = Column(Integer, primary_key=False, nullable=False)
    disk = Column(Integer, primary_key=False, nullable=False)
    host_agent_port = Column(Integer, primary_key=False, nullable=False)

    def __init__(self, id, name, ip, type, cpu="", mem="", disk="", host_agent_port=""):
        self.id = id
        self.name = name
        self.ip = ip
        self.type = type
        self.cpu = cpu
        self.mem = mem
        self.disk = disk
        self.host_agent_port = host_agent_port

    def __repr__(self):
        return '<GnHostMachines %r>' % self.id

    def to_json(self):
        return dict(id=self.id, name=self.name, ip=self.ip, type=self.type, cpu=self.cpu, mem=self.mem, disk=self.disk,
                    max_cpu=self.max_cpu, max_mem=self.max_mem, max_disk=self.max_disk,
                    host_agent_port=self.host_agent_port)


'''
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

    def __init__(self, id, name, ip, type, cpu, mem, disk, max_cpu, max_mem, max_disk, host_agent_port):
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
'''


class GnVmMachines(Base):
    __tablename__ = 'GN_VM_MACHINES'
    id = Column(String(8), primary_key=True, nullable=False, default='')
    name = Column(String(50), nullable=True, default='')
    tag = Column(String(100), nullable=True, default='')
    type = Column(String(10), nullable=False, default='')
    internal_id = Column(String(100), nullable=True, default='')
    internal_name = Column(String(100), nullable=True, default='')
    host_id = Column(Integer, ForeignKey('GN_HOST_MACHINES.id'))
    ip = Column(String(20), nullable=True, default='')
    cpu = Column(Integer, nullable=False, default='')
    memory = Column( nullable=False, default='')
    disk = Column( nullable=True, default='')
    os = Column(String(10), nullable=True, default='')
    os_ver = Column(String(20), nullable=True, default='')
    os_sub_ver = Column(String(20), nullable=True, default='')
    os_bit = Column(String(2), nullable=True, default='')
    team_code = Column(String(10), nullable=True, default='')
    author_id = Column(String(50), nullable=False, default='')
    create_time = Column(DateTime, default=datetime.datetime.now())
    start_time = Column(DateTime, default=datetime.datetime.now())
    stop_time = Column(DateTime, default=datetime.datetime.now())
    status = Column(String(10), nullable=True, default='')
    hyperv_pass = Column(String(50), nullable=True, default='')
    image_id = Column(String(8), nullable=True, default='')
    ssh_key_id = Column(Integer, nullable=True, default='')
    gnHostMachines = relationship('GnHostMachines')
    gnDockerServices = relationship('GnDockerServices')
    gnDockerContainers = relationship('GnDockerContainers')
    gnDockerVolumes = relationship('GnDockerVolumes')
    gnDockerPorts = relationship('GnDockerPorts')
    size_id = Column(String(8), nullable=False, default=None)

    def __init__(self,
                 id, name=None, tag=None, type=None, internal_id=None, internal_name=None, host_id=None, ip=None,
                 cpu=None, memory=None, disk=None, os=None, os_ver=None, os_sub_ver=None, os_bit=None, team_code=None,
                 author_id=None, create_time=None, status=None, hyperv_pass=None, image_id=None, ssh_key_id=None, size_id=None):
        self.id = id
        self.name = name
        self.tag = tag
        self.type = type
        self.internal_id = internal_id
        self.internal_name = internal_name
        self.host_id = host_id
        self.ip = ip
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.os = os
        self.os_ver = os_ver
        self.os_sub_ver = os_sub_ver
        self.os_bit = os_bit
        self.team_code = team_code
        self.author_id = author_id
        self.status = status
        self.hyperv_pass = hyperv_pass
        self.create_time = create_time
        self.image_id = image_id
        self.ssh_key_id = ssh_key_id
        self.size_id = size_id

    def __repr__(self):
        return '<Id %r / Name %r / Type %r / Internal_id %r / Internal_name %r / Cpu %r / Memory %r / Disk %r / Ip %r / Status %r / Tag %r / Create_time %r>' \
               % (self.id, self.name, self.type, self.internal_id, self.internal_name, self.cpu, self.memory, self.disk,
                  self.ip, self.status, self.tag, self.create_time)

    def to_json(self):
        return dict(id=self.id, name=self.name, tag=self.tag, type=self.type, internal_id=self.internal_id,
                    internal_name=self.internal_name, host_id=self.host_id, ip=self.ip, cpu=self.cpu,
                    memory=self.memory, disk=self.disk, os=self.os, os_ver=self.os_ver, os_sub_ver=self.os_sub_ver,
                    os_bit=self.os_bit, team_code=self.team_code, author_id=self.author_id,
                    create_time=self.create_time, start_time=self.start_time, stop_time=self.stop_time,
                    hyperv_pass=self.hyperv_pass, status=self.status, image_id=self.image_id, ssh_key_id=self.ssh_key_id)


class GnDockerServices(Base):
    __tablename__ = 'GN_DOCKER_SERVICES'
    service_id = Column(String(8), ForeignKey('GN_VM_MACHINES.id'), primary_key=True, nullable=False)
    image = Column(String(100), ForeignKey('GN_DOCKER_IMAGES.name'), nullable=True, default='')
    gnDockerImages = relationship('GnDockerImages')

    def __init__(self, service_id, image):
        self.service_id = service_id
        self.image = image

    def __repr__(self):
        return "<GnDockerServices %r>" % self.service_id

    def to_json(self):
        return dict(service_id=self.service_id, image=self.image)


# class GnDockerServices(Base):
#     __tablename__ = 'GN_DOCKER_SERVICES'
#     id = Column(String(8), primary_key=True, nullable=False, default='')
#     name = Column(String(50), nullable=True, default='')
#     internal_id = Column(String(100), nullable=True, default='')
#     internal_name = Column(String(100), nullable=True, default='')
#     image = Column(String(50), nullable=True, default='')
#     cpu = Column(Integer, nullable=True, default='')
#     memory = Column(Integer, nullable=True, default='')
#     volume = Column(String(8), nullable=True, default='')
#     team_code = Column(String(10), nullable=True, default='')
#     author_id = Column(String(50), nullable=False, default='')
#     create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
#     start_time = Column(DateTime, nullable=True, default=datetime.datetime.now())
#     stop_time = Column(DateTime, nullable=True, default=datetime.datetime.now())
#     tag = Column(String(100), nullable=True, default='')
#     status = Column(String(10), nullable=True, default='')
#
#     def __init__(
#         self,
#         id, name, tag, internal_id, internal_name,
#         image, cpu, memory, volume, team_code,
#         author_id, create_time, start_time=create_time, stop_time=create_time, status=''
#     ):
#         self.id = id
#         self.name = name
#         self.tag = tag
#         self.internal_id = internal_id
#         self.internal_name = internal_name
#         self.image = image,
#         self.cpu = cpu
#         self.memory = memory
#         self.volume = volume
#         self.team_code = team_code
#         self.author_id = author_id
#         self.create_time = create_time
#         self.start_time = start_time
#         self.stop_time = stop_time
#         self.status = status
#
#     def __repr__(self):
#         return "<GnDockerServices %r>" % self.id
#
#     def to_json(self):
#         return dict(id=self.id, name=self.name, tag=self.tag, internal_id=self.internal_id,
#                     internal_name=self.internal_name, image=self.image, cpu=self.cpu, memory=self.memory,
#                     volume=self.volume, team_code=self.team_code, author_id=self.author_id,
#                     create_time=self.create_time, start_time=self.start_time,
#                     stop_time=self.stop_time, status=self.status)


class GnDockerContainers(Base):
    __tablename__ = 'GN_DOCKER_CONTAINERS'
    service_id = Column(String(8), ForeignKey('GN_VM_MACHINES.id'), primary_key=True, nullable=False)
    internal_id = Column(String(100), primary_key=True, nullable=True, default='')
    internal_name = Column(String(100), primary_key=True, nullable=True, default='')
    host_id = Column(String(8), ForeignKey('GN_HOST_MACHINES.id'), nullable=False, default='')
    status = Column(String(10), nullable=True, default='')
    gnHostMachines = relationship('GnHostMachines')

    def __init__(self, service_id, internal_id, internal_name, host_id, status=""):
        self.service_id = service_id
        self.internal_id = internal_id
        self.internal_name = internal_name
        self.host_id = host_id
        self.status = status

    def __repr__(self):
        return "<GnDockerContainers %r>" % self.internal_id

    def to_json(self):
        return dict(service_id=self.service_id, internal_id=self.internal_id,
                    internal_name=self.internal_name, host_id=self.host_id, status=self.status)


class GnDockerVolumes(Base):
    __tablename__ = 'GN_DOCKER_VOLUMES'
    service_id = Column(String(8), ForeignKey('GN_VM_MACHINES.id'), primary_key=True)
    name = Column(String(200), nullable=False, default='')
    source_path = Column(String(200), nullable=False, default='')
    destination_path = Column(String(200), nullable=False, default='')
    status = Column(String(10), nullable=True, default='')

    def __init__(self, service_id, name, source_path, destination_path, status=""):
        self.service_id = service_id
        self.name = name
        self.source_path = source_path
        self.destination_path = destination_path
        self.status = status

    def __repr__(self):
        return "<GnDockerVolumes %r_%r>" % (self.service_id, self.name)

    def to_json(self):
        return dict(service_id=self.service_id, name=self.name, source_path=self.source_path,
                    destination_path=self.destination_path, status=self.status)


class GnDockerPorts(Base):
    __tablename__ = 'GN_DOCKER_PORTS'
    service_id = Column(String(8), ForeignKey('GN_VM_MACHINES.id'), primary_key=True, nullable=False, default='')
    protocol = Column(String(10), primary_key=True, nullable=False, default='')
    target_port = Column(String(5), primary_key=True, nullable=False, default='0')
    published_port = Column(String(5), primary_key=True, nullable=False, default='0')

    def __init__(self, service_id, protocol, target_port, published_port):
        self.service_id = service_id
        self.protocol = protocol
        self.target_port = target_port
        self.published_port = published_port

    def __repr__(self):
        return "<GnDockerPorts %r_%r_%r_%r>" % (self.service_id, self.protocol, self.target_port, self.published_port)

    def to_json(self):
        return dict(service_id=self.service_id, protocol=self.protocol, target_port=self.target_port, published_port=self.published_port)


class GnDockerImages(Base):
    __tablename__ = 'GN_DOCKER_IMAGES'
    id = Column(String(8), primary_key=True, nullable=False)
    base_image = Column(String(8), primary_key=True, nullable=False)
    name = Column(String(200), nullable=False, default='')
    view_name = Column(String(200), nullable=False, default='')
    tag = Column(String(200), nullable=False, default='')
    os = Column(String(50), nullable=False, default='')
    os_ver = Column(String(45), nullable=False, default='')
    sub_type = Column(String(10), nullable=False, default='')
    team_code = Column(String(10), nullable=True, default='')
    author_id = Column(String(15), nullable=True, default='')
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    status = Column(String(10), nullable=True, default='')

    def __init__(self, id, base_image, name, view_name, tag, os, os_ver, sub_type, team_code, author_id, create_time, status):
        self.id = id
        self.name = name
        self.base_image = base_image
        self.view_name = view_name
        self.tag = tag
        self.os = os
        self.os_ver = os_ver
        self.sub_type = sub_type
        self.team_code = team_code
        self.author_id = author_id
        self.create_time = create_time
        self.status = status

    def __repr__(self):
        return "<GnDockerImages %r_%r_%r>" % (self.id, self.name, self.view_name)

    def to_json(self):
        return dict(id=self.id, base_image=self.base_image, name=self.name, view_name=self.view_name, tag=self.tag, os=self.os,
                    os_ver=self.os_ver, sub_type=self.sub_type, team_code=self.team_code,
                    author_id=self.author_id, create_time=self.create_time, status=self.status)


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
    ssh_id = Column(String(10), primary_key=False, nullable=False)
    status = Column(String(10), primary_key=False, nullable=False)

    def __init__(self, name=None, filename=None, type=None
                 , sub_type=None, icon=None, os=None, os_ver=None, os_subver=None
                 , os_bit=None, team_code=None, author_id=None, ssh_id=None, status=None):
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
        self.ssh_id = ssh_id
        self.status = status

    def __repr__(self):
        return '<Id %r / Name %r / File_name %r / Type %r / Sub_type %r / Icon %r / Os %r / Os_ver %r / Os_subver %r / Team_code %r /Author_id %r / Create_time %r / Create_time %r / Ssh_id %r>' \
               % (self.id, self.name, self.file_name, self.type, self.sub_type
                  , self.icon, self.os, self.os_ver, self.os_subver, self.os_bit
                  , self.team_code, self.author_id, self.create_time, self.ssh_id)

    def __json__(self):
        return ['id', 'name', 'filename', 'type', 'sub_type'
            , 'icon', 'os', 'os_ver', 'os_subver', 'os_bit'
            , 'team_code', 'author_id', 'create_time', 'ssh_id', 'status']

    def to_json(self):
        return dict(id=self.id, name=self.name, file_name=self.file_name, type=self.type, sub_type=self.sub_type,
                    icon=self.icon, os=self.os, os_ver=self.os_ver, os_subver=self.os_subver, os_bit=self.os_bit,
                    team_code=self.team_code, author_id=self.author_id, create_time=self.create_time, ssh_id=self.ssh_id,
                    status=self.status)


class GnDockerImageDetail(Base):
    __tablename__ = 'GN_DOCKER_IMAGES_DETAIL'
    id = Column(String(8), primary_key=True, nullable=False, default='')
    image_id = Column(String(8), ForeignKey('GN_DOCKER_IMAGES.id'))
    arg_type = Column(String(10), nullable=False, default='')
    argument = Column(String(200), nullable=False, default='')
    description = Column(String(300), nullable=True, default='')
    status = Column(String(10), nullable=True, default='')

    def __init__(self, id, image_id, arg_type, argument, description, status):
        self.id = id
        self.image_id = image_id
        self.arg_type = arg_type
        self.argument = argument
        self.description = description
        self.status = status

    def __repr__(self):
        return "<GnDockerImageDetail %r_%r)>" % (self.id, self.image_id)

    def to_json(self):
        return dict(id=self.id, image_id=self.image_id, arg_type=self.arg_type,
                    argument=self.argument, description=self.description, status=self.status)


class GnMonitor(Base):
    __tablename__ = "GN_MONITOR"
    id = Column(String(8), primary_key=True, nullable=False)
    type = Column(String(6), primary_key=False, nullable=False)
    cpu_usage = Column(Numeric, primary_key=False, nullable=False)
    mem_usage = Column(Numeric, primary_key=False, nullable=False)
    disk_usage = Column(Numeric, primary_key=False, nullable=False)
    net_usage = Column(Numeric, primary_key=False, nullable=False)

    def __init__(self, id, type, cpu_usage=None, mem_usage=None, disk_usage=None, net_usage=None):
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

    def __init__(self, id, type, cpu_usage=None, mem_usage=None, disk_usage=None, net_usage=None):
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


class GnVmSize(Base):
    __tablename__ = 'GN_VM_SIZE'
    id = Column(String(8), primary_key=True, nullable=False)
    cpu = Column(Numeric, primary_key=False, nullable=False)
    mem = Column(Numeric, primary_key=False, nullable=False)
    disk = Column(Numeric, primary_key=False, nullable=False)
    hour_price = Column(Integer, primary_key=False, nullable=False)
    day_price= Column(Integer, primary_key=False, nullable=False)

    def __init__(self,id=id, cpu=None, mem=None, disk=None, hour_price=None, day_price=None):
        self.id=id
        self.cpu = cpu
        self.mem = mem
        self.disk = disk
        self.hour_price = hour_price
        self.day_price = day_price

    def __repr__(self):
        return '< ID %r / Cpu %r / Mem %r / Disk %r / Hour_price %r / day_price %r/>' \
               %(self.id, self.cpu, self.mem, self.disk, self.hour_price, self.day_price)

    def __json__(self):
        return ['id', 'cpu', 'mem', 'disk', 'hour_price', 'day_price']


class GnInstanceStatus(Base):
    __tablename__ = 'GN_INSTANCE_STATUS'
    vm_id = Column(String(8), primary_key=True, nullable=False, default='')
    vm_name = Column(String(50), nullable=True, default='')
    create_time = Column(DateTime, nullable=False, default='')
    delete_time = Column(DateTime, nullable=True)
    author_id = Column(String(50), nullable=False, default='')
    author_name = Column(String(20), nullable=False, default='')
    team_code = Column(String(10), nullable=True, default='')
    team_name = Column(String(50), nullable=True, default=None)
    price = Column(Integer, nullable=True, default='')
    price_type = Column(String(2), nullable=True, default='')
    cpu = Column( nullable=True, default='')
    memory = Column( nullable=True, default='')
    disk = Column( nullable=True, default='')


    def __init__(self, vm_id=None,vm_name=None,create_time=None, delete_time=None, author_id=None, author_name=None
                 ,team_code=None, team_name=None, price=None, price_type=None, cpu=None, memory=None, disk=None):
        self.vm_id = vm_id
        self.vm_name = vm_name
        self.create_time = create_time
        self.delete_time = delete_time
        self.author_id = author_id
        self.author_name = author_name
        self.team_code = team_code
        self.team_name = team_name
        self.price = price
        self.price_type = price_type
        self.cpu = cpu
        self.memory = memory
        self.disk = disk

    def __repr__(self):
        return "<GnInstanceStatus(vm_id='%r', create_time='%r', delete_time='%r', author_id='%r', team_code='%r'," \
               "price='%r', price_type='%r', cpu='%r', memory='%r', disk='%r')" \
               % (self.vm_id, self.create_time, self.delete_time, self.author_id, self.team_code, self.price,
                  self.price_type, self.cpu, self.memory, self.disk)


class GnSystemSetting(Base):
    __tablename__='GN_SYSTEM_SETTING'
    billing_type = Column(String(2), primary_key=True, nullable=False, default='')
    backup_schedule_type = Column(String(2), nullable=True, default='')
    backup_schedule_period = Column(String(13), nullable=True, default='')
    monitor_period = Column(String(4), nullable=True, default='')

    def __init__(self, billing_type = billing_type, backup_schedule_type =None, backup_schedule_period= None, monitor_period=None):
        self.billing_type = billing_type
        self.backup_schedule_type = backup_schedule_type
        self.backup_schedule_period = backup_schedule_period
        self.monitor_period = monitor_period

    def __repr__(self):
        return '<Billing_type %r / Backup_schedule_type %r / Backup_schedule_period %r / Monitor_period %r/ >' \
               %(self.billing_type, self.backup_schedule_type, self.backup_schedule_period, self.monitor_period)

    def __json__(self):
        return ['billing_type', 'backup_schedule_type', 'backup_schedule_period', 'monitor_period']


class GnUsers(Base):
    __tablename__ = 'GN_USERS'
    user_id = Column(String(50), primary_key=True, nullable=False)
    user_name = Column(String(20), primary_key=True, nullable=False)
    privilege = Column(String(4), nullable=True, default=None)
    tel = Column(String(15), nullable=True, default=None)
    email = Column(String(15), nullable=True, default=None)
    start_date = Column(DateTime, nullable=False, default=datetime.datetime.now())
    end_date = Column(DateTime, nullable=True, default=None)

    def __init__(self, user_id, user_name, privilege=None, tel=None, email=None, start_date=datetime.datetime.now(), end_date=None):
        self.user_id = user_id
        self.user_name = user_name
        self.privilege = privilege
        self.tel = tel
        self.email = email
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return "<GnUsers(user_id='%r', user_name='%r', privilege='%r', tel='%r', email='%r', start_date='%r', end_date='%r')>" \
               % (self.user_id, self.user_name, self.privilege, self.tel, self.email, self.start_date, self.end_date)


class GnTeam(Base):
    __tablename__ = 'GN_TEAM'
    team_code = Column(String(10), primary_key=True, nullable=False)
    team_name = Column(String(50), nullable=True, default=None)
    author_id = Column(String(50), nullable=True, default=None)
    cpu_quota = Column(Integer, nullable=True, default=None)
    mem_quota = Column(Integer, nullable=True, default=None)
    disk_quota = Column(Integer, nullable=True, default=None)
    create_date = Column(DateTime, nullable=False, default=datetime.datetime.now())

    def __init__(self, team_code, team_name, author_id, cpu_quota, mem_quota, disk_quota, create_date):
        self.team_code = team_code
        self.team_name = team_name
        self.author_id = author_id
        self.cpu_quota = cpu_quota
        self.mem_quota = mem_quota
        self.disk_quota = disk_quota
        self.create_date = create_date

    def __repr__(self):
        return "<GnTeam(team_code='%r', team_name='%r', author_id='%r', cpu_quota='%r'," \
               " mem_quota='%r', disk_quota='%r', create_date='%r')>" \
               % (self.team_code, self.team_name, self.author_id, self.cpu_quota, self.mem_quota , self.disk_quota, self.create_date)

class GnErrorHist(Base):
    __tablename__='GN_ERROR_HIST'
    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(String(10), primary_key=False, nullable=False)
    action = Column(String(10), primary_key=False, nullable=False)
    team_code = Column(String(10), primary_key=False, nullable=False)
    author_id = Column(String(50), primary_key=False, nullable=False)
    action_time = Column(DateTime, primary_key=False, default=datetime.datetime.now())
    solve_time = Column(DateTime, primary_key=False, nullable=True)
    solver_id = Column(String(10), primary_key=False, nullable=True)
    vm_id = Column(String(8), primary_key=False, nullable=False)
    vm_name = Column(String(50), primary_key=False, nullable=True)
    action_year = Column(String(4), primary_key=False, default=datetime.date.today().year)
    action_month = Column(String(4), primary_key=False, default=datetime.date.today().month)

    def __init__(self, type=None, action=None, team_code=None, author_id=None, solve_time=None, solver_id=None, vm_id=None, vm_name=None):
        self.type = type
        self.action = action
        self.team_code = team_code
        self.author_id = author_id
        self.solve_time = solve_time
        self.solver_id = solver_id
        self.vm_id = vm_id
        self.vm_name = vm_name

    def __repr__(self):
        return '<Type %r / Action %r / Team_code %r / Author id %r / Solve time %r / Solver name %r >' \
               %(self.type, self.action, self.team_code, self.author_id, self.solve_time, self.solver_name)

    def __json__(self):
        return ['id', 'type', 'action','action_time','team_code','author_id','solve_time','solver_name','vm_name']

# -*- coding: utf-8 -*-
__author__ = 'gncloud'

import datetime

from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Numeric, BigInteger

from HyperV.db.database import Base


# class GnController(Base):
#     __tablename__ = 'GN_CLUSTER'
#     controller_id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
#     controller_name = Column(String(50), nullable=True, default=None)
#     ip = Column(String(20), nullable=True, default=None)
#     port = Column(Integer, nullable=True, default=None)
#     type = Column(String(10), nullable=True, default=None)
#
#     def __init__(self, controller_name, ip, port, type):
#         self.controller_name = controller_name
#         self.ip = ip
#         self.port = port
#         self.type = type
#
#     def __repr__(self):
#         return "<GnController(controller_id='%r', controller_name='%r', ip='%r', port='%r', type='%r')>" \
#                % (self.controller_id, self.controller_name, self.ip, self.port, self.type)

class GnImagesPool(Base):
    __tablename__ = 'GN_IMAGES_POOL'
    host_id = Column(String(8), primary_key=True, nullable=False, unique=True)
    id = Column(String(8), nullable=False, unique=True)
    type = Column(String(10), nullable=True, default=None)
    local_path = Column(String(200), nullable=True, default=None)
    nas_path = Column(String(200), nullable=True, default=None)
    manager_path =  Column(String(200), nullable=True, default=None)

    def __init__(self, host_id ,type ,local_path, nas_path, manager_path):
        self.id = id
        self.type = type
        self.local_path = local_path
        self.nas_path = nas_path
        self.host_id = host_id
        self.manager_path = manager_path

    def __repr__(self):
        return "<GnImagesPool(_hostid='%r', type='%r', local_path='%r', nas_path='%r', manager_path = '%r')>" \
               % (self._hostid, self.type, self.local_path, self.nas_path, self.manager_path)


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


class GnEndPointMap(Base):
    __tablename__ = 'Gn_ENDPOINT_MAP'
    controller_id = Column(String(8), primary_key=True, nullable=False)
    host_id = Column(String(8),primary_key=True, nullable=False, default='0')

    def __init__(self, controller_id, host_id):
        self.controller_id = controller_id
        self.host_id = host_id

    def __repr__(self):
        return "<GnEndPointMap(controller_id='%r', host_id='%r')>" \
               % (self.controller_id, self.host_id)


class GnContainers(Base):
    __tablename__ = 'GN_CONTAINERS'
    id = Column(String(8), primary_key=True, nullable=False, unique=True)
    name = Column(String(50), nullable=True, default=None)
    tag = Column(String(100), nullable=True, default=None)
    internal_id = Column(String(100), nullable=True, default=None)
    internal_name = Column(String(100), nullable=True, default=None)
    host_id = Column(String(100), nullable=True, default=None)
    # cpu = Column(Integer, nullable=True, default=None)
    # memory = Column(Integer, nullable=True, default=None)
    # disk = Column(Integer, nullable=True, default=None)
    cpu = Column(BigInteger, nullable=True, default=None)
    memory = Column(BigInteger, nullable=True, default=None)
    disk = Column(BigInteger, nullable=True, default=None)
    team_code = Column(String(10), nullable=True, default=None)
    author_id = Column(String(3), nullable=True, default=None)
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    start_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    stop_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    status = Column(String(10), nullable=True, default=None)  # running, starting, error, stop, stoping, create, delete

    def __init__(self, id, name, tag, internal_id,
                 internal_name, host_id, cpu, memory, disk,
                 team_code, author_id, create_time, start_time, stop_time, status):
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
        return "<GNContainers" \
               "(controller_id='%r', name='%r', tag='%r', " \
               "internal_id='%r', internal_name='%r',host_id='%r',cpu='%r'," \
               "memory='%r',disk='%r',team_code='%r',author_id='%r'," \
               "create_time='%r',start_time='%r',stop_time='%r',status='%r' )" \
               % (self.id, self.name, self.tag, self.internal_id,
                  self.internal_name, self.host_id, self.cpu,
                  self.memory, self.disk, self.team_code,
                  self.author_id, self.create_time, self.start_time,
                  self.stop_time, self.status)


class GnContainerDetail(Base):
    __tablename__ = 'GN_CONTAINER_DETAIL'
    id = Column(String(8), primary_key=True, nullable=False)
    arg_type = Column(String(10), primary_key=True, nullable=False)
    argument = Column(String(200), primary_key=True, nullable=False)
    description = Column(String(300), nullable=False, default=None)

    def __init__(self, id, arg_type, argument, description):
        self.id = id
        self.arg_type = arg_type
        self.argument = argument
        self.description = description

    def __repr__(self):
        return "<GnContainerDetail(id='%r', arg_type='%r', argument='%r', description='%r')>" \
               % (self.id, self.arg_type, self.argument, self.description)


class GnContainerImages(Base):
    __tablename__ = 'GN_CONTAINER_IMAGES'
    id = Column(String(8), primary_key=True, nullable=False)
    name = Column(String(50), nullable=False)
    icon = Column(String(100), nullable=True, default=None)
    internal_id = Column(String(100), nullable=True, default=None)
    internal_name = Column(String(100), nullable=True, default=None)
    team_code = Column(String(10), nullable=True, default=None)
    author_id = Column(String(15), nullable=True, default=None)
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())

    def __init__(self, id, name, icon, internal_id, internal_name, team_code, author_id, create_time):
        self.id = id
        self.name = name
        self.icon = icon
        self.internal_id = internal_id
        self.internal_name = internal_name
        self.team_code = team_code
        self.author_id = author_id
        self.create_time = create_time

    def __repr__(self):
        return "<GnContainerImages(id='%r', name='%r',icon='%r',internal_id='%r', internal_name='%r'," \
               "team_code='%r',author_id='%r', create_time='%r' )>" \
               % (self.id, self.name, self.icon,self.internal_id, self.internal_name, self.team_code, self.author_id, self.create_time)



class GnDepts(Base):
    __tablename__ = 'GN_DEPTS'
    dept_code = Column(String(3), primary_key=True, nullable=False)
    dept_name = Column(String(50), nullable=True, default=None)
    cpu_quota = Column(BigInteger, nullable=True, default=None)
    mem_quota = Column(BigInteger, nullable=True, default=None)
    disk_quota = Column(BigInteger, nullable=True, default=None)
    # cpu_quota = Column(Integer, nullable=True, default=None)
    # mem_quota = Column(Integer, nullable=True, default=None)
    # disk_quota = Column(Integer, nullable=True, default=None)

    def __init__(self, dept_code, dept_name=None, cpu_quota=None, mem_quota=None, disk_quota=None):
        self.dept_code = dept_code
        self.dept_name = dept_name
        self.cpu_quota = cpu_quota
        self.mem_quota = mem_quota
        self.disk_quota = disk_quota

    def __repr__(self):
        return "<GnDepts(dept_code='%r', dept_name='%r', cpu_quota='%r', mem_quota='%r', disk_quota='%r')>" \
               % (self.dept_code, self.dept_name, self.cpu_quota, self.mem_quota, self.disk_quota)


class GnHostMachines(Base):
    __tablename__ = 'GN_HOST_MACHINES'
    id = Column(String(100), primary_key=True, nullable=False)
    name = Column(String(100), nullable=True, default='')
    ip = Column(String(100), nullable=True, default='')
    type = Column(String(10), nullable=True, default='')
    cpu = Column(BigInteger, nullable=True, default=None)
    mem = Column(BigInteger, nullable=True, default=None)
    disk = Column(BigInteger, nullable=True, default=None)

    host_agent_port = Column(Integer, nullable=True, default=None)
    image_path = Column(String(200), nullable=True, default='')

    def __init__(self, id, name='', ip='', type='', cpu=None, mem=None, disk=None, host_agent_port=None, image_path = None):
        self.id = id
        self.name = name
        self.ip = ip
        self.type = type
        self.cpu = cpu
        self.mem = mem
        self.disk = disk
        self.host_agent_port = host_agent_port
        self.image_path = image_path

    def __repr__(self):
        return "<GnHostMachines(id='%r', name='%r', ip='%r', type='%r', cpu='%r', mem='%r', disk='%r', max_cpu='%r', max_mem='%r', max_disk='%r',host_agent_port='%r', image_path='%r')>" \
               % (self.id, self.name, self.ip, self.type, self.cpu, self.mem, self.disk, self.max_cpu, self.max_mem, self.max_disk, self.host_agent_port, self.image_path)


class GnHostMonitor(Base):
    __tablename__ = 'GN_HOST_MONITOR'
    vm_id = Column(String(100), primary_key=True, nullable=False)
    cpu_usage = Column(DECIMAL(11, 4), nullable=True, default=None)
    mem_usage = Column(DECIMAL(11, 4), nullable=True, default=None)
    disk_usage = Column(DECIMAL(11, 4), nullable=True, default=None)
    net_usage = Column(DECIMAL(11, 4), nullable=True, default=None)

    def __init__(self, vm_id, time_stamp, cpu_usage, mem_usage, disk_usage, net_usage):
        self.vm_id = vm_id
        self.time_stamp = time_stamp
        self.cpu_usage = cpu_usage
        self.mem_usage = mem_usage
        self.disk_usage = disk_usage
        self.net_usage = net_usage

    def __repr__(self):
        return "<GnHostMonitor(vm_id='%r', cpu_usage='%r', mem_usage='%r', disk_usage='%r', net_usage='%r')>" \
               % (self.vm_id, self.cpu_usage, self.mem_usage, self.disk_usage, self.net_usage)


class GnHostMonitorHist(Base):
    __tablename__ = 'GN_HOST_MONITOR_HIST'
    vm_id = Column(String(100), primary_key=True, nullable=False)
    time_stamp = Column(DateTime, primary_key=True, nullable=False, default=datetime.datetime.utcnow)
    cpu_usage = Column(DECIMAL(11, 4), nullable=True, default=None)
    mem_usage = Column(DECIMAL(11, 4), nullable=True, default=None)
    disk_usage = Column(DECIMAL(11, 4), nullable=True, default=None)
    net_usage = Column(DECIMAL(11, 4), nullable=True, default=None)

    def __init__(self, vm_id, time_stamp, cpu_usage, mem_usage, disk_usage, net_usage):
        self.vm_id = vm_id
        self.time_stamp = time_stamp
        self.cpu_usage = cpu_usage
        self.mem_usage = mem_usage
        self.disk_usage = disk_usage
        self.net_usage = net_usage

    def __repr__(self):
        return "<GnHostMonitorHist(vm_id='%r', time_stamp='%r', cpu_usage='%r', mem_usage='%r', disk_usage='%r', net_usage='%r')>" \
               % (self.vm_id, self.time_stamp, self.cpu_usage, self.mem_usage, self.disk_usage, self.net_usage)


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


class GnVmImages(Base):
    __tablename__ = 'GN_VM_IMAGES'
    id = Column(String(8), primary_key=True, nullable=False)
    name = Column(String(50), nullable=False, default='')
    filename = Column(String(100), nullable=True, default='')
    type = Column(String(10), nullable=False, default='')
    sub_type = Column(String(10), nullable=False, default='')
    icon = Column(String(100), nullable=True, default=None)
    os = Column(String(10), nullable=True, default=None)
    os_ver = Column(String(20), nullable=True, default=None)
    os_subver = Column(String(20), nullable=True, default=None)
    os_bit = Column(String(2), nullable=True, default=None)
    team_code = Column(String(10), nullable=True, default=None)
    author_id = Column(String(15), nullable=True, default=None)
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    status = Column(String(10), nullable=True, default=None)
    ssh_id = Column(String(10), nullable=True, default=None)
    pool_id = Column(String(8), nullable=True, default=None)
    host_id = Column(String(8), nullable=True, default=None)

    def __init__(self, id='', image_name='', filename='',
                 type='', sub_type='', icon=None,
                 os=None, os_ver=None, os_subver=None, os_bit=None,
                 team_code=None, author_id=None, create_time=datetime.datetime.now(),
                 status=None, ssh_id=None,pool_id=None,host_id=None):
        self.id = id
        self.name = image_name
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
        self.create_time = create_time
        self.status = status
        self.ssh_id = ssh_id
        self.pool_id = pool_id
        self.host_id = host_id

    def __repr__(self):
        return "<GnVmImages(" \
               "id='%r', name='%r', filename='%r', " \
               "type='%r', sub_type='%r', icon='%r', " \
               "os='%r', os_ver='%r', os_subver='%r', os_bit='%r', team_code='%r', author_id='%r',create_time='%r', status='%r', ssh_id='%r', pool_id='%r', host_id='%r')>" \
               % (self.id, self.name, self.filename, self.type,
                  self.sub_type, self.icon, self.os, self.os_ver, self.os_subver,
                  self.os_bit, self.team_code, self.author_id, self.create_time, self.status, self.ssh_id, self.pool_id, self.host_id)

'''
    def __json__(self):
        return ['id', 'name', 'filename', 'type','sub_type', 'icon', 'os', 'os_ver', 'os_bit',
                'team_code', 'author_id', 'create_time', 'status', 'ssh_id']
'''

class GnVmMachines(Base):
    __tablename__ = 'GN_VM_MACHINES'
    id = Column(String(8), primary_key=True, nullable=False)
    name = Column(String(50), nullable=True, default='')
    tag = Column(String(100), nullable=True, default='')
    type = Column(String(10), nullable=False, default='')
    internal_id = Column(String(100), nullable=True, default='')
    internal_name = Column(String(100), nullable=True, default='')
    host_id = Column(String(100), nullable=False, default=None)
    ip = Column(String(20), nullable=True, default=None)
    cpu = Column(BigInteger, nullable=False)
    memory = Column(BigInteger, nullable=False)
    disk = Column(BigInteger, nullable=False)
    # cpu = Column(Integer, nullable=False)
    # memory = Column(Integer, nullable=False)
    # disk = Column(Integer, nullable=False)
    os = Column(String(10), nullable=True, default=None)
    os_ver = Column(String(20), nullable=True, default=None)
    os_sub_ver = Column(String(20), nullable=True, default=None)
    os_bit = Column(String(2), nullable=True, default=None)
    team_code = Column(String(10), nullable=True, default=None)
    author_id = Column(String(50), nullable=True, default=None)
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    start_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    stop_time = Column(DateTime, nullable=False, default=datetime.datetime.now())
    status = Column(String(10), nullable=True, default=None)
    hyperv_pass = Column(String(50), nullable=True, default='')
    image_id = Column(String(8), nullable=False, default=None)
    size_id = Column(String(8), nullable=False, default=None)

    def __init__(self,
                 id, name='', tag='', type='',
                 internal_id='', internal_name='',
                 host_id='', ip='',
                 cpu=None, memory=None, disk=None,
                 os=None, os_ver=None, os_sub_ver=None, os_bit=None,
                 team_code=None, author_id=None,
                 create_time=datetime.datetime.now(), start_time=datetime.datetime.now(),
                 stop_time=datetime.datetime.now(),
                 status=None, hyperv_pass=None, image_id=None, size_id=None):
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
        self.create_time = create_time
        self.start_time = start_time
        self.stop_time = stop_time
        self.status = status
        self.hyperv_pass = hyperv_pass
        self.image_id = image_id
        self.size_id = size_id


    def __repr__(self):
        return "<GnVmMachines(" \
               "id='%r', name='%r', tag='%r', type='%r', internal_id='%r', internal_name='%r'" \
               "host_id='%r', ip='%r', cpu='%r', memory='%r', disk='%r', os='%r', " \
               "os_ver='%r', os_sub_ver='%r', os_bit='%r', team_code='%r', author_id='%r', " \
               "create_time='%r', start_time='%r', stop_time='%r', status='%r', hyperv_pass='%r', image_id='%r')>" \
               % (self.id, self.name, self.tag, self.type, self.internal_id, self.internal_name,
                  self.host_id, self.ip, self.cpu, self.memory, self.disk,
                  self.os, self.os_ver, self.os_sub_ver, self.os_bit, self.team_code, self.author_id,
                  self.create_time, self.start_time, self.stop_time, self.status, self.hyperv_pass, self.image_id)


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
        return "<GnMonitor( id='%r', type='%r', cpu_usage='%r', mem_usage='%r', disk_usage='%r'," \
               "net_usage='%r')>" \
               % (self.id, self.type, self.cpu_usage, self.mem_usage, self.disk_usage, self.net_usage)

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

    def __init__(self, id=id, type=type, cur_time = None, cpu_usage=None, mem_usage=None, disk_usage=None, net_usage=None):
        self.id = id
        self.type = type
        self.cur_time = cur_time
        self.cpu_usage = cpu_usage
        self.mem_usage = mem_usage
        self.disk_usage = disk_usage
        self.net_usage = net_usage

    def __repr__(self):
        return "<GnMonitorHist(id='%r',type='%r', cur_time='%r',cpu_usage='%r', mem_usage='%r', disk_usage='%r'," \
               "net_usage='%r'" \
               % (self.id, self.type, self.cur_time, self.cpu_usage, self.mem_usage, self.disk_usage, self.net_usage)

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
    cause = Column(String(1000), primary_key=False, nullable=True)

    def __init__(self, type=None, action=None, team_code=None, author_id=None, solve_time=None, solver_id=None,
                 vm_id=None, vm_name=None, cause=None):
        self.type = type
        self.action = action
        self.team_code = team_code
        self.author_id = author_id
        self.solve_time = solve_time
        self.solver_id = solver_id
        self.vm_id = vm_id
        self.vm_name = vm_name
        self.cause = cause

    def __repr__(self):
        return '<Type %r / Action %r / Team_code %r / Author id %r / Solve time %r / Solver name %r >' \
               %(self.type, self.action, self.team_code, self.author_id, self.solve_time, self.solver_name)

    def __json__(self):
        return ['id', 'type', 'action','action_time','team_code','author_id','solve_time','solver_name','vm_name']



class GnBackup(Base):
    __tablename__ = 'GN_BACKUP'
    vm_id = Column(String(8), primary_key=True, nullable=False)
    backup_time = Column(DateTime, nullable=True, default=None)
    team_code = Column(String(10), nullable=True, default='')
    author_id = Column(String(50), nullable=True, default='')
    vm_type = Column(String(10), nullable=True, default='')
    vm_name = Column(String(50), nullable=True, default='')
    team_name = Column(String(10), nullable=True, default='')
    author_name = Column(String(20), nullable=True, default='')

    def __init__(self, vm_id, backup_time=None, team_code=None, author_id=None, vm_type=None,
                 vm_name=None, team_name=None, author_name=None):
        self.vm_id = vm_id
        self.backup_time = backup_time
        self.team_code = team_code
        self.author_id = author_id
        self.vm_type = vm_type
        self.vm_name = vm_name
        self.team_name = team_name
        self.author_name = author_name

    def __repr__(self):
        return "<GnBackup(vm_id='%r', backup_time='%r', team_code='%r', author_id='%r', vm_type='%r', vm_name='%r', team_name='%r', author_name='%r' " \
               % (self.vm_id, self.backup_time, self.team_code, self.author_id, self.vm_type, self.vm_name, self.team_name, self.author_name)


class GnBackupHist(Base):
    __tablename__ = 'GN_BACKUP_HIST'
    vm_id = Column(String(8), primary_key=True, nullable=False)
    filename = Column(String(150), primary_key=True, nullable=False, default='')
    backup_time = Column(DateTime, nullable=True, default=datetime.datetime.now())
    vm_type = Column(String(10), nullable=True, default='')
    host_ip = Column(String(50), nullable=True, default='')

    def __init__(self, vm_id, filename, backup_time, vm_type=None, host_ip=None):
        self.vm_id = vm_id
        self.filename = filename
        self.backup_time = backup_time
        self.vm_type = vm_type
        self.host_ip = host_ip

    def __repr__(self):
        return "<GnBackupHist(vm_id='%r', filename='%r', backup_time='%r', vm_type='%r', host_ip='%r' " \
               % (self.vm_id, self.filename, self.backup_time, self.vm_type, self.host_ip)


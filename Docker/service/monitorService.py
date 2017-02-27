# -*- coding: utf-8 -*-
__author__ = 'jhjeon'
import subprocess
from Docker.db.models import GnVmMachines, GnMonitorHist, GnMonitor, GnDockerContainers, GnHostMachines
from Docker.util.logger import logger

KILO_TO_BYE=1024
MEGA_TO_BYTE=1048576
GIGA_TO_BYTE=1073741824
TERA_TO_BYTE=1099511627776


def convert_to_byte(unit, mem):
    convert_byte = 0.0
    if unit == 'MiB':
        convert_byte = mem * MEGA_TO_BYTE
    elif unit == 'GiB':
        convert_byte = mem * GIGA_TO_BYTE
    elif unit == 'kB':
        convert_byte = mem * KILO_TO_BYE
    elif unit == 'TiB':
        convert_byte = mem * TERA_TO_BYTE
    else:
        convert_byte = mem
    return convert_byte


def service_monitoring(sql_session):
    service_list = sql_session.query(GnVmMachines).filter(GnVmMachines.type == "docker") \
        .filter(GnVmMachines.status == "Running").all()
    try:
        for service in service_list:
            cpu_usage = 0.0
            mem_usage = 0.0
            disk_usage = 0.0
            net_usage = 0.0
            worker_count = 0
            container_list = sql_session.query(GnDockerContainers).filter(GnDockerContainers.service_id == service.id).all()
            for container in container_list:
                container_host = sql_session.query(GnHostMachines).filter(GnHostMachines.id == container.host_id).first()
                ip=''
                port='2375'
                if container_host.ip.find(':') >=0:
                    ip = container_host.ip.split(':')[0]
                    port = container_host.ip.split(':')[1]
                else:
                    ip = container_host.ip
                docker_stat_cmd = 'docker -H %s:%s stats --all --no-stream | grep "$(docker ps --filter=name=%s --quiet)"' \
                                  % (ip, port, container.internal_name)

                result = subprocess.check_output (docker_stat_cmd , shell=True)
                result = result.split("\r\n")
                for line in result:
                    line = line.split()
                    if len(line) < 2:
                        continue
                    elif line[0] == "docker":
                        continue
                    elif line[0] == "CONTAINER":
                        continue
                    else:
                        # CPU 사용량 가지고 오기
                        cpu_usage += round(float(line[1][:-1]), 4)
                        # Memory 사용량 가지고 오기
                        unit = line[3]
                        mem_byte = 0.0
                        mem = float(line[2])
                        mem_byte = convert_to_byte(unit, mem)
                        mem_usage += round(mem_byte,4)
                        # container_info['DISK_USAGE'] = float(line[13])/float(line[16])
                        # 디스크 사용량 가지고 오기 => change "no disk usage of docker"
                        #disk_usage += round(float(line[13])/1000.0, 4)
                        # 네트워크 정보 가지고 오기
                        unit = line[9]
                        net = float(line[8])
                        net_byte = convert_to_byte(unit, net)
                        net_usage += round(net_byte,4)

            if worker_count > 0:
                cpu_usage = (cpu_usage/worker_count)
                mem_usage = (mem_usage/worker_count)
                net_usage = (net_usage/worker_count)
            else:
                cpu_usage = 0.0
                mem_usage = 0.0
                net_usage = 0.0
            #disk_usage = (disk_usage/2.0)

            vm_monitor_hist = GnMonitorHist(
                id=service.id, type="docker", cpu_usage=cpu_usage, mem_usage=mem_usage,
                disk_usage=disk_usage, net_usage=net_usage)
            sql_session.add(vm_monitor_hist)
            gnMontor_info = sql_session.query(GnMonitor).filter(GnMonitor.id == service.id).one_or_none()
            if gnMontor_info is None:
                vm_monitor = GnMonitor(
                    id=service.id, type="docker", cpu_usage=cpu_usage/2.0, mem_usage=mem_usage/2.0,
                    disk_usage=disk_usage/2.0, net_usage=net_usage)
                sql_session.add(vm_monitor)
            else:
                gnMontor_info.type = "docker"
                gnMontor_info.cpu_usage = cpu_usage
                gnMontor_info.mem_usage = mem_usage
                gnMontor_info.disk_usage = disk_usage
                gnMontor_info.net_usage = net_usage
            sql_session.commit()
        logger.info("도커 서비스 상태 업데이트 완료")
    except:
        logger.exception("에러 발생")
        sql_session.rollback()
    else:
        pass
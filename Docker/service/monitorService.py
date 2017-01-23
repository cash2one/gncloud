# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from datetime import datetime
from pexpect import pxssh
from Docker.db.models import GnVmMachines, GnMonitorHist, GnMonitor
from Docker.util.logger import logger


def service_monitoring(sql_session):
    service_list = sql_session.query(GnVmMachines).filter(GnVmMachines.type == "docker") \
        .filter(GnVmMachines.status == "Running").all()
    try:
        for service in service_list:
            cpu_usage = 0.0
            mem_usage = 0.0
            disk_usage = 0.0
            net_usage = 0.0
            for container in service.gnDockerContainers:
                container_host = container.gnHostMachines
                ssh = pxssh.pxssh()
                ssh.login(container_host.ip, "root", "docker")

                docker_stat_cmd = "docker stats --all --no-stream | grep \"$(docker ps --filter=name=%s --quiet)\"" % container.internal_name
                ssh.sendline(docker_stat_cmd)
                ssh.prompt()
                result = ssh.before
                result = result.split("\r\n")
                for line in result:
                    line = line.split()
                    if len(line) < 2:
                        pass
                    elif line[0] == "docker":
                        pass
                    elif line[0] == "CONTAINER":
                        pass
                    else:
                        # CPU 사용량 가지고 오기
                        cpu_usage += round(float(line[1][:-1]), 4)
                        # Memory 사용량 가지고 오기
                        mem_usage += round(float(line[7][:-1]), 4)
                        # container_info['DISK_USAGE'] = float(line[13])/float(line[16])
                        # 디스크 사용량 가지고 오기 => change "no disk usage of docker"
                        #disk_usage += round(float(line[13])/1000.0, 4)
                        # 네트워크 정보 가지고 오기
                        net_usage += float(line[8])
                ssh.close()
            cpu_usage = (cpu_usage/2.0)
            mem_usage = (mem_usage/2.0)
            #disk_usage = (disk_usage/2.0)
            net_usage = (net_usage/2.0)
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
        sql_session.remove()
    except:
        logger.exception("에러 발생")
        sql_session.remove()
    else:
        pass

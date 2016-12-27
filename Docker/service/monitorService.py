# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import re
from pexpect import pxssh
from docker.api.client import APIClient
from db.database import db_session
from db.models import GnHostMachines, GnVmMachines
# dest: "http://192.168.22.23:5000/"


class MonitorService(object):

    def __init__(self, sql_session):
        self.list = sql_session.query(GnVmMachines).filter(GnVmMachines.type == "docker").filter(GnVmMachines.status == "running").all()

    def node_monitoring(self):
        for service in self.list:
            for container in service.gnDockerContainers:
                container_host = container.gnHostMachines
                ssh = pxssh.pxssh()
                ssh.login(container_host.ip, "root", "docker")

                docker_stat_cmd = "docker stats --all --no-stream | grep %s" % container.internal_id[0:12]
                ssh.sendline(docker_stat_cmd)
                ssh.prompt()
                result = ssh.before
                result = result.split("\r\n")
                for line in result:
                    container_info = {}
                    line = line.split()
                    if len(line) == 0:
                        pass
                    elif line[0] == "docker":
                        pass
                    else:
                        container_info['CONTAINER'] = line[0]
                        # CPU 사용량 가지고 오기
                        container_info['CPU_USAGE'] = round(float(line[1][:-1]), 4)
                        # Memory 사용량 가지고 오기
                        container_info['MEM_USAGE'] = round(float(line[7][:-1]), 4)
                        # container_info['DISK_USAGE'] = float(line[13])/float(line[16])
                        # 디스크 사용량 가지고 오기
                        container_info['DISK_USAGE'] = round(float(line[13])/1000.0, 4)
                        # 네트워크 정보 가지고 오기
                        container_info['NET_USAGE'] = float(line[8])
                    print container_info
                ssh.close()


mservice = MonitorService(db_session)
mservice.node_monitoring()

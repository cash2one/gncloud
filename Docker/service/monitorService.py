# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import re
from pexpect import pxssh
from docker.api.client import APIClient
from db.database import db_session
from db.models import GnHostMachines, GnVmMachines
# dest: "http://192.168.22.23:5000/"


class MonitorService(object):

    def __init__(self, sql_session, dest, user, passwd):
        self.client = APIClient(base_url=dest)
        self.pure_url = dest.split(':', 2)[1][2:]
        self.ssh = pxssh.pxssh()
        self.ssh.login(self.pure_url, user, passwd)
        self.sql_session = sql_session

    def node_monitoring(self):
        for container in self.client.containers():
            response = self.client.stats(container, stream=None)
            cont = self.client.inspect_container(container)
            id = cont['Id']
            service = GnVmMachines.query.filter_by(type="docker", internal_id=id).first()
            # print service
            # ---------------------------------------
            #!/bin/bash
            #
            # ip=$2
            # if [ $1 = "cpu" ]; then
            # ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null centos@${ip}  top -bn2 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}'
            # elif [ $1 = "mem" ]; then
            # ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null centos@${ip} free | grep Mem | awk '{ print(100 - ($4/$2 * 100.0)) }'
            # elif [ $1 = "disk" ]; then
            # ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null centos@${ip} df -P | grep -v ^Filesystem | awk '{sum += $3} END { print sum/1024}'
            # elif [ $1 = "net" ]; then
            # ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null centos@${ip} netstat -i | grep eth0 | awk '{print $3}'
            # fi
            #
            # response = self.client.stats(container, stream=None)
            # cont = self.client.inspect_container(container)
            # id = cont['Id']
            # # print 'URL = ' + self.client.base_url + ', Name : ' + cont['Name'] + ', Status : ' + cont['State']['Status'] + ', ID : ' + id
            # # print "cpu_user : " + str(response['cpu_stats']['cpu_usage']['usage_in_usermode']) + ', total :' + str(response['cpu_stats']['cpu_usage']['total_usage']) + ', kernel : ' + str(response['cpu_stats']['cpu_usage']['usage_in_kernelmode'])
            # # print "memory_user : " + str(response['memory_stats']['usage']) + ', memory_limit : ' + str(response['memory_stats']['limit'])
            # cmd = 'docker exec ' + id + ' /bin/df -h | grep docker | awk \'{print $2, $3, $4, $5}\''
            # self.ssh.sendline(cmd)
            # self.ssh.prompt()
            # print self.ssh.before
            # ---------------------------------------

            # print 'URL = ' + self.client.base_url + ', Name : ' + cont['Name'] + ', Status : ' + cont['State']['Status'] + ', ID : ' + id

            docker_stat_cmd = "docker stats --all --no-stream"
            self.ssh.sendline(docker_stat_cmd)
            self.ssh.prompt()
            result = self.ssh.before
            result = result.split("\r\n")
            check_stats = False
            for line in result:
                container_info = {}
                container_info['CONTAINER'] = line[0]
                container_info['CPU'] = line[1]
                container_info['MEM_USAGE'] = line[2]
                container_info['MEM_USAGE_UNIT'] = line[3]
                line = line.split()
                if check_stats and len(line) != 0:
                    print line
                if check_stats is False and line[0] == "CONTAINER":
                    check_stats = True

            # todo. CPU 사용량 가지고 오기
            # print "cpu_user : " + str(response['cpu_stats']['cpu_usage']['usage_in_usermode']) + ', total :' + str(response['cpu_stats']['cpu_usage']['total_usage']) + ', kernel : ' + str(response['cpu_stats']['cpu_usage']['usage_in_kernelmode'])
            # todo. Memory 사용량 가지고 오기
            # print "memory_user : " + str(response['memory_stats']['usage']) + ', memory_limit : ' + str(response['memory_stats']['limit'])
            # Disk 사용량 가지고 오기
            # disk_cmd = 'docker exec ' + id + ' /bin/df -h | grep docker | awk \'{print $2, $3, $4, $5}\''
            # self.ssh.sendline(disk_cmd)
            # self.ssh.prompt()
            # disk_info = self.ssh.before
            # disk_info = disk_info.split("\r\n", 2)[1]
            # disk_info = disk_info.split()
            # # print disk_usage
            # use_mem = float(self.get_kbytes(disk_info[1]))
            # total_mem = float(self.get_kbytes(disk_info[0]))
            # disk_usage = round(use_mem/total_mem, 4)
            # print "disk_usage: %s" % disk_usage
            # todo. 네트워크 정보 가지고 오기

            # print 'URL = ' + self.client.base_url + ', Name : ' + cont['Name'] + ', Status : ' + cont['State']['Status'] + ', ID : ' + id
            # cpu_cmd = "docker exec " + id + " top -bn2 | grep \"Cpu(s)\" | sed \"s/.*, *\([0-9.]*\)%* id.*/\1/\" | awk '{print 100 - $1}'"
            # self.ssh.sendline(cpu_cmd)
            # self.ssh.prompt()
            # cpu_use = (str(self.ssh.before)).split("\r\n")[3]
            # print "cpu: " + cpu_use
            # print "cpu_user : " + str(response['cpu_stats']['cpu_usage']['usage_in_usermode']) + ', total :' + str(response['cpu_stats']['cpu_usage']['total_usage']) + ', kernel : ' + str(response['cpu_stats']['cpu_usage']['usage_in_kernelmode'])

            # mem_cmd = "docker exec %s free | grep Mem | awk '{ print(100 - ($4/$2 * 100.0)) }'" % id
            # self.ssh.sendline(mem_cmd)
            # self.ssh.prompt()
            # print "mem: " + self.ssh.before
            # print "memory_user : " + str(response['memory_stats']['usage']) + ', memory_limit : ' + str(response['memory_stats']['limit'])

            # disk_cmd = "docker exec %s df -P | grep -v ^Filesystem | awk '{sum += $3} END { print sum/1024}'" % id
            # self.ssh.sendline(disk_cmd)
            # self.ssh.prompt()
            # print "disk: " + self.ssh.before

            # net_cmd = "docker exec %s netstat -i | grep eth0 | awk '{print $3}'" % id
            # self.ssh.sendline(net_cmd)
            # self.ssh.prompt()
            # print "net: " + self.ssh.before

            # gnMontor_info = sql_session.query(GnMonitor).filter(GnMonitor.id == list.id).one_or_none()
            # if gnMontor_info is None:
            #     vm_monitor = GnMonitor(id=list.id, type="kvm", cpu_usage=cpu_use, mem_usage=mem_use, disk_usage=disk_use, net_usage=net_use)
            #     sql_session.add(vm_monitor)
            # else:
            #     gnMontor_info.cpu_usage = cpu_use
            #     gnMontor_info.mem_usage = mem_use
            #     gnMontor_info.disk_usage = disk_use
            #     gnMontor_info.net_usage = net_use

    def get_kbytes(self, size_string):
        try:
            size_string = size_string.lower().replace(',', '')
            size = re.search('^(\d+)[a-z]', size_string).groups()[0]
            suffix = re.search('^\d+([kmgtp])', size_string).groups()[0]
        except AttributeError:
            raise ValueError("Invalid Input")
        if suffix == 'm':
            size = int(size) * 1024
        elif suffix == 'g':
            size = int(size) * 1024 * 1024
        elif suffix == 't':
            size = int(size) * 1024 * 1024 * 1024
        return size

    def close(self):
        self.ssh.logout()
        self.client.close()


# mservice = MonitorService(db_session, "http://192.168.0.201:2375", "root", "docker")
# mservice.node_monitoring()
# mservice.close()

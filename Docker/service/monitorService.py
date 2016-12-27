# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from pexpect import pxssh
from docker.api.client import APIClient
from db.models import GnHostMachines

# dest: "http://192.168.22.23:5000/"


class MonitorService(object):

    def __init__(self, dest, user, passwd):
        self.client = APIClient(base_url=dest)
        self.pure_url = dest.split(':', 2)[1][2:]
        self.ssh = pxssh.pxssh()
        self.ssh.login(self.pure_url, user, passwd)

    def node_monitoring(self):
        for container in self.client.containers():
            response = self.client.stats(container, stream=None)
            cont = self.client.inspect_container(container)
            id = cont['Id']
            # print 'URL = ' + self.client.base_url + ', Name : ' + cont['Name'] + ', Status : ' + cont['State']['Status'] + ', ID : ' + id
            # print "cpu_user : " + str(response['cpu_stats']['cpu_usage']['usage_in_usermode']) + ', total :' + str(response['cpu_stats']['cpu_usage']['total_usage']) + ', kernel : ' + str(response['cpu_stats']['cpu_usage']['usage_in_kernelmode'])
            # print "memory_user : " + str(response['memory_stats']['usage']) + ', memory_limit : ' + str(response['memory_stats']['limit'])
            cmd = 'docker exec ' + id + ' /bin/df -h | grep docker | awk \'{print $2, $3, $4, $5}\''
            self.ssh.sendline(cmd)
            self.ssh.prompt()
            print self.ssh.before

    def close(self):
        self.ssh.logout()
        self.client.close()


mservice = MonitorService("http://192.168.22.21:2375", "root", "docker")
mservice.node_monitoring()
mservice.close()



    # try:
    #     lists = GnHostMachines.query.filter_by(type="docker_w").all()
    #     for list in lists:
    #         host_ip = list.ip
    #         s = pxssh.pxssh()
    #         s.login(host_ip, "root", "docker")
    #         s.sendline(config.SCRIPT_PATH+"get_vm_use.sh cpu " + list.ip + " "+list.os)
    #         s.prompt()
    #         cpu_use = (str(s.before)).split("\r\n")[3]
    #         s.sendline(config.SCRIPT_PATH+"get_vm_use.sh mem " + list.ip + " "+list.os)
    #         s.prompt()
    #         mem_use = (str(s.before)).split("\r\n")[2]
    #         s.sendline(config.SCRIPT_PATH+"get_vm_use.sh disk " + list.ip + " "+list.os)
    #         s.prompt()
    #         disk_use = (str(s.before)).split("\r\n")[2]
    #         s.sendline(config.SCRIPT_PATH+"get_vm_use.sh net " + list.ip + " "+list.os)
    #         s.prompt()
    #         net_use = (str(s.before)).split("\r\n")[2]
    #         s.logout()
    #
    #         vm_monitor_hist = GnMonitorHist(id=list.id, type="kvm", cpu_usage=cpu_use, mem_usage=mem_use, disk_usage=disk_use, net_usage=net_use)
    #         sql_session.add(vm_monitor_hist)
    #
    #         gnMontor_info = sql_session.query(GnMonitor).filter(GnMonitor.id == list.id).one_or_none()
    #         if gnMontor_info is None:
    #             vm_monitor = GnMonitor(id=list.id, type="kvm", cpu_usage=cpu_use, mem_usage=mem_use, disk_usage=disk_use, net_usage=net_use)
    #             sql_session.add(vm_monitor)
    #         else:
    #             gnMontor_info.cpu_usage = cpu_use
    #             gnMontor_info.mem_usage = mem_use
    #             gnMontor_info.disk_usage = disk_use
    #             gnMontor_info.net_usage = net_use
    #
    # except:
    #     sql_session.rollback()
    # finally:
    #     print("end")
    #     sql_session.commit()
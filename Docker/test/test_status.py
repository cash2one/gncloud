# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from pexpect import pxssh
from docker.api.client import APIClient


def dockerStats(dest):
    client = APIClient(base_url=dest)
    pure_url = dest.split(':', 2)[1][2:]
    s = pxssh.pxssh()

    login_ok = False
    if pure_url == '192.168.22.21':
        login_ok = s.login(pure_url, 'root', 'docker')
    elif pure_url == '192.168.22.22':
        login_ok = s.login(pure_url, 'root', 'docker')

    if login_ok:
        for container in client.containers():
            response = client.stats(container, stream=None)
            cont = client.inspect_container(container)
            # print json.dumps(cont,indent=4)
            id = cont['Id']
            print 'URL = ' + client.base_url + ', Name : ' + cont['Name'] + ', Status : ' + cont['State']['Status'] + ', ID : ' + id
            print "cpu_user : " + str(response['cpu_stats']['cpu_usage']['usage_in_usermode']) + ', total :' + str(response['cpu_stats']['cpu_usage']['total_usage']) + ', kernel : ' + str(response['cpu_stats']['cpu_usage']['usage_in_kernelmode'])
            print "memory_user : " + str(response['memory_stats']['usage']) + ', memory_limit : ' + str(response['memory_stats']['limit'])
            cmd='docker exec ' + id + ' /bin/df -h | grep docker | awk \'{print $2, $3, $4, $5}\''
            s.sendline(cmd)
            s.prompt()
            print s.before
        s.logout()
    client.close()

dockerStats("http://192.168.22.21:2375")

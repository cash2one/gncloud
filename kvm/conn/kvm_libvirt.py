# -*- coding: utf-8 -*-
__author__ = 'yhk'

import ConfigParser
import os
import libvirt
from pexpect import pxssh
from xml.dom import minidom
from kvm.util.config import config
from flask import  render_template

URL = config.LIBVIRT_REMOTE_URL
HOST = "192.168.0.131"
USER = "root"

def server_list():
        conn = libvirt.openReadOnly(URL)
        machine_list = []

        for id in conn.listDomainsID():
            dom = conn.lookupByID(id)
            dom.connect()
            machine_info = {}
            state, maxmem, mem, cpus, cput = dom.info()
            if state == 1:
               dom_state = "Running"
            elif state == 2:
               dom_state = "Idle"
            elif state == 3:
               dom_state = "Paused"
            elif state == 4:
               dom_state = "Shutdown"
            elif state == 5:
               dom_state = "Shutoff"
            elif state == 6:
               dom_state = "Crashed"
            else:
               dom_state = "Nostate"

            machine_info['name'] = dom.name()
            machine_info['dom_state'] = dom_state
            machine_info['memory'] = mem
            machine_info['cpus'] = cpus

            #libvirt 라리브러리로 ip 받아오는 부분
            #guest qemu_geuest_agent 서비스 실행시 문제로 인하여 차후 처리
            # raw_xml = dom.XMLDesc(0)
            # xml = minidom.parseString(raw_xml)
            # interfaceTypes = xml.getElementsByTagName('interface')
            # for interfaceType in interfaceTypes:
            #     interfaceNodes = interfaceType.childNodes
            #     for interfaceNode in interfaceNodes:
            #         if interfaceNode.nodeName[0:1] != '#':
            #             if interfaceNode.nodeName == 'mac':
            #                 for attr in interfaceNode.attributes.keys():
            #                     mac_address = interfaceNode.attributes[attr].value

            #ssh 스크립트로 직접 guest에 할당된 ip 체크
            s = pxssh.pxssh()
            s.login(HOST, USER)
            s.sendline("/root/get_ipadress.sh " + dom.name())
            s.prompt()
            if len(s.before.split()) > 2:
                machine_info['ip'] = s.before.split()[2]
            else:
                machine_info['ip'] = ""
            s.logout()
            machine_list.append(machine_info)

        conn.close()
        return machine_list

def get_ip(domainName, mac_address):
    conn = libvirt.open(URL)
    dom = conn.lookupByName(domainName)

    ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
    i=0
    for (name, val) in ifaces.iteritems():
        i += 1
        if val['addrs'] and val['hwaddr'] == mac_address:
            for ipaddr in val['addrs']:
                if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                    ip = ipaddr['addr']


    conn.close()
    return ip

def server_create(name, cpu, memory):
    try:
        #create ssh key
        s = pxssh.pxssh()
        s.login(HOST, USER)
        s.sendline("cd /var/lib/librt/sshkeys")
        s.sendline("./sshkey_coyp.sh")
        s.prompt()
        s.logout()

        #guest 생성 정보 xml 템플릿 생성
        vol = render_template(
            "volume.xml"
            ,guest_name= name
        )
        guest = render_template(
            "guest.xml"
            ,guest_name = name
            ,current_memory = memory
            ,vcpu = cpu
        )

        #create vm
        conn = libvirt.open(URL)
        ptr_POOL = conn.storagePoolLookupByName("default")

        # raw 이미지 사용시 volume.xml의 capacity가 적용됩니다
        # qcow2 이미지 사용시 최대 8G 의 qcow 이미지에 세팅되어있는 virtual size: 8.0G 로 적용되어 무조건 8G의 이미지가 생성됩니다
        # 테스트 결과 qcow 이미지를 사용해서 생성할때가 속도가 더 빠른것 같습니다
        # defaultVol = ptr_POOL.storageVolLookupByName("CentOS-7-x86_64-GenericCloud-1511.raw")
        defaultVol = ptr_POOL.storageVolLookupByName("CentOS-7-x86_64-GenericCloud.qcow2")

        ptr_POOL.createXMLFrom(vol, defaultVol, 0)
        conn.createXML(guest, 0)
        conn.close()
        return "ok"
    except IOError as errmsg:
       return errmsg



def server_change_status(vm_name , status):
    conn = libvirt.open(URL)
    ptr_VM = conn.lookupByName(vm_name)
    if status == 'suspend':
        ptr_VM.suspend()
    elif status == "reboot":
        ptr_VM.reboot()
    elif status == "resume":
        ptr_VM.resume()
    elif status == "reboot":
        ptr_VM.reboot();
    elif status == "delete":
        ptr_VM.destroy()
        ptr_POOL = conn.storagePoolLookupByName("default")
        ptr_POOL.storageVolLookupByName(vm_name + ".img").delete()
        conn.close()




# -*- coding: utf-8 -*-
from xml.etree import ElementTree

__author__ = 'yhk'

import ConfigParser
import os
import libvirt
from xml.dom import minidom
from kvm.util.config import config
from flask import  render_template
import paramiko
import datetime

URL = config.LIBVIRT_REMOTE_URL
HOST = "192.168.0.131"
USER = "root"
LOCAL_SSH_KEY_PATH = "/Users/yhk/.ssh/id_rsa"

def kvm_list():
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

            # paramiko
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(HOST, username=USER, key_filename="/Users/yhk/.ssh/id_rsa")
            stdin, stdout, stderr = ssh.exec_command('/root/get_ipadress.sh ' + dom.name())
            machine_info['ip'] = stdout.readlines()
            ssh.close()
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


def kvm_create(name, cpu, memory, disk, base_name, base_sub_type):
    try:
        # paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=LOCAL_SSH_KEY_PATH)
        stdin, stdout, stderr = ssh.exec_command('/var/lib/libvirt/initcloud/sshkey_copy.sh')
        print stdout.readlines()
        ssh.close()


        # 스냅샷 기반 유무에 따른 생성 로직 분기
        if base_sub_type == "base":
            # guest 생성 정보 xml 템플릿 생성
            vol = render_template(
                "volume.xml"
                , guest_name=name
                , disk=disk
            )
            conn = libvirt.open(URL)
            ptr_POOL = conn.storagePoolLookupByName("default")

            defaultVol = ptr_POOL.storageVolLookupByName(base_name)
            ptr_POOL.createXMLFrom(vol, defaultVol, 0)
            ptr_POOL.storageVolLookupByName(name + ".img").resize(gigaToByte(int(disk)))
        else:
            kvm_image_copy(base_name, name)

        # vm 생성
        guest = render_template(
            "guest.xml"
            ,guest_name = name
            ,current_memory = memory
            ,vcpu = cpu
        )
        conn.createXML(guest, 0)
        id = conn.lookupByName(name).UUIDString()
        conn.close()
        return id
    except IOError as errmsg:
        print(str(errmsg))


def kvm_change_status(vm_name, status, datetime, URL):
    conn = libvirt.open(URL)
    ptr_VM = conn.lookupByName(vm_name)
    if status == 'start':
        ptr_VM.resume()
    elif status == "suspend":
        ptr_VM.suspend()
    elif status == "resume":
        ptr_VM.resume()
    elif status == "reboot":
        ptr_VM.reboot();

    conn.close()


def kvm_vm_delete(guest_name):
    conn = libvirt.open(URL)
    ptr_VM = conn.lookupByName(guest_name)
    ptr_VM.destroy()
    ptr_POOL = conn.storagePoolLookupByName("default")
    ptr_POOL.storageVolLookupByName(guest_name + ".img").delete()
    conn.close()


def kvm_image_list():
    conn = libvirt.open(URL)
    ptr_POOL = conn.storagePoolLookupByName("default")
    list = ptr_POOL.listVolumes()
    conn.close()
    return list


def kvm_image_delete(name):
    conn = libvirt.open(URL)
    ptr_POOL = conn.storagePoolLookupByName("default")
    ptr_POOL.storageVolLookupByName(name).delete()
    conn.close()


def kvm_image_copy(name_volume, name_snap):
    conn = libvirt.open(URL)
    ptr_POOL = conn.storagePoolLookupByName("default")
    org_vol = ptr_POOL.storageVolLookupByName(name_volume + ".img")
    info = org_vol.info()
    save_vol = render_template(
        "volume.xml"
        , guest_name=name_snap
        , hdd=byteToGiga(info[1])
    )
    ptr_POOL.createXMLFrom(save_vol, org_vol, 0)
    conn.close()



# size convert BYTE TO GIGA
def byteToGiga(nbytes):
    return nbytes / (1024 * 1024 * 1024)


# size convert GIGA TO BYTE
def gigaToByte(gigabytes):
    return gigabytes * 1024 * 1024 * 1024

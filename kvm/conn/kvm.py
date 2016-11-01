# -*- coding: utf-8 -*-
__author__ = 'yhk'

import ConfigParser
import os
import libvirt
from util.config import config


URL = config.LIBVIRT_REMOTE_URL
vm_NAME = "test1"
conf_POOL = "<pool type='dir'>" \
            "<name>"+vm_NAME+"-POOL</name>" \
            "<target>" \
            "<path>/var/lib/libvirt/"+vm_NAME+"/</path>" \
            "</target>" \
            "</pool>"

conf_VOL = "<volume>" \
           "<name>"+vm_NAME+"-VOL.img</name>" \
           "<allocation>5</allocation>" \
           "<capacity unit='G'>1</capacity>" \
           "<target>" \
               "<path>/var/lib/libvirt/"+vm_NAME+"/"+vm_NAME+"-VOL.img</path>" \
               "<permission>" \
                   "<owner>0</owner>" \
                   "<group>501</group>" \
                   "<mode>0700</mode>" \
                   "<label>test-guest</label>" \
               "</permission>" \
           "</target>" \
           "</volume>"

conf_VM = "<domain type='kvm'>" \
              "<name>"+vm_NAME+"-VM</name>" \
              "<memory>524288</memory>" \
              "<currentMemory>524288</currentMemory>" \
              "<vcpu>1</vcpu>" \
              "<os>" \
                "<type arch='x86_64'>hvm</type>" \
                "<boot dev='hd'/>" \
              "</os>" \
              "<clock offset='utc'/>" \
              "<on_poweroff>destroy</on_poweroff>" \
              "<on_reboot>restart</on_reboot>" \
              "<on_crash>restart</on_crash>" \
              "<devices>" \
                "<disk type='file' device='disk'>" \
                    "<source file='/var/lib/libvirt/"+vm_NAME+"/"+vm_NAME+"-VOL.img'/>" \
                    "<target dev='hda' bus='ide'/>" \
                "</disk>" \
                "<interface type='network'>" \
                    "<mac address='00:16:3e:18:d5:a5'/>" \
                    "<source network='default'/>" \
                    "<model type='virtio'/>" \
                "</interface>" \
              "</devices>" \
          "</domain>"

#원격 libvirt 커넥션 테스트
def init_kvm_conn():
    conn = libvirt.openReadOnly(URL)
    print conn.getHostname()

def server_list():
    conn = libvirt.openReadOnly(URL)
    machine_list = []

    for id in conn.listDomainsID():
        dom = conn.lookupByID(id)
        machine_info = {}
        info = dom.info()
        if info[0] == 1:
           dom_state = "Running"
        elif info[0] == 2:
           dom_state = "Idle"
        elif info[0] == 3:
           dom_state = "Paused"
        elif info[0] == 4:
           dom_state = "Shutdown"
        elif info[0] == 5:
           dom_state = "Shutoff"
        elif info[0] == 6:
           dom_state = "Crashed"
        else:
           dom_state = "Nostate"

        machine_info['name'] = dom.name()
        machine_info['dom_state'] = dom_state
        machine_list.append(machine_info)
    return machine_list

def server_create():
    print vm_NAME
    conn = libvirt.open(URL)
    ptr_POOL = conn.storagePoolCreateXML(conf_POOL,0)
    ptr_POOL.createXML(conf_VOL, 0)
    conn.createXML(conf_VM, 0)

def server_delete():
    conn = libvirt.open(URL)
    vm_NAME = "test1-VM"
    pool_NAME =vm_NAME[:-3]+"-POOL"
    vol_NAME =vm_NAME[:-3]+"-VOL.img"
    ptr_VM = conn.lookupByName(vm_NAME)
    ptr_VM.destroy()

    ptr_POOL = conn.storagePoolLookupByName(pool_NAME)
    ptr_VOL = ptr_POOL.storageVolLookupByName(vol_NAME)

    ptr_VOL.delete(0)
    ptr_POOL.destroy()

# -*- coding: utf-8 -*-

__author__ = 'yhk'

import libvirt
from flask import  render_template
from pexpect import pxssh

from kvm.util.config import config

USER = "root"

def kvm_create(name, cpu, memory, disk, base_name, base_sub_type, host_ip):
    try:
        s = pxssh.pxssh()
        s.login(host_ip, USER)
        s.sendline(config.SCRIPT_PATH + "sshkey_copy.sh ")
        s.logout()

        url = config.LIBVIRT_REMOTE_URL.replace("ip", host_ip, 1)
        conn = libvirt.open(url)

        # 스냅샷 기반 유무에 따른 생성 set_vm_ip.sh로직 분기
        if base_sub_type == "base":
            # guest 생성 정보 xml 템플릿 생성
            vol = render_template(
                "volume.xml"
                , guest_name=name
                , disk=disk
            )

            ptr_POOL = conn.storagePoolLookupByName(config.POOL_NAME)
            defaultVol = ptr_POOL.storageVolLookupByName(base_name)
            ptr_POOL.createXMLFrom(vol, defaultVol, 0)
            ptr_POOL.storageVolLookupByName(name + ".img").resize(gigaToByte(int(disk)))
        else:
            kvm_image_copy(base_name.split(".")[0], name, host_ip)

        # vm 생성
        guest = render_template(
            "guest.xml"
            , guest_name=name
            , current_memory=memory
            , vcpu=cpu
        )
        conn.createXML(guest, 0)
        uuid = conn.lookupByName(name).UUIDString()
        conn.close()
        return uuid
    except IOError as errmsg:
        print(str(errmsg))


def kvm_change_status(vm_name, status, host_ip):
    url = config.LIBVIRT_REMOTE_URL.replace("ip", host_ip, 1)
    conn = libvirt.open(url)
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


def kvm_vm_delete(guest_name, host_ip):
    url = config.LIBVIRT_REMOTE_URL.replace("ip", host_ip, 1)
    conn = libvirt.open(url)
    ptr_VM = conn.lookupByName(guest_name)
    ptr_VM.destroy()
    ptr_POOL = conn.storagePoolLookupByName(config.POOL_NAME)
    ptr_POOL.storageVolLookupByName(guest_name + ".img").delete()
    conn.close()


def kvm_image_list():
    conn = libvirt.open(config.LIBVIRT_REMOTE_URL)
    ptr_POOL = conn.storagePoolLookupByName(config.POOL_NAME)
    list = ptr_POOL.listVolumes()
    conn.close()
    return list


def kvm_image_delete(name):
    conn = libvirt.open(config.LIBVIRT_REMOTE_URL)
    ptr_POOL = conn.storagePoolLookupByName(config.POOL_NAME)
    ptr_POOL.storageVolLookupByName(name).delete()
    conn.close()


def kvm_image_copy(name_volume, name_snap, host_ip):
    conn = libvirt.open(config.LIBVIRT_REMOTE_URL.replace("ip", host_ip, 1))
    ptr_POOL = conn.storagePoolLookupByName(config.POOL_NAME)
    org_vol = ptr_POOL.storageVolLookupByName(name_volume + ".img")
    info = org_vol.info()
    save_vol = render_template(
        "volume.xml"
        , guest_name=name_snap
        , disk=byteToGiga(info[1])
    )
    ptr_POOL.createXMLFrom(save_vol, org_vol, 0)
    conn.close()


# size convert BYTE TO GIGA
def byteToGiga(nbytes):
    return nbytes / (1024 * 1024 * 1024)


# size convert GIGA TO BYTE
def gigaToByte(gigabytes):
    return gigabytes * 1024 * 1024 * 1024

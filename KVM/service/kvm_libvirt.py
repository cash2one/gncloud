# -*- coding: utf-8 -*-

__author__ = 'yhk'

import libvirt
from flask import  render_template
from pexpect import pxssh

from KVM.util.config import config

USER = "root"

def kvm_create(name, cpu, memory, disk, base_name, base_sub_type, host_ip):
    s = pxssh.pxssh(timeout=1200)
    s.login(host_ip, USER)
    s.sendline(config.SCRIPT_PATH + "sshkey_copy.sh ")
    url = config.LIBVIRT_REMOTE_URL.replace("ip", host_ip, 1)
    conn = libvirt.open(url)

    # 스냅샷 기반 유무에 따른 생성 set_vm_ip.sh로직 분기
    instance_POOL = conn.storagePoolLookupByName(config.POOL_NAME)

    if base_sub_type == "base":
        s.sendline("\cp "+config.LIVERT_IMAGE_BASE_PATH+base_name +" "+config.LIVERT_IMAGE_LOCAL_PATH+base_name)
        s.logout()
        instance_POOL.refresh()
        vol = render_template(
            "volume.xml"
            , guest_name=name
            , disk=disk
        )
        defaultVol = instance_POOL.storageVolLookupByName(base_name)
        instance_POOL.createXMLFrom(vol, defaultVol, 0)
        instance_POOL.storageVolLookupByName(name + ".img").resize(disk)
        defaultVol.delete()
    else:
        s.sendline("\cp "+config.LIVERT_IMAGE_SNAPSHOT_PATH+base_name +" "+config.LIVERT_IMAGE_LOCAL_PATH+name + ".img")
        s.logout()
        instance_POOL.refresh()
        instance_POOL.storageVolLookupByName(name + ".img").resize(disk)

    # vm 생성
    guest = render_template(
        "guest.xml"
        , guest_name=name
        , guest_path=config.LIVERT_IMAGE_LOCAL_PATH+name+".img"
        , config_path = config.SCRIPT_PATH+"initcloud/config.iso"
        , current_memory=memory
        , vcpu=cpu
    )
    dom = conn.defineXML(guest)
    dom.create()
    guest = conn.lookupByName(name)
    guest.setAutostart(True)
    conn.close()
    return guest.UUIDString()

def kvm_change_status(vm_name, status, host_ip):
    url = config.LIBVIRT_REMOTE_URL.replace("ip", host_ip, 1)
    conn = libvirt.open(url)
    ptr_VM = conn.lookupByName(vm_name)
    if status == 'Resume':
        ptr_VM.resume()
    elif status == "Suspend":
        ptr_VM.suspend()
    elif status == "Reboot":
        ptr_VM.reboot();

    conn.close()


def kvm_vm_delete(guest_name, host_ip):
    url = config.LIBVIRT_REMOTE_URL.replace("ip", host_ip, 1)
    conn = libvirt.open(url)
    ptr_VM = conn.lookupByName(guest_name)
    ptr_VM.destroy()
    ptr_VM.undefine()
    ptr_POOL = conn.storagePoolLookupByName(config.POOL_NAME)
    ptr_POOL.storageVolLookupByName(guest_name + ".img").delete()
    conn.close()


def kvm_image_list():
    conn = libvirt.open(config.LIBVIRT_REMOTE_URL)
    ptr_POOL = conn.storagePoolLookupByName(config.POOL_NAME)
    list = ptr_POOL.listVolumes()
    conn.close()
    return list


def kvm_image_delete(name,host_ip):
    conn = libvirt.open(config.LIBVIRT_REMOTE_URL.replace("ip", host_ip, 1))
    ptr_POOL = conn.storagePoolLookupByName(config.POOL_NAME)
    ptr_POOL.storageVolLookupByName(name).delete()
    conn.close()


def kvm_image_copy(name_volume, name_snap, host_ip):
    conn = libvirt.open(config.LIBVIRT_REMOTE_URL.replace("ip", host_ip, 1))
    ptr_POOL = conn.storagePoolLookupByName(config.POOL_NAME)

    #디스크 유무 체크
    stgvols = ptr_POOL.listVolumes()
    if all(e != name_volume + ".img" for e in stgvols):
        ptr_POOL.refresh()

    org_vol = ptr_POOL.storageVolLookupByName(name_volume + ".img")

    info = org_vol.info()
    save_vol = render_template(
        "volume.xml"
        , guest_name=name_snap
        , disk=info[1]
    )
    ptr_POOL.createXMLFrom(save_vol, org_vol, 0)


# size convert BYTE TO GIGA
def byteToGiga(nbytes):
    return nbytes / (1024 * 1024 * 1024)


# size convert GIGA TO BYTE
def gigaToByte(gigabytes):
    return gigabytes * 1024 * 1024 * 1024

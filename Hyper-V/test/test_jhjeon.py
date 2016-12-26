# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from service.powershellService import PowerShell
from util.config import config
from sqlalchemy.sql import func
import datetime


def test_service_new_vm():
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    return ps.new_vm(Name="testvm222", MemoryStartupBytes="2048MB", Path="C:\images", SwitchName="out")


def test_service_set_vm(vm):
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    return ps.set_vm(VMId=vm['VMId'], ProcessorCount="2")


def test_service_convert_vhd():
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    CONVERT_VHD_DESTINATIONPATH = "C:\\images\\testvm_disk2\\disk.vhdx"
    CONVERT_VHD_PATH = "C:\\images\\windows10.vhdx"
    return ps.convert_vhd(DestinationPath=CONVERT_VHD_DESTINATIONPATH, Path=CONVERT_VHD_PATH)


def test_add_vmharddiskdrive():
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    CONVERT_VHD_DESTINATIONPATH = "C:\\images\\testvm_disk2\\disk.vhdx"
    VMId = "208AAC01-EBAF-4060-B7F1-59F1B7FB68A4"
    return ps.add_vmharddiskdrive(VMId=VMId, Path=CONVERT_VHD_DESTINATIONPATH)

# vm = test_service_new_vm()
# print vm
# print test_service_set_vm(vm)
# return print test_service_convert_vhd()
# print test_add_vmharddiskdrive()

now = datetime.datetime.now()
print now

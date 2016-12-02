# -*- coding: utf-8 -*-
"""
Hyper-V를 컨트롤 할 PowerShell Script(서비스의 powershellSerivce에서 제공)를 실행하는 Rest 함수들을 정의한다.
각 Rest 함수들의 이름은 hvm_(Action을 대표하는 영단어 소문자)로 표기한다.
"""
__author__ = 'jhjeon'

import datetime
from flask import request, jsonify
from service.powershellService import PowerShell
from db.database import db_session
from db.models import GnVmMachines
from util.config import config


# PowerShell Script Manual 실행: (Script) | ConvertTo-Json
def manual():
    script = request.args.get('script')
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    # return ps.send(script)
    return jsonify(result=ps.send(script))


# VM 생성 및 실행
def hvm_create():
    # cpu core 수
    cpu = request.args.get('cpu')
    # 디스크 설정
    hdd = request.args.get('hdd')
    # 가상머신 메모리
    memory = request.args.get('memory')
    # 베이스 이미지 경로
    baseImage = request.args.get('baseImage')

    os = request.args.get('os')
    os_ver = request.args.get('os_ver')
    os_subver = request.args.get('os_subver')
    os_bit = request.args.get('os_bit')
    author_id = request.args.get('author_id')

    # VM Name (Hyper-V에서는 VMName의 중복이 가능, VM별 구분은 VMId로 구분 필요)
    name = request.args.get('name')

    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)

    # 새 머신을 만든다. (New-VM)
    # todo hvm_create test value 1. Path 및 SwitchName은 추후 DB에서 불러올 값들이다.
    SWITCHNAME = "out"
    new_vm = ps.new_vm(Name=name, MemoryStartupBytes=memory, Path="C:\images", SwitchName=SWITCHNAME)
    # 머신이 생성되었는지 확인한다. (New-VM 리턴값 체크)
    if new_vm is not None:
        # 새 머신에서 추가적인 설정을 한다 (Set-VM)
        set_vm = ps.set_vm(VMId=new_vm['VMId'], ProcessCount=cpu)
        # 정해진 OS Type에 맞는 디스크(VHD 또는 VHDX)를 가져온다. (Convert-VHD)
        # todo. CONVERT_VHD_PATH 및 SwitchName은 추후 DB에서 불러올 값들이다.
        CONVERT_VHD_DESTINATIONPATH = "C:\\images\\testvm_disk2\\disk.vhdx"
        CONVERT_VHD_PATH = "C:\\images\\windows10.vhdx"
        convert_vhd = ps.convert_vhd(DestinationPath=CONVERT_VHD_DESTINATIONPATH, Path=CONVERT_VHD_PATH)
        # 가져온 디스크를 가상머신에 연결한다. (Add-VMHardDiskDrive)
        add_vmharddiskdrive = ps.add_vmharddiskdrive(VMId=new_vm['VMId'], Path=CONVERT_VHD_DESTINATIONPATH)
        # todo hvm_create 6. VM에 IP를 설정한다. (???)
        # VM을 시작한다.
        start_vm = ps.start_vm(new_vm['VMId'])
        # todo hvm_create 7. 새로 생성된 가상머신 데이터를 DB에 저장한다.
        vm = GnVmMachines(start_vm['VMId'], name, '', 'hyperv', start_vm['VMId'], 1, '192.168.0.144', cpu,
                          memory, CONVERT_VHD_DESTINATIONPATH, os, os_ver, os_subver, os_bit, None, author_id, datetime.datetime.utcnow,
                          datetime.datetime.utcnow, None, start_vm['state'])
        db_session.add(vm)
        db_session.commit()
        return jsonify(status=True, massage="VM 생성 성공")
    else:
        return jsonify(status=False, massage="VM 생성 실패")


# todo REST. VM 스냅샷 생성
def hvm_snap(id):
    name = request.args.get("name")
    type = request.args.get("type")
    author_id = request.args.get("author_id")
    return jsonify(status=False, message="미구현")


# todo REST. VM 상태변경
# -------------------------------------------------------
# VM 상태 "start", "stop", "resume", "shutdown", "restart", "powerdown"
# -------------------------------------------------------
# VM State Value and Meaning (Windows WMI Manual에서 가져옴, 상태 변경 작업 시 참고할 것)
# Other 1 - Corresponds to CIM_EnabledLogicalElement.EnabledState = Other.
# Running 2 - Corresponds to CIM_EnabledLogicalElement.EnabledState = Enabled.
# Off 3 - Corresponds to CIM_EnabledLogicalElement.EnabledState = Disabled.
#
# Stopping 4 -
# Valid in version 1 (V1) of Hyper-V only. The virtual machine is shutting down via the shutdown service.
# Corresponds to CIM_EnabledLogicalElement.EnabledState = ShuttingDown.
#
# Saved 6 - Corresponds to CIM_EnabledLogicalElement.EnabledState = Enabled but offline.
# Paused 9 - Corresponds to CIM_EnabledLogicalElement.EnabledState = Quiesce, Enabled but paused.
# Starting 10 - State transition from Off or Saved to Running.
# Reset 11 - Reset the virtual machine. Corresponds to CIM_EnabledLogicalElement.EnabledState = Reset.
# Saving 32773 - In version 1 (V1) of Hyper-V, corresponds to EnabledStateSaving.
# Pausing 32776 - In version 1 (V1) of Hyper-V, corresponds to EnabledStatePausing.
#
# Resuming 32777 -
# In version 1 (V1) of Hyper-V, corresponds to EnabledStateResuming. State transition from Paused to Running.
#
# FastSaved 32779 - Corresponds to EnabledStateFastSuspend.
# FastSaving 32780 - Corresponds to EnabledStateFastSuspending. State transition from Running to FastSaved.
# -------------------------------------------------------
def hvm_state(id):

    type = request.args.get('type')
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)

    if type == "start":
        # VM 시작
        # 1. 가상머신을 시작한다. (Start-VM)
        start = ps.start_vm(id)
        print id
        # 2. 가상머신 상태를 체크한다. (Get-VM)
        if start['State'] is 2:
            return jsonify(status=True, message="가상머신이 정상적으로 실행되었습니다.")
        elif start['State'] is not 2:
            return jsonify(status=False, message="가상머신이 실행되지 않았습니다.")
        else:
            return jsonify(status=False, message="정상적인 결과가 아닙니다.")
    elif type == "stop":
        #stop 1. 가상머신을 정지한다. (Stop-VM)
        stop = ps.stop_vm(id)
        # stop 2. 가상머신 상태를 체크한다. (Get-VM)
        if stop['State'] is 3:
            return jsonify(status=True, message="가상머신이 종료되었습니다.")
        else:
            return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
        # todo stop 3. 변경된 가상머신 상태를 DB에 업데이트한다.
        return jsonify(status=False, message="상태 미완성")
    elif type == "restart":
        restart = ps.restart_vm(id)
        # resume 1. 가상머신을 재시작한다. (Restart-VM)
        if restart['State'] is 2:
            return jsonify(status=True, message="가상머신이 정상적으로 재시작되었습니다.")
        else:
            return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
        # resume 2. 가상머신 상태를 체크한다. 다만 (Get-VM)
    elif type == "shutdown":
        # todo shutdown 1.
        return jsonify(status=False, message="미구현")
    elif type == "suspend":
        suspend = ps.suspend_vm(id)
        if suspend['State'] is 9:
            return  jsonify(status=True, message="가상머신이 일시정지되었습니다.")
        else:
            return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
    elif type == "resume":
        resume = ps.resume_vm(id)
        if resume['State'] is 2:
            return jsonify(status=True, message="가상머신이 재시작되었습니다.")
        else:
            return jsonify(status=True, message="정상적인 결과값이 아닙니다.")
        return jsonify(status=False, message="")
    elif type == "powerdown":
        return jsonify(status=False, message="상태 미완성")
    else:
        return jsonify(status=False, message="정상적인 상태 정보를 받지 못했습니다.")


# todo REST. VM 정보
def hvm_vm(vmid):
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    # Powershell Script를 통해 VM 정보를 가져온다.
    vm = ps.get_vm(vmid)
    # todo get-vm. VM 정보를 DB에서 가져온다.
    return jsonify(vm=vm, message="", status=True)


# todo REST. VM 리스트 정보
def hvm_vm_list():
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    vm_list = ps.get_vm()
    # todo get-vm. VM 정보를 DB에서 가져온다.
    return jsonify(list=vm_list, message="", status=True)

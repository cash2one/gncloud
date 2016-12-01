# -*- coding: utf-8 -*-
"""
Hyper-V를 컨트롤 할 PowerShell Script(서비스의 powershellSerivce에서 제공)를 실행하는 Rest 함수들을 정의한다.
각 Rest 함수들의 이름은 hvm_(Action을 대표하는 영단어 소문자)로 표기한다.
"""
__author__ = 'jhjeon'

from flask import request, jsonify
from service.powershellService import PowerShell
from util.config import config


# 수동으로 Script를 보내 실행하도록 한다.
# Convertto-Json는 자동으로 적용되므로 따로 적지 않도록 한다.
def manual():
    script = request.args.get('script')
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    # return ps.send(script)
    return jsonify(result=ps.send(script))


# VM을 생성한다.
# Request
# Response
def hvm_create():
    # VM Name (Hyper-V에서는 VMName의 중복이 가능, VM별 구분은 VMId로 구분 필요)
    name = request.args.get('name')
    # CPU Core 수
    cpu = request.args.get('cpu')
    # 디스크 경로
    hdd = request.args.get('hdd')
    # 가상머신 메모리
    memory = request.args.get('memory')
    # 베이스 이미지 경로
    baseImage = request.args.get('baseImage')
    # todo parameter 1. OSType 파라미터가 필요해 보임
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    # 새 머신을 만든다. (New-VM)
    # todo hvm_create test value 1. Path 및 SwitchName은 추후 DB에서 불러올 값들이다.
    PATH = "c:\images"
    SWITCHNAME = "out"
    new_vm = ps.new_vm(Name=name, MemoryStartupBytes=memory, Path=PATH, SwitchName=SWITCHNAME)
    # 머신이 생성되었는지 확인한다. (New-VM 리턴값 체크)
    if new_vm is not None:
        # 새 머신에서 추가적인 설정을 한다 (Set-VM)
        set_vm = ps.set_vm(VMId=new_vm['VMId'], ProcessCount=cpu)
        # 정해진 OS Type에 맞는 디스크(VHD 또는 VHDX)를 가져온다. (Convert-VHD)
        # CONVERT_VHD_PATH 및 SwitchName은 추후 DB에서 불러올 값들이다.
        CONVERT_VHD_DESTINATIONPATH = "C:\\images\\testvm_disk2\\disk.vhdx"
        CONVERT_VHD_PATH = "C:\\images\\windows10.vhdx"
        convert_vhd = ps.convert_vhd(DestinationPath=CONVERT_VHD_DESTINATIONPATH, Path=CONVERT_VHD_PATH)
        # todo hvm_create 5. 가져온 디스크를 가상머신에 연결한다. (Add-VMHardDiskDrive / 리턴값 없음)
        # todo hvm_create 6. VM에 IP를 설정한다. (???)
        # todo hvm_create 8. 새로 생성된 가상머신 데이터를 DB에 저장한다.
        return jsonify(status=True, massage="VM 생성 성공")
    else:
        return jsonify(status=False, massage="VM 생성 실패")


# VM 리스트 정보를 가져온다.
# Request
# Response
# {
#   list: JSONArray
#       {
#           cpu: int,
#           hdd: int,
#           id: int,
#           ip: String,
#           memory: int?
#           name: String,
#           status: ?
#           type: String (hyperv)
#       },
#   message: String,
#   status: boolean
# }
def hvm_vm_list():
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    vm_list = ps.get_vm()
    return jsonify(list=vm_list, message="", status=True)


# VM 하나의 정보를 가져온다.
def hvm_vm(vm_name):
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    vm = ps.get_vm(vm_name)
    return jsonify(vm=vm, message="", status=True)


# VM 상태를 변경한다.
# -------------------------------------------------------
# 스냅샷 상태 snap / 시작 start / 정지 stop / 재시작 resume / 삭제 delete
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
def hvm_state(vm_name, status):

    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)

    if status == "start":
        # VM 시작
        # 1. 가상머신을 시작한다. (Start-VM)
        start = ps.start_vm(vm_name)
        # 2. 가상머신 상태를 체크한다. (Get-VM)
        result = ps.get_vm(vm_name)
        if result['State'] is 2:
            return jsonify(status=True, message="가상머신이 정상적으로 실행되었습니다.")
        elif result['State'] is not 2:
            return jsonify(status=False, message="가상머신이 실행되지 않았습니다.")
        else:
            return jsonify(status=False, message="정상적인 결과가 아닙니다.")
    elif status == "stop":
        # todo stop 1. 가상머신을 정지한다. (Stop-VM)
        # todo stop 2. 가상머신 상태를 체크한다. (Get-VM)
        # todo stop 3. 변경된 가상머신 상태를 DB에 업데이트한다.
        return jsonify(status=False, message="상태 미완성")
    elif status == "resume":
        # todo resume 1. 가상머신을 재시작한다. (Restart-VM)
        # todo resume 2. 가상머신 상태를 체크한다. 다만 (Get-VM)
        return jsonify(status=False, message="상태 미완성")
    elif status == "delete":
        # todo delete 1. 가상머신을 정지한다. (Stop-VM)
        # todo delete 2. 가상머신을 삭제한다. (Remove-VM)
        # todo delete 3. 가상머신을 리스트를 가져와서 가상머신이 삭제되었는지 확인한다. (Get-VM List)
        # todo delete 4. 변경된 가상머신 상태를 DB에 업데이트한다.
        # (현재는 구현하지 않는다.) todo delete 5. 삭제된 데이터를
        return jsonify(status=False, message="상태 미완성")
    elif status == "snap":
        # todo snap 1. 가상머신 현재 상태를 스냅샷으로 저장한다. (???)
        # todo snap 2. 생성된 스냅샷 내용을 DB에 저장한다
        return jsonify(status=False, message="상태 미완성")
    else:
        return jsonify(status=False, message="정상적인 상태 정보를 받지 못했습니다.")

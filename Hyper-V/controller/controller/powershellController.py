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
def hvm_create():
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    # todo hvm_create 1. 새 머신을 만든다. (New-VM)
    # todo hvm_create 1. 머신이 생성되었는지 확인한다. (New-VM 리턴값 체크)
    # todo hvm_create 2. 새 머신에서 추가적인 설정을 한다 (Set-VM / 리턴값 없음)
    # todo hvm_create 3. 정해진 OS Type에 맞는 디스크(VHD 또는 VHDX)를 가져온다. (Convert-VHD / 리턴값 없음)
    # todo hvm_create 4. 가져온 디스크를 가상머신에 연결한다. (Add-VMHardDiskDrive / 리턴값 없음)
    # todo hvm_create 5. VM에 IP를 설정한다. (???)
    # todo hvm_create 6. 요청된 작업이 제대로 실행되었는지 체크한다 (Get-VM)
    return ""


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
        # 가상머신을 시작한다. (Start-VM)
        start = ps.start_vm(vm_name)
        # 가상머신 상태를 체크한다. (Get-VM)
        result = ps.get_vm(vm_name)
        if result['State'] is 2:
            return jsonify(status=True, message="가상머신이 정상적으로 실행되었습니다.")
        elif result['State'] is not 2:
            return jsonify(status=False, message="가상머신이 실행되지 않았습니다.")
        else:
            return jsonify(status=False, message="정상적인 결과가 아닙니다.")
    elif status == "stop":
        # 가상머신을 정지한다. (Stop-VM)
        return jsonify(status=False, message="상태 미완성")
    elif status == "resume":
        # 가상머신을 재시작한다. (Stop-VM)
        return jsonify(status=False, message="상태 미완성")
    elif status == "delete":
        return jsonify(status=False, message="상태 미완성")
    elif status == "snap":
        return jsonify(status=False, message="상태 미완성")
    else:
        return jsonify(status=False, message="정상적인 상태 정보를 받지 못했습니다.")

# -*- coding: utf-8 -*-
"""
PowerShell 스크립트를 전달할 함수들을 가지고 있는 PowerShell 클래스를 정의한다.
하나의 파워쉘 스크립트당 하나의 함수로 구현한다.
모든 함수명은 소문자로, -는 _로 표현한다
다른 결과가 나오지만 같은 명령어를 사용하여 함수명이 겹칠 경우, 함수명 뒤에 _(역할)로 추가적으로 함수명을 구분해준다.
"""
__author__ = 'jhjeon'

import json
import requests


class PowerShell(object):
    # 스크립트 실행 결과를 JSON 형식으로 받도록 하기 위한 커맨드
    CONVERTTO_JSON = " | ConvertTo-Json -Compress"
    # Script Default 설정이 리턴값을 주지 않는 경우 해당 옵션이 추가되어야 리턴값이 나온다.
    PASSTHRU = " -Passthru"
    VERBOSE = " -Verbose"
    GENERATION_TYPE_1 = 1
    GENERATION_TYPE_2 = 2

    def __init__(self, address, port, uri):
        self.address = address
        self.port = port
        self.uri = uri

    # 가상머신을 생성한다.
    # example) New-VM -Name testvm -Generation 2 -MemoryStartupBytes 2048MB
    # / -Path C:\images -SwitchName out | Convertto-Json
    # Return VMObject
    def new_vm(self, **kwargs):
        script = "New-VM"
        for option, value in kwargs.items():
            if option == "Path":
                script += " -" + option + " '" + value + "'"
            elif option == "MemoryStartupBytes":
                script += " -" + option + " " + value + "MB"
            else:
                script += " -" + option + " " + value
        script += " -Generation " + str(self.GENERATION_TYPE_2)
        script += self.CONVERTTO_JSON
        return self.send(script)

    # 가상머신 설정
    # example) $vm = Get-VM -Id E6CE3D4E-1152-494B-9445-CBD38549CFF4; Set-VM -VM $vm -ProcessorCount 2
    # Return VMObject
    def set_vm(self, **kwargs):
        vmscript = ""
        script = "Set-VM $vm"
        for option, value in kwargs.items():
            # vmId 값의 경우 VMObject를 불러오기 위해서 필요한 값이므로 Set-VM Script에서는 직접 넣지 않는다.
            if option == "VMId":
                vmscript = "$vm = Get-VM -Id " + value + "; "
            else:
                script += " -" + option + " " + value
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        return self.send(vmscript + script)

    # VHD 파일을 복사
    # example) Convert-VHD -DestinationPath C:\images\2_testvm\disk.vhdx
    # / -Path C:\images\windows10.vhdx -Verbose -Passthru | ConvertTo-Json
    # Return VHDObject
    def convert_vhd(self, **kwargs):
        script = "Convert-VHD"
        for option, value in kwargs.items():
            if option == "Path" or option == "DestinationPath":
                script += " -" + option + " '" + value + "'"
            elif option == "BlockSizeBytes":
                script += " -" + option + " " + value + "GB"
            else:
                script += " -" + option + " '" + value + "'"
        script += self.VERBOSE
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        return self.send(script)

    # VM 하드디스크 추가
    # example) $vm = Get-VM -Id E6CE3D4E-1152-494B-9445-CBD38549CFF4;
    # / Add-VMHardDiskDrive -VM $vm -Path C:\images\2_testvm\disk.vhdx
    # Return ?
    def add_vmharddiskdrive(self, **kwargs):
        script = "Add-VMHardDiskDrive $vm"
        for option, value in kwargs.items():
            # vmId 값의 경우 VMObject를 불러오기 위해서 필요한 값이므로 Set-VM Script에서는 직접 넣지 않는다.
            if option == "VMId":
                vmscript = "$vm = Get-VM -Id " + value + "; "
            elif option == "Path":
                script += " -" + option + " '" + value + "'"
            else:
                script += " -" + option + " " + value
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        return self.send(vmscript + script)

    # 가상머신을 시작한다.
    # example) $vm = Get-VM -Id 8102C1F1-6A15-4BDC-8BF1-C8ECBE9D94E2; Start-VM -VM $vm | Convertto-Json
    def start_vm(self, vm_Id):
        script = "$vm = Get-VM -Id " + vm_Id + "; "
        script += "Start-VM -VM $vm"
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        return self.send(script)

    # 가상머신을 종료한다. -force, -turnoff
    def stop_vm(self, vm_Id):
        script = "$vm = Get-VM -Id " + vm_Id + "; "
        script += "Stop-VM -Force $vm "
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        return self.send(script)


    #가상머신을 재부팅 한다
    def restart_vm(self, vm_Id):
        script = "$vm = Get-VM -Id " + vm_Id + "; "
        script += "Restart-VM -Force $vm "
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        return self.send(script)


    #가상머신을 일시정지상태로 돌린다. 리턴 state = 9
    def suspend_vm(self, vm_Id):
        script = "$vm = Get-VM -Id " + vm_Id + "; "
        script += "Suspend-VM -VM $vm "
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        return self.send(script)


   #일시정지된 가상머신을 다시 시작한다. 리턴 state = 2
    def resume_vm(self, vm_Id):
        script = "$vm = Get-VM -Id " + vm_Id + "; "
        script += "Resume-VM -VM $vm "
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        return self.send(script)


    # 가상머신 하나의 정보를 가져온다.
    # example) $vm = Get-VM -Id 8102C1F1-6A15-4BDC-8BF1-C8ECBE9D94E2 | Convertto-Json
    def get_vm(self, vm_name):
        script = "Get-VM -Id " + vm_name
        script += self.CONVERTTO_JSON
        return self.send(script)

    # 서버 내의 모든 가상머신 리스트 정보를 가져온다.
    # example) Get-VM
    def get_vm(self):
        script = "Get-VM"
        script += self.CONVERTTO_JSON
        return self.send(script)

    # 스냅샷 생성
    def create_snap(self, vm_Id):
        script = "Invoke-Command -ComputerName GNCLOUDWIN -ScriptBlock {"
        script += "$vm = Get-VM -Id "
        script += vm_Id + ";"
        script += " powershell.exe -file C:\images\make_snap.ps1 "
        script += '$vm.Name '
        script += vm_Id+"_clone"
        script += ' -passthru ; Get-ChildItem C:\images\Vhdx\*.vhdx | ConvertTo-Json -Compress }'
        print script
        return self.send(script)

    # agent 모듈에 파워쉘 스크립트를 전달하여 실행하고 결과를 받아온다.
    def send(self, script):
        address = self.address
        port = str(self.port)
        uri = self.uri
        url = "http://" + address
        url += ":"
        url += port
        url += "/"
        url += uri
        # todo send. 나중에 이 부분은 agent에서 데이터 값을 받아 처리하도록 수정이 끝나면 지울 것
        url += "?script=" + script
        # todo send. 추후 스크립트를 URL에 포함시켜 보내지 않고 Post data로 전달받을 수 있도록 agent 수정 필요
        data = {'script': script}
        response = requests.post(url, data=json.dumps(data), timeout=1000 * 60 * 20)
        return json.loads(response.json())

    def get_state_string(self, state):
        if state is 1:
            return "Other"
        elif state is 2:
            return "Running"
        elif state is 3:
            return "Off"
        elif state is 4:
            # 현재 버전에서는 사용하지 않는 상태..
            return "Stopping"
        elif state is 6:
            return "Starting"
        elif state is 9:
            return "Paused"
        elif state is 10:
            return "Starting"
        elif state is 11:
            return "Reset"
        elif state is 32773:
            return "Saving"
        elif state is 32776:
            return "Pausing"
        elif state is 32777:
            return "Resuming"
        elif state is 32779:
            return "FastSaved"
        elif state is 32780:
            return "FastSaving"
        else:
            return "Other"

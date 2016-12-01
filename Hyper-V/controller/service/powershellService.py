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
from db.models import GnVmMachines


class PowerShell(object):

    # 스크립트 실행 결과를 JSON 형식으로 받도록 하기 위한 커맨드
    CONVERTTO_JSON = " | Convertto-Json"
    GENERATION_TYPE_1 = 1
    GENERATION_TYPE_2 = 2

    def __init__(self, address, port, uri):
        self.address = address
        self.port = port
        self.uri = uri

    # New-VM -Name (vm_name) -Generation GENERATION_TYPE -MemoryStartupBytes (memory)
    # new_vm(MemoryStartupBytes='1024MB')
    # 가상머신을 생성한다.
    def new_vm(self, **kwargs):
        script = "New-VM"
        for option, value in kwargs.items():
            script += " -" + option + " " + value
        script += " -Generation " + self.GENERATION_TYPE_2
        script += self.CONVERTTO_JSON
        return self.send(script)

    # todo make Set-VM
    # 가상머신 설정
    def set_vm(self):
        script = "Set-VM"
        script += ""
        script += self.CONVERTTO_JSON
        return self.send(script)

    # todo make Convert-VHD
    # VHD 파일을 복사
    def convert_vhd(self):
        script = "Convert-VHD"
        script += self.CONVERTTO_JSON
        return self.send(script)

    # todo make Add-VMHardDiskDrive
    # 가상머신 설정
    def add_vmharddiskdrive(self):
        script = "Add-VMHardDiskDrive"
        script += self.CONVERTTO_JSON
        return self.send(script)

    # Start-VM -VMName (가상머신 이름)
    # example) $vm = Get-VM -Id 8102C1F1-6A15-4BDC-8BF1-C8ECBE9D94E2; Start-VM -VM $vm | Convertto-Json
    # 가상머신을 시작한다.
    def start_vm(self, vm_name):

        script = "$vm = Get-VM -Id " + vm_name + "; "
        script += "Start-VM -VM $vm"
        script += self.CONVERTTO_JSON
        return self.send(script)

    # Get-VM -Id (가상머신 Hyper-V VMID)
    # example) $vm = Get-VM -Id 8102C1F1-6A15-4BDC-8BF1-C8ECBE9D94E2 | Convertto-Json
    # get_vm(Id='444-44asdf-1234-....')
    # 가상머신 하나의 정보를 가져온다.
    def get_vm(self, vm_name):
        script = "Get-VM -Id " + vm_name
        script += self.CONVERTTO_JSON
        return self.send(script)

    # Get-VM
    # 서버 내의 모든 가상머신 리스트 정보를 가져온다.
    def get_vm(self):
        script = "Get-VM"
        script += self.CONVERTTO_JSON
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
        response = requests.post(url, data=json.dumps(data))
        return json.loads(response.json())

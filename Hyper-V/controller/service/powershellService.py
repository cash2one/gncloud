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

    def __init__(self, address, port, uri):
        self.address = address
        self.port = port
        self.uri = uri

    # New-VM
    def new_vm(self):
        return ""

    # Start-VM -VMName (가상머신 이름)
    def start_vm(self, vm_name):
        script = "Start-VM -VMName " + vm_name + self.CONVERTTO_JSON
        return self.send(script)

    # Get-VM -VMName (가상머신 이름)
    def get_vm(self, vm_name):
        script = "Get-VM -VMName " + vm_name + self.CONVERTTO_JSON
        return self.send(script)

    # Get-VM
    def get_vm(self):
        script = "Get-VM" + self.CONVERTTO_JSON
        return self.send(script)


    # agent 모듈에 파워쉘 스크립트를 전달하여 실행하고 결과를 받아온다.
    def send(self, script):
        address = self.address
        port = str(self.port)
        uri = self.uri
        #URL = "http://60.196.149.135:8180/powershell/execute?script=Get-VM%20%7C%20Convertto-Json"
        url = "http://" + address
        url += ":"
        url += port
        url += "/"
        url += uri
        # todo. 나중에 이 부분은 agent에서 데이터 값을 받아 처리하도록 수정이 끝나면 지울 것
        url += "?script=" + script

        # todo. 추후 스크립트를 URL에 포함시켜 보내지 않고 Post data로 전달받을 수 있도록 agent 수정 필요
        data = {'script': script}
        response = requests.post(url, data=json.dumps(data))
        return json.loads(response.json())

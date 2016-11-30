# -*- coding: utf-8 -*-
__author__ = 'gncloud'

import json
import requests


class PowerShell():

    CONVERTTO_JSON = " | Convertto-Json"

    def __init__(self, address, port, uri):
        self.address = address
        self.port = port
        self.uri = uri

    def start_vm(self, vm_name):
        script = "Start-VM -VMName " + vm_name + self.CONVERTTO_JSON
        start_command = self.send(script)
        script = "Get-VM -VMName " + vm_name + self.CONVERTTO_JSON
        get_vm_command = self.send(script)

        return get_vm_command


    # agent 모듈에 파워쉘 스크립트를 전달하여 실행하고 결과를 받아온다.
    def send(self, script):
        address = self.address
        port = str(self.port)
        uri = self.uri
        #URL = "http://60.196.149.135:8180/powershell/execute?script=Get-VM%20%7C%20Convertto-Json"
        URL = "http://" + address
        URL += ":"
        URL += port
        URL += "/"
        URL += uri
        # todo. 나중에 이 부분은 agent에서 데이터 값을 받아 처리하도록 수정이 끝나면 지울 것
        URL += "?script=" + script

        # todo. 추후 스크립트를 URL에 포함시켜 보내지 않고 Post data로 전달받을 수 있도록 agent 수정 필요
        data = {'script': script}
        response = requests.post(URL, data=json.dumps(data))
        return json.loads(response.json())

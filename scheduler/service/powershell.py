# -*- coding: utf-8 -*-
"""
PowerShell 스크립트를 전달할 함수들을 가지고 있는 PowerShell 클래스를 정의한다.
하나의 파워쉘 스크립트당 하나의 함수로 구현한다.
모든 함수명은 소문자로, -는 _로 표현한다
다른 결과가 나오지만 같은 명령어를 사용하여 함수명이 겹칠 경우, 함수명 뒤에 _(역할)로 추가적으로 함수명을 구분해준다.
"""

import datetime
from db.models import *

__author__ = 'nhcho'

import json
import requests


class BackupPowerShell(object):
    # 스크립트 실행 결과를 JSON 형식으로 받도록 하기 위한 커맨드
    CONVERTTO_JSON = " | ConvertTo-Json -Compress"
    # Script Default 설정이 리턴값을 주지 않는 경우 해당 옵션이 추가되어야 리턴값이 나온다.
    PASSTHRU = " -Passthru"
    VERBOSE = " -Verbose"

    def __init__(self, address, uri):
        self.address = address
        self.uri = uri

    # create backup
    def create_backup(self, vm_Id, local_path, backup_path):
        backup_id = "_"+datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        script = '$vm = Get-VM -Id '
        script += vm_Id + ';'
        script += '$VMname = $vm.Name;'
        script += '$CloneVMname = "' +backup_id+'";'
        script += 'Export-VM -Name $VMname -Path '+local_path+'/$VMname"clone"/ '+';'
        script += 'Move-Item '+local_path+'/$VMname"clone"/$VMname/"Virtual Hard Disks"/$VMName.vhdx '
        script += '-Destination '+backup_path+'/$VMName$CloneVMname".vhdx";'
        script += 'Remove-Item -Path '+local_path+'/$VMname"clone" -Recurse ;'
        script += 'Get-ChildItem -Path '+backup_path+'/$VMName'
        script += '"' + backup_id
        script += '.vhdx"| Select-Object -Property Name | ConvertTo-Json -Compress'
        # print script
        return self.send(script)

    # delete backup
    def delete_backup(self, filename, path):
        script = 'Remove-Item -Path %s/%s ;' % (path, filename)
        return self.send(script)

    # agent 모듈에 파워쉘 스크립트를 전달하여 실행하고 결과를 받아온다.
    def send(self, script):
        address = self.address
        uri = self.uri
        url = "http://" + address
        url += "/"
        url += uri
        url += "?script=" + script
        data = {'script': script}
        response = requests.post(url, data=json.dumps(data), timeout=1000 * 60 * 20)
        return json.loads(response.json())
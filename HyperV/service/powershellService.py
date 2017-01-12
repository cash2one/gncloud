# -*- coding: utf-8 -*-
"""
PowerShell 스크립트를 전달할 함수들을 가지고 있는 PowerShell 클래스를 정의한다.
하나의 파워쉘 스크립트당 하나의 함수로 구현한다.
모든 함수명은 소문자로, -는 _로 표현한다
다른 결과가 나오지만 같은 명령어를 사용하여 함수명이 겹칠 경우, 함수명 뒤에 _(역할)로 추가적으로 함수명을 구분해준다.
"""

from HyperV.util.config import config
from HyperV.db.models import *

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
    COMPUTER_NAME = " GNCLOUDWIN "

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
                script += " -" + option + " " + value + ""
            elif option == "MemoryStartupBytes":
                script += " -" + option + " " + "500MB"
            else:
                script += " -" + option + " " + value
        #script += " -Generation " + str(self.GENERATION_TYPE_2)
        script += " -Generation " + str(self.GENERATION_TYPE_1) #1세대 통일하여 생성
        script += self.CONVERTTO_JSON
        # print script
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
            elif option == "MemoryMaximumBytes":
                script += " -" + option + " " + value
            else:
                script += " -" + option + " " + value + " -DynamicMemory"
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        #print vmscript + script
        return self.send(vmscript + script)

    def get_vm_ip_address(self, vmid):
        script = '$vm = Get-VM -Id '+vmid+';'
        script += '$ip = Get-VMNetworkAdapter -VMName $vm.VMName;'
        script += '$ip.IPAddresses.GetValue(0) | ConvertTo-Json'
        return self.send(script)

    def set_vm_ip_address(self, ip, dns_address, dns_sub_address):
        script = '$IP = "'+ip+'";'
        script += '$MaskBits = '+config.MASK_BIT+';'
        script += '$Gateway = "'+config.GATE_WAY+'";'
        script += '$DNS = "' + dns_address + '";'
        script += '$S_DNS = "'+dns_sub_address+'";'
        script += '$IPType = "IPv4";'
        script += '$adapter = Get-NetAdapter | ? {$_.Status -eq "up"};'
        script += 'If (($adapter | Get-NetIPConfiguration).IPv4Address.IPAddress) {'
        script += '    $adapter | Remove-NetIPAddress -AddressFamily $IPType -Confirm:$false}'
        script += 'If (($adapter | Get-NetIPConfiguration).Ipv4DefaultGateway) {'
        script += '    $adapter | Remove-NetRoute -AddressFamily $IPType -Confirm:$false}'
        script += '$adapter | New-NetIPAddress -AddressFamily $IPType -IPAddress $IP -PrefixLength $MaskBits '
        script += '-DefaultGateway $Gateway; '
        script += '$adapter | Set-DnsClientServerAddress -ServerAddresses ($DNS, $S_DNS);'
        script += 'Get-NetAdapter | ConvertTo-Json '
        #self.send(script)
        return self.send_new_vm(script, ip)

    #ip address의 타입을 받기위한 ex) dhcp or static, static은 false로 리턴받음
    def get_ip_address_type(self, ip):
        script = '$wmi = Get-WmiObject win32_networkadapterconfiguration -filter "ipenabled =\'true\'";'
        script += '$wmi.DHCPEnabled | ConvertTo-Json -Compress;'
        return self.send_get_vm_info(script, ip)

    #하드디스크 확장
    def resize_vhd(self, vhd_name, path, size):
        script = 'Resize-VHD -Path '+vhd_name+' -SizeBytes '+str(size)+';'
        script += "$dl=mount-vhd " +vhd_name+" -Passthru | get-disk | get-partition | get-volume;" \
                                            "foreach($x in $dl){" \
                                            "if ($x.FileSystemLabel -eq '') {$drive = $x.DriveLetter;}" \
                                            "Else { $sysize = $x.Size;} " \
                                            "}; " \
                                            "$drive, $sysize | ConvertTo-Json -Compress; "
        result = self.send(script)
        print script
        script = 'resize-partition -DriveLetter '+str(result[0])+' -size '+str(long(size)-long(result[1])-111111111)+';'
        script += 'dismount-vhd '+vhd_name +';'
        print script
        result = self.send(script)
        return result

    # password 셋팅
    def set_password(self,ip, password):
        # script = '$user=[adsi]"WinNT://$env:computerName/gncloud";'
        # script += '$user.setPassword("'+password+'"); '
        # script += '$user:USERNAME | ConvertTo-Json -Compress ;'
        script = 'Set-Item WSMan:\localhost\Client\TrustedHosts -Value "'+ip+'" -Force;'
        script += '$username = "gncloud";'
        script += '$password = "gnc=1151";'
        script += '$secstr = New-Object -TypeName System.Security.SecureString;'
        script += '$password.ToCharArray() | ForEach-Object {$secstr.AppendChar($_)};'
        script += '$cred = new-object -typename System.Management.Automation.PSCredential -argumentlist $username, $secstr;'
        script += '$s = New-PSSession -ComputerName "'+ip+'" -Credential $cred ;'
        script += 'Invoke-Command -Session $s -ScriptBlock {'
        script += '$user=[adsi]"WinNT://$env:computerName/gncloud";'
        script += '$user.setPassword("'+password+'");}'

        # while True:
        #     try:
        #         ret = self.send_new_vm(script, ip)
        #     except:
        #         break
        return self.send(script)

    # Get-WmiObject win32_useraccount | Select-Object -Property Name | ConvertTo-Json
    # user의 리스트를 받아온다. 리스트를 받아온 뒤 Admin 계정에 패스워드 설정 가능


    #vm들이 사용하고 있는 자원들의 정보를 받아온다. 모니터링을 위한 메소드
    def get_vm_usage_info(self, ip):
        script = ""
        return self.send_get_vm_info(script, ip)

    # VHD 파일을 복사
    # example) Convert-VHD -DestinationPath C:\images\2_testvm\disk.vhdx
    # / -Path C:\images\windows10.vhdx -Verbose -Passthru | ConvertTo-Json
    # Return VHDObject
    def convert_vhd(self, **kwargs):
        script = "Convert-VHD"
        for option, value in kwargs.items():
            if option == "Path" or option == "DestinationPath":
                script += " -" + option + " " + value + " "
            elif option == "BlockSizeBytes":
                script += " -" + option + " " + value # + "GB"
            else:
                script += " -" + option + " " + value + " "
        script += self.VERBOSE
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        return self.send(script)

    def move_vhd(self, pool, base, vmid):
        script = "$imagename = Get-ChildItem -Path "+pool+" | Select-Object -Index 0;"
        script += "$orimage = $imagename.Name;"
        script += '$ori_Path = "'+pool+'";'
        script += 'Move-Item -Path $ori_Path"/"$orimage -Destination '+base+';'
        script += '$vm = Get-VM -id  '+vmid+';'
        script += 'Add-VMHardDiskDrive $vm -Path '+base+';'
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
                script += " -" + option + " " + value + " "
            else:
                script += " -" + option + " " + value
        script += self.PASSTHRU
        script += self.CONVERTTO_JSON
        #print vmscript + script
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
    def get_vm_one(self, vm_name):
        script = "Get-VM -Id " + vm_name
        script += self.CONVERTTO_JSON
        return self.send(script)

    # 서버 내의 모든 가상머신 리스트 정보를 가져온다.
    # example) Get-VM
    def get_vm(self):
        script = "Get-VM"
        script += self.CONVERTTO_JSON
        return self.send(script)

    #VM 이미지 삭제
    def delete_vm_Image(self, vhd_File_Name, type, path):
        #하이퍼V폴더에 반드시 backup 폴더가 있어야 합니다.
        script = "Move-Item -Path "+path+"/vhdx/"+type+"/" + vhd_File_Name
        script += " -Destination "+path+"/vhdx/backup/" + vhd_File_Name + " | ConvertTo-Json -Compress;"
        #print script
        return self.send(script)

    #VM 삭제
    def delete_vm(self, vmId, type, path):
        script = "$vm = Get-VM -Id "+vmId+";"
        script += "$vmn = $vm.Name;"
        script += "Remove-VM -VM $vm -Force;"
        script += "Move-Item -Path "+path+"/vhdx/"+type+'/$vmn".vhdx" '
        script += "-Destination "+path+"/vhdx/backup/ | ConvertTo-Json -Compress"
        #print script
        return self.send(script)

    # 모니터링을 위한 스크립트
    def monitor(self, vm_ip):
        script = ""
        return self.send(script)

    #스냅샷 생성
    def create_snap(self, vm_Id, path):
        snapshot_id = "_"+datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        #script = 'Invoke-Command -ComputerName '+computer_name+' -ScriptBlock {'
        script = '$vm = Get-VM -Id '
        script += vm_Id + ';'
        script += '$VMname = $vm.Name;'
        script += '$CloneVMname = "' +snapshot_id+'";'
        script += 'Export-VM -Name $VMname -Path '+path+'/$VMname"clone"/ '+';'
        script += 'Move-Item '+path+'/$VMname"clone"/$VMname/"Virtual Hard Disks"/$VMName.vhdx '
        script += '-Destination '+path+'/vhdx/snap/$VMName$CloneVMname".vhdx";'
        script += 'Remove-Item -Path '+path+'/$VMname"clone" -Recurse ;'
        script += 'Get-ChildItem -Path '+path+'/vhdx/snap/$VMName'
        script += '"' + snapshot_id
        script += '.vhdx"| Select-Object -Property Name | ConvertTo-Json -Compress'
        # print script
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

    #새로 생성된 agent에 전달, timeout은 그대로
    def send_get_vm_info(self, script, address):
        port = str(self.port)
        uri = self.uri
        url = "http://" + address
        url += ":"
        url += port
        url += "/"
        url += uri
        url += "?script=" + script
        data = {'script': script}
        response = requests.post(url, data=json.dumps(data), timeout=1000 * 60 * 20)
        return json.loads(response.json())

    # 새로 생성된 agent에 전달, setting을 위해 timeout이 작은값을 넣는다
    def send_new_vm(self, script, address):
        port = str(self.port)
        uri = self.uri
        url = "http://" + address
        url += ":"
        url += port
        url += "/"
        url += uri
        url += "?script=" + script
        data = {'script': script}
        response = requests.post(url, data=json.dumps(data), timeout=10)
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

def vm_monitor(sql_session):
    print '====================================vm monioter================================================='
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.type == 'hyperv').filter(GnVmMachines.status == 'Running').all()
    for seq in vm_info:
        host = sql_session.query(GnHostMachines).filter(GnHostMachines.id == seq.host_id).first()
        ps = PowerShell(host.ip, host.host_agent_port, "powershell/execute")

        script = 'Get-VM -id '+seq.internal_id+' | Select-Object -Property id, cpuusage, memoryassigned | ConvertTo-Json '
        vm_monitor = ps.send(script)

        script = 'Get-VHD -VMId ' +seq.internal_id+' | Select-Object -Property Filesize, Size | ConvertTo-Json;'
        hdd_usage = ps.send(script)
        #hdd = float(hdd_usage['FileSize'])/float(hdd_usage['Size'])
        hdd = float(hdd_usage['FileSize'])

        mem = round((float(vm_monitor['MemoryAssigned']))/float(seq.memory), 4) * 100
        cpu = round(float(vm_monitor['CPUUsage'])*float((host.cpu/seq.cpu)), 4)

        script = '$vm = Get-vm -id '+ seq.internal_id+';'
        script += '$ip = Get-VMNetworkAdapter -VM $vm | Select-Object -Property IPAddresses;'
        script += '$ip.IPAddresses.GetValue(0) | ConvertTo-Json ;'
        ip = ps.send(script)
        print hdd
        print cpu
        print mem
        print ip
        try:
            monitor_insert = GnMonitorHist(seq.id, "hyperv", datetime.datetime.now(), cpu, mem, round(hdd, 4), 0.0000)
            sql_session.add(monitor_insert)
            sql_session.commit()

            sql_session.query(GnMonitor).filter(GnMonitor.id == seq.id).update(
                {"cpu_usage": cpu, "mem_usage": mem, "disk_usage": round(hdd, 4)}
            )
            sql_session.commit()

            sql_session.query(GnVmMachines).filter(GnVmMachines.id == seq.id).update(
                {"ip": ip}
            )
            sql_session.commit()
        except Exception as message:
            print message
            sql_session.rollback()

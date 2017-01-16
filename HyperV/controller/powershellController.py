# -*- coding: utf-8 -*-
"""
Hyper-V를 컨트롤 할 PowerShell Script(서비스의 powershellSerivce에서 제공)를 실행하는 Rest 함수들을 정의한다.
각 Rest 함수들의 이름은 hvm_(Action을 대표하는 영단어 소문자)로 표기한다.
"""
import json

from HyperV.util.json_encoder import AlchemyEncoder
from HyperV.db.models import GnImagesPool, GnHostMachines, GnMonitorHist

__author__ = 'jhjeon'

import datetime
import time
from flask import request, jsonify
from HyperV.service.powershellService import PowerShell
from HyperV.db.database import db_session
from HyperV.db.models import GnVmMachines, GnVmImages, GnMonitor

from HyperV.util.config import config
from HyperV.util.hash import random_string

ps_exec = 'powershell/execute'

def manual():
    script = request.form['script']
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, ps_exec)
    return jsonify(result=ps.send(script))

# VM 생성 및 실행
def hvm_create(id, sql_session):
    try:
        vm_id = id
        vm_info =sql_session.query(GnVmMachines).filter(GnVmMachines.id == vm_id).first()

        host_id =vm_info.host_id
        host_machine = sql_session.query(GnHostMachines).filter(GnHostMachines.id == host_id).first()
        ps = PowerShell(host_machine.ip, host_machine.host_agent_port, ps_exec)

        base_image_info = sql_session.query(GnVmImages).filter(GnVmImages.id == vm_info.image_id).first()

        image_path = "/original/"
        if base_image_info.sub_type == 'snap':
            image_path = "/snap/"

        base_image = base_image_info.filename
        os = base_image_info.os
        os_ver = base_image_info.os_ver
        os_sub_ver = base_image_info.os_subver
        os_bit = base_image_info.os_bit
        internal_name = base_image_info.os_ver + '_' + base_image_info.os_subver + '_' + \
                        base_image_info.os_bit + '_' + vm_id

        SWITCHNAME = "out"
        new_vm = ps.new_vm(Name=internal_name, MemoryStartupBytes=str(vm_info.memory), Path=host_machine.image_path,
                           SwitchName=SWITCHNAME)
        if new_vm is not None:
            # 새 머신에서 추가적인 설정을 한다 (Set-VM)
            set_vm = ps.set_vm(VMId=new_vm['VMId'], ProcessorCount=str(vm_info.cpu), MemoryMaximumBytes=str(vm_info.memory))
            CONVERT_VHD_DESTINATIONPATH = host_machine.image_path+"/vhdx/base/"+internal_name+".vhdx"

            CONVERT_VHD_PATH = host_machine.image_path+"/vhdx"+ image_path + base_image  #원본이미지로부터

            # CONVERT_VHD_DESTINATIONPATH = config.DISK_DRIVE+config.HYPERV_PATH+"/vhdx/base/"+internal_name+".vhdx"
            # CONVERT_VHD_PATH = config.DISK_DRIVE+config.HYPERV_PATH+"/vhdx/original/" + base_image  #원본이미지로부터

            convert_vhd = ps.convert_vhd(DestinationPath=CONVERT_VHD_DESTINATIONPATH, Path=CONVERT_VHD_PATH)
            add_vmharddiskdrive = ps.add_vmharddiskdrive(VMId=new_vm['VMId'], Path=CONVERT_VHD_DESTINATIONPATH)

            # hdd 확장
            if vm_info.disk > 21475000000 and base_image_info.sub_type == 'base':
                ps.resize_vhd(host_machine.image_path+"/vhdx/base/"+internal_name+".vhdx", host_machine.image_path, vm_info.disk)

            start_vm = ps.start_vm(new_vm['VMId'])

            get_ip_count = 0
            get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])

            while True:
                if len(get_vm_ip) <= 2 and get_ip_count <= 160:
                    #print get_vm_ip
                    time.sleep(5)
                    get_ip_count = get_ip_count + 1
                    get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])
                elif get_ip_count > 160:
                    return False
                # elif get_vm_ip[:2] == "16":
                #     time.sleep(5)
                #     get_ip_count = get_ip_count + 1
                #     get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])
                else:
                    break

            count = 0
            # password setting
            while True:
                time.sleep(5)
                count += 1
                if count >= 50 or base_image_info.sub_type == 'snap':
                    break
                try:
                    ps.set_password(get_vm_ip, vm_info.hyperv_pass)
                except Exception as message:
                    break

            vm_info.internal_id=new_vm['VMId']
            vm_info.internal_name=internal_name
            vm_info.ip = get_vm_ip
            vm_info.os = os
            vm_info.os_ver = os_ver
            vm_info.os_sub_ver = os_sub_ver
            vm_info.os_bit = os_bit
            vm_info.create_time = datetime.datetime.now()
            vm_info.start_time = datetime.datetime.now()
            vm_info.status = ps.get_state_string(start_vm['State'])

            insert_monitor = GnMonitor(vm_id, 'hyperv', 0.0000, 0.0000, 0.0000, 0.0000)
            sql_session.add(insert_monitor)
            sql_session.commit()
            sql_session.remove()
            return True
    except:
        vm_info.status = "Error"
        sql_session.commit()
        sql_session.remove()
        return True


def hvm_snapshot():
    vm_info = db_session.query(GnVmImages).filter(GnVmImages.id == request.json['vm_id']).first()
    org_id = db_session.query(GnVmMachines).filter(GnVmMachines.id == request.json['ord_id']).first()

    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.id == org_id.host_id).first()
    image_pool = db_session.query(GnImagesPool).filter(GnImagesPool.host_id == org_id.host_id).first()

    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, ps_exec)
    create_snap = ps.create_snap(org_id.internal_id, image_pool.image_path)
    try:
        if create_snap['Name'] is not None:
            # base_image_info = db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == org_id.internal_id).first()

            filename = create_snap['Name']
            icon = 'gn_icon_windows.png'

            vm_info.filename = filename
            vm_info.icon = icon
            vm_info.status = "Running"
            vm_info.os_ver = org_id.os_ver
            vm_info.host_id = host_machine.id
            db_session.commit()

            start_vm = ps.start_vm(org_id.internal_id)
            if start_vm['State'] is 2:
                return jsonify(status=True)
            else:
                vm_info.status="Error"
                db_session.commit()
                return jsonify(status=False)
    except:
        vm_info.status="Error"
        db_session.commit()
        return jsonify(status=False)

# -------------------------------------------------------
# REST. VM 상태변경
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

    vmid = db_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.id == vmid.host_id).first()
    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, ps_exec)

    type = request.json['type']
    #print vmid.internal_id
    #    vm = GnVmMachines.query.filter_by().first
    if type == "Resume":
        # VM 시작
        # 1. 가상머신을 시작한다. (Start-VM)
        start_vm = ps.start_vm(vmid.internal_id)
        # start_vm
        # print id
        # 2. 가상머신 상태를 체크한다. (Get-VM)
        if start_vm['State'] is 2:
            update = db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == start_vm['Id']).update(
                {"status": "Running", "start_time": datetime.datetime.now()})
            db_session.commit()
            # print start_vm['Id']
            return jsonify(status=True, message="start success")
        elif start_vm['State'] is not 2:
            return jsonify(status=False, message="fail")
        else:
            return jsonify(status=False, message="정상적인 결과가 아닙니다.")
    elif type == "stop" or type == "shutdown" :
        # stop 1. 가상머신을 정지한다. (Stop-VM)
        stop = ps.stop_vm(vmid.internal_id)
        # stop 2. 가상머신 상태를 체크한다. (Get-VM)
        if stop['State'] is 3:
            # stop 3. 변경된 가상머신 상태를 DB에 업데이트한다.
            update = db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == stop['Id']).update(
                {"status": "Stop", "stop_time": datetime.datetime.now()})
            db_session.commit()
            return jsonify(status=True, message="VM Stop")
        else:
            return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
            # return jsonify(status=False, message="상태 미완성")
    elif type == "Reboot":
        restart = ps.restart_vm(vmid.internal_id)
        # resume 1. 가상머신을 재시작한다. (Restart-VM)
        if restart['State'] is 2:
            update = db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == restart['Id']).update(
                {"start_time": datetime.datetime.now(), "stop_time": datetime.datetime.now()})
            db_session.commit()
            return jsonify(status=True, message="VM Restart")
        else:
            return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
    elif type == "Suspend":
        suspend = ps.suspend_vm(vmid.internal_id)
        if suspend['State'] is 9:
            update = db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == suspend['Id']).update(
                {"status": "Suspend"})
            db_session.commit()
            return jsonify(status=True, message="가상머신이 일시정지되었습니다.")
        else:
            return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
    elif type == "powerdown":
        return jsonify(status=False, message="상태 미완성")
    else:
        return jsonify(status=False, message="정상적인 상태 정보를 받지 못했습니다.")


# REST. VM 삭제
def hvm_delete(id):
    vmid = db_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.id == vmid.host_id).first()
    image_pool = db_session.query(GnImagesPool).filter(GnImagesPool.host_id == vmid.host_id).first()

    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, ps_exec)
    vm_info =ps.get_vm_one(vmid.internal_id)
    #  REST hvm_delete 1. Powershell Script를 통해 VM을 정지한다.
    stop_vm = ps.stop_vm(vmid.internal_id)
    if stop_vm['State'] is 3:
        delete_vm = ps.delete_vm(vmid.internal_id, "base", image_pool.image_path)
        update_vm_machines = db_session.query(GnVmMachines).filter(GnVmMachines.id
                                                                   == id).update({"status" : "Removed"})
        db_session.commit()
        update_vm_images = db_session.query(GnVmImages).filter(GnVmImages.filename == vm_info['VMName']
                                                               +".vhdx").update({"status" : "Removed"})
        db_session.commit()
        # REST hvm_delete 2. VM을 삭제한다.
        # todo REST hvm_delete 3. 삭제된 VM DB 데이터를 삭제 상태로 업데이트한다.
        return jsonify(message="Remove success", status=True)


# todo REST. VM 정보
def hvm_vm(vmid):
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.name == 'hyperv').first()
    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, ps_exec)
    # Powershell Script를 통해 VM 정보를 가져온다.
    vm = ps.get_vm_one(vmid)
    # todo get-vm. VM 정보를 DB에서 가져온다.
    return jsonify(vm=vm, message="", status=True)


# todo REST. VM 리스트 정보
def hvm_vm_list():
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.name == 'hyperv').first()
    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, ps_exec)
    vm_list = ps.get_vm()
    # todo get-vm. VM 정보를 DB에서 가져온다.
    return jsonify(list=vm_list, message="", status=True)


# REST. VM 이미지 생성 및 업로드
# 업로드 기능은 나중에 구현 예정, 이미지 정보만 업데이트할 것
def hvm_new_image():

    name = request.json['name']
    filename = request.json['filename']
    icon = request.json['icon']
    os = request.json['os']
    os_ver = request.json['os_ver']
    os_subver = request.json['os_subver']
    subtype = request.json['subtype']
    type = request.json['type']
    author_id = request.json['author_id']
    os_bit = request.json['os_bit']
    team_code = request.json['team_code']

    insert_image_query = GnVmImages(random_string(config.SALT, 8), name, filename, type, subtype,
                                    icon, os, os_ver, os_subver, os_bit, team_code,
                                    author_id, datetime.datetime.now())
    db_session.add(insert_image_query)
    db_session.commit()

    return jsonify(status=True, message="success")


# tdo REST. VM 이미지 수정
def hvm_modify_image(id):
    # null 값이 들어오면 수정 하지 않는 기능으로 구현 .....
    # db값은 frontend 에서 수정함.....
    return jsonify(status=False, message="미구현")


# REST. VM 이미지 삭제
# 이미지를 백업 폴더로 옮긴다
# 이미지 따로 관리
def hvm_delete_image(id):
    vhd_Name = db_session.query(GnVmImages).filter(GnVmImages.id == id).first()
    image_pool = db_session.query(GnImagesPool).filter(GnImagesPool.host_id == vhd_Name.host_id).first()
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.id == vhd_Name.host_id).first()

    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, ps_exec)
    image_delete = ps.delete_vm_Image(vhd_Name.filename, vhd_Name.sub_type, image_pool.image_path)

    json_obj = json.dumps(image_delete)
    json_size = len(json_obj)
    if json_size <= 2: #json 크기는 '{}' 포함
        delete_vm = db_session.query(GnVmImages).filter(GnVmImages.id == id).update({"status": "Removed"})
        db_session.commit()
        #update 완료시 리턴값은 1
        if delete_vm == 1:
            return jsonify(status=True, message="image delete complete")
        else:
            return jsonify(status=False, message="DB update fail")
    else:
        return jsonify(status=False, message="image delete fail")


# REST. VM 이미지 리스트
def hvm_image_list(type):
    list_get_query = db_session.query(GnVmImages).filter(GnVmImages.sub_type == type).all()
    get_items_to_json = json.dumps(list_get_query, cls=AlchemyEncoder)
    json.loads(get_items_to_json)
    return jsonify(status=True, message="success", list=json.loads(get_items_to_json))


# todo REST. VM 이미지 정보
def hvm_image():
    return jsonify(status=False, message="미구현")


def vm_monitor(sql_session):

    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.type == 'hyperv').filter(GnVmMachines.status == 'Running').all()
    for seq in vm_info:
        host = sql_session.query(GnHostMachines).filter(GnHostMachines.id == seq.host_id).first()
        ps = PowerShell(host.ip, host.host_agent_port, "powershell/execute")

        script = 'Get-VM -id '+seq.internal_id+' | Select-Object -Property id, cpuusage, memoryassigned | ConvertTo-Json '
        monitor = ps.send(script)

        script = 'Get-VHD -VMId ' +seq.internal_id+' | Select-Object -Property Filesize, Size | ConvertTo-Json;'
        hdd_usage = ps.send(script)
        #hdd = float(hdd_usage['FileSize'])/float(hdd_usage['Size'])
        hdd = float(hdd_usage['FileSize'])

        mem = round((float(monitor['MemoryAssigned']))/float(seq.memory), 4) * 100
        cpu = round(float(monitor['CPUUsage'])*float((host.cpu/seq.cpu)), 4)

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



# 모니터링을 위한 스크립트 전송 함수
'''
def vm_monitor():
    vm_ip_info = db_session.query(GnVmMachines).filter(GnVmMachines.type == "hyperv").all()
    for i in range(0, len(vm_ip_info)):
        if vm_ip_info[i].status == "Running":
            ps = PowerShell(vm_ip_info[i].ip, config.AGENT_PORT, ps_exec)
            script = "$freemem = Get-WmiObject -Class Win32_OperatingSystem;"
            script += "$mem = $freemem.FreePhysicalMemory / $freemem.TotalVirtualMemorySize;"
            script += "$idle = Get-Counter '\Process(idle)\% Processor Time' | "
            script += "Select-Object -ExpandProperty countersamples | "
            script += "Select-Object -Property instancename, cookedvalue| "
            script += "Sort-Object -Property cookedvalue -Descending;"
            script += "$total = Get-Counter '\Process(_total)\% Processor Time' | "
            script += "Select-Object -ExpandProperty countersamples |"
            script += "Select-Object -Property instancename, cookedvalue| "
            script += "Sort-Object -Property cookedvalue -Descending;"
            script += "$res = (($idle.CookedValue/$total.CookedValue)) ;"
            script += "$hdd = Get-PSDrive C |Select-Object Free;"
            script += "$hdd = $hdd.Free /1024 /1024/ 1024;"
            script += "$res, $mem, $hdd | ConvertTo-Json -Compress;"
            try:
                result = json.loads(json.dumps(ps.send_get_vm_info(script, vm_ip_info[i].ip)))
            except Exception as message:
                print message
            # finally:
            #     print result

            cpu = round(1 - result[0], 4)  #점유량 ex) 0.3~~
            mem = round(1 - result[1], 4)
            hdd = round(1 - (result[2]/float(vm_ip_info[i].disk)), 4)
            #hdd_free_per = hdd/float(vm_ip_info[i].disk)

            if cpu >= 1.0:
                cpu = 1.0000
            elif cpu <= 0:
                cpu = 0.0000
            else:
                cpu = round(1-result[0], 4)

            try:
                monitor_insert = GnMonitorHist(vm_ip_info[i].id, "hyperv", datetime.datetime.now(),
                                               cpu, mem*100, hdd, 0.0000)
                db_session.add(monitor_insert)
                db_session.query(GnMonitor).filter(GnMonitor.id == vm_ip_info[i].id).update(
                    {"cpu_usage": cpu, "mem_usage": mem*100, "disk_usage":hdd} )
            except Exception as message:
                print message
                db_session.rollback()
            finally:
                db_session.commit()
                #print "Running status"
        elif vm_ip_info[i].status != "Removed": #단순히 db만 업데이트
            #print "stop status"
            try:
                vm_info = db_session.query(GnMonitor).filter(GnMonitor.id == vm_ip_info[i].id).first()

                monitor_insert = GnMonitorHist(vm_ip_info[i].id, "hyperv", datetime.datetime.now(),
                                               0.0000, 0.0000, vm_info.disk_usage, 0.0000)
                db_session.add(monitor_insert)
                db_session.query(GnMonitor).filter(GnMonitor.id == vm_ip_info[i].id).update(
                    {"cpu_usage": 0.0000, "mem_usage": 0.0000})
                #print "insert success"
            except Exception as message:
                print message
                db_session.rollback()
            finally:
                db_session.commit()
'''
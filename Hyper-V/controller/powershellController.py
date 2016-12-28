# -*- coding: utf-8 -*-
"""
Hyper-V를 컨트롤 할 PowerShell Script(서비스의 powershellSerivce에서 제공)를 실행하는 Rest 함수들을 정의한다.
각 Rest 함수들의 이름은 hvm_(Action을 대표하는 영단어 소문자)로 표기한다.
"""
import json

from util.json_encoder import AlchemyEncoder

__author__ = 'jhjeon'

import datetime
import time
from flask import request, jsonify, session
from service.powershellService import PowerShell
from db.database import db_session
from db.models import GnVmMachines, GnVmImages, GnMonitor, GnMonitorHist, GnImagesPool

from util.config import config
from util.hash import random_string




# PowerShell Script Manual 실행: (Script) | ConvertTo-Json
def manual():
    script = request.form['script']
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    # return ps.send(script)
    return jsonify(result=ps.send(script))

# VM 생성 및 실행
def hvm_create():
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)

    base_image_info = db_session.query(GnVmImages).filter(GnVmImages.id == request.json['id']).first()

    base_image = base_image_info.filename
    name = request.json['vm_name']
    tag = request.json['tag']
    memory = request.json['memory']
    cpu = request.json['cpu']
    hdd = request.json['hdd']
    os = base_image_info.os
    os_ver = base_image_info.os_ver
    os_sub_ver = base_image_info.os_subver
    os_bit = base_image_info.os_bit
#    print session['teamCode']
#    team_code = session.get('teamCode')
    team_code = session['teamCode']
    author_id = session['userName']

    #vm에 대한 명명규칙
    internal_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    # 새 머신을 만든다. (New-VM)
    # hvm_create test value 1. Path 및 SwitchName은 추후 DB에서 불러올 값들이다.
    SWITCHNAME = "out"
    new_vm = ps.new_vm(Name=internal_name, MemoryStartupBytes=str(memory), Path=config.DISK_DRIVE+config.HYPERV_PATH,
                       SwitchName=SWITCHNAME)


    # 머신이 생성되었는지 확인한다. (New-VM 리턴값 체크)
    if new_vm is not None:
        # 새 머신에서 추가적인 설정을 한다 (Set-VM)
        set_vm = ps.set_vm(VMId=new_vm['VMId'], ProcessorCount=str(cpu))
        #print set_vm
        # 정해진 OS Type에 맞는 디스크(VHD 또는 VHDX)를 가져온다. (Convert-VHD)
        # CONVERT_VHD_PATH 및 SwitchName은 추후 DB에서 불러올 값들이다.
        #image_pool = db_session.query(GnImagesPool).filter(GnImagesPool.type == "hyperv").first()
        CONVERT_VHD_DESTINATIONPATH = config.DISK_DRIVE+config.HYPERV_PATH+"/vhdx/base/"+internal_name+".vhdx"
        CONVERT_VHD_PATH = config.DISK_DRIVE+ config.HYPERV_PATH+"/vhdx/original/" + base_image  #원본이미지로부터
        convert_vhd = ps.convert_vhd(DestinationPath=CONVERT_VHD_DESTINATIONPATH, Path=CONVERT_VHD_PATH)
        # 가져온 디스크를 가상머신에 연결한다. (Add-VMHardDiskDrive)
        add_vmharddiskdrive = ps.add_vmharddiskdrive(VMId=new_vm['VMId'], Path=CONVERT_VHD_DESTINATIONPATH)
        # VM을 시작한다.
        start_vm = ps.start_vm(new_vm['VMId'])
        # 생성된 VM의 ip 정보를 가지고 온다

        get_ip_count = 0
        get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])

        while True:
            if len(get_vm_ip) <= 2 and get_ip_count <= 20:
                time.sleep(20)
                get_ip_count = get_ip_count + 1
                get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])
            elif get_ip_count > 20:
                return jsonify(status=False, massage="VM 생성 실패")
            else:
                get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])
                break

        # print get_vm_ip
        # 생성된 VM의 ip 정보를 고정한다

        dhcp_ip_address = ps.get_ip_address_type(get_vm_ip)

        while True:
            if dhcp_ip_address is True:
                try:
                    ps.set_vm_ip_address(get_vm_ip, config.DNS_ADDRESS, config.DNS_SUB_ADDRESS)
                except Exception as message:
                    print message
                    ps.get_ip_address_type(get_vm_ip)
                finally:
                    dhcp_ip_address = ps.get_ip_address_type(get_vm_ip)
            else:
                try:
                    hostid = db_session.query(GnImagesPool).filter(GnImagesPool.type == "hyperv").first()

                    vmid = random_string(config.SALT, 8)
                    vm = GnVmMachines(vmid, name, tag, 'hyperv', start_vm['VMId'],
                                      internal_name,
                                      hostid.host_id, get_vm_ip, cpu, memory, hdd,
                                      os
                                      , os_ver, os_sub_ver, os_bit, team_code,
                                      author_id, datetime.datetime.now(),
                                      datetime.datetime.now(), None, ps.get_state_string(start_vm['State']))

                    insert_monitor = GnMonitor(vmid, 'hyperv', 0.0000, 0.0000, 0.0000, 0.0000)
                    db_session.add(insert_monitor)
                    db_session.add(vm)

                except Exception as message:
                    print message
                    db_session.rollback()
                    return jsonify(status=False, massage="DB insert fail")
                finally:
                    db_session.commit()
                return jsonify(status=True,massage = "create vm success")
    else:
        return jsonify(status=False, massage="VM 생성 실패")


#  REST. VM 스냅샷 생성
#  hvm_snapshot 1. VM 정지 (Stop-VM)
#  hvm_snapshot 2. 스냅샷을 생성한다.
#  hvm_snapshot 3. 생성된 스냅샷 이미지 이름 변경 (2번에서 이름 변경이 안 될 경우)
#  hvm_snapshot 4. 생성된 스냅샷 이미지 이름 를 지정된 폴더에 옮긴다. (테스트 때에는 C:\images 로 한다.)
#  hvm_snapshot 5. 생성된 스냅샷의 정보를 데이터베이스에 저장한다.
def hvm_snapshot():
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    # 지금은 internal_id 받아야한다
    #org_id = request.json['org_id'] #원본 이미지 아이디
    org_id = db_session.query(GnVmMachines).filter(GnVmMachines.id == request.json['ord_id']).first()

    stop_vm = ps.stop_vm(org_id.internal_id) #원본 이미지 인스턴스 종료
    if stop_vm['State'] is 3:
        create_snap = ps.create_snap(org_id.internal_id, config.COMPUTER_NAME)
       # print create_snap
        if create_snap['Name'] is not None:
            base_image_info = db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == org_id.internal_id).first()

            name = request.json['name'] #request name 으로 저장해야한다.

            filename = create_snap['Name']
            icon = 'icon_path'
            os = base_image_info.os
            os_ver = base_image_info.os_ver
            os_subver = base_image_info.os_sub_ver
            subtype = 'snap'
            type = request.json['type']
            author_id = session['userName']
            #author_id = request.json['author_id']

            os_bit = base_image_info.os_bit
            #team_code = request.json['team_code']
            team_code = session['teamCode']

            insert_image_query = GnVmImages(random_string(config.SALT, 8), name, filename, type, subtype,
                                            icon, os, os_ver, os_subver, os_bit, team_code,
                                            author_id, datetime.datetime.now(), 'Running', None)
            db_session.add(insert_image_query)
            db_session.commit()

            start_state = ps.start_vm(org_id.internal_id)

            if start_state['State'] is 2:
                return jsonify(status=True, message="성공")
            else:
                return jsonify(status=False, message="VM시작을 하지 못하였습니다")
        else:
            return jsonify(status=False, message="실패")
    else:
        return jsonify(status=False, message="실패")

'''
    org_id = request.form['org_id']
    name = request.form['name']
    type = request.form['type']
    author_id = request.form['author_id']
'''



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
    type = request.json['type']
    # type = request.args.get('type')
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)

    vmid = db_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()
  #  print vmid.internal_id
    #    vm = GnVmMachines.query.filter_by().first
    if type == "start":
        # VM 시작
        # 1. 가상머신을 시작한다. (Start-VM)
        start_vm = ps.start_vm(vmid.internal_id)
       # print start_vm
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
    elif type == "stop":
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
    elif type == "restart":
        restart = ps.restart_vm(vmid.internal_id)
        # resume 1. 가상머신을 재시작한다. (Restart-VM)
        if restart['State'] is 2:
            return jsonify(status=True, message="VM Restart")
        else:
            return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
            # resume 2. 가상머신 상태를 체크한다. 다만 (Get-VM)
    elif type == "shutdown":
        # todo shutdown 1.
        return jsonify(status=False, message="미구현")
    elif type == "suspend":
        suspend = ps.suspend_vm(vmid.internal_id)
        if suspend['State'] is 9:
            update = db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == suspend['Id']).update(
                {"status": "Suspend"})
            db_session.commit()
            return jsonify(status=True, message="가상머신이 일시정지되었습니다.")
        else:
            return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
    elif type == "resume":
        resume = ps.resume_vm(vmid.internal_id)
        if resume['State'] is 2:
            update = db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == resume['Id']).update(
                {"status": "Running"})
            db_session.commit()
            return jsonify(status=True, message="가상머신이 재시작되었습니다.")
        else:
            return jsonify(status=True, message="정상적인 결과값이 아닙니다.")
    elif type == "powerdown":
        return jsonify(status=False, message="상태 미완성")
    else:
        return jsonify(status=False, message="정상적인 상태 정보를 받지 못했습니다.")


# todo REST. VM 삭제
def hvm_delete(id):
    vmid = db_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    vm_info =ps.get_vm_one(vmid.internal_id)
    #  REST hvm_delete 1. Powershell Script를 통해 VM을 정지한다.
    stop_vm = ps.stop_vm(vmid.internal_id)
    if stop_vm['State'] is 3:
        delete_vm = ps.delete_vm(vmid.internal_id, "base", config.COMPUTER_NAME)
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
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    # Powershell Script를 통해 VM 정보를 가져온다.
    vm = ps.get_vm_one(vmid)
    # todo get-vm. VM 정보를 DB에서 가져온다.
    return jsonify(vm=vm, message="", status=True)


# todo REST. VM 리스트 정보
def hvm_vm_list():
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
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
    ps = PowerShell(config.AGENT_SERVER_IP, config.AGENT_PORT, config.AGENT_REST_URI)
    vhd_Name = db_session.query(GnVmImages).filter(GnVmImages.id == id).first()
    image_delete = ps.delete_vm_Image(vhd_Name.filename, vhd_Name.sub_type, config.COMPUTER_NAME)
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


# 모니터링을 위한 스크립트 전송 함수
def vm_monitor():
    vm_ip_info = db_session.query(GnVmMachines).filter(GnVmMachines.type == "hyperv").all()
    for i in range(0, len(vm_ip_info)):
        if vm_ip_info[i].status == "Running":
            ps = PowerShell(vm_ip_info[i].ip, config.AGENT_PORT, config.AGENT_REST_URI)
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
                cpu = round(1 - result[0], 4)  #점유량 ex) 0.3~~
                mem = round(1 - result[1], 4)
                hdd = round(1 - (result[2]/float(vm_ip_info[i].disk)), 4)
                #hdd_free_per = hdd/float(vm_ip_info[i].disk)

                if cpu >= 1.0:
                    cpu = 0.0000
                elif cpu <= 0:
                    cpu = 1.0000
                else:
                    cpu = round(1-result[0], 4)
                monitor_insert = GnMonitorHist(vm_ip_info[i].id, "hyperv", datetime.datetime.now(),
                                               cpu, mem*100, hdd, 0.0000)
                db_session.add(monitor_insert)
                db_session.query(GnMonitor).filter(GnMonitor.id == vm_ip_info[i].id).update(
                    {"cpu_usage": cpu, "mem_usage": mem*100, "disk_usage":hdd} )
            except Exception as message:
                print message
                db_session.rollback()
            finally:
               # print result
                db_session.commit()

        elif vm_ip_info[i].status != "Removed": #단순히 db만 업데이트
           # print "stop status"
            try:
                vm_info = db_session.query(GnMonitor).filter(GnMonitor.id == vm_ip_info[i].id).first()

                monitor_insert = GnMonitorHist(vm_ip_info[i].id, "hyperv", datetime.datetime.now(),
                                               0.0000, 0.0000, vm_info.disk_usage, 0.0000)
                db_session.add(monitor_insert)
                db_session.query(GnMonitor).filter(GnMonitor.id == vm_ip_info[i].id).update(
                    {"cpu_usage": 0.0000, "mem_usage": 0.0000})
               # print "insert success"
            except Exception as message:
                print message
                db_session.rollback()
            finally:
                db_session.commit()


# -*- coding: utf-8 -*-
"""
Hyper-V를 컨트롤 할 PowerShell Script(서비스의 powershellSerivce에서 제공)를 실행하는 Rest 함수들을 정의한다.
각 Rest 함수들의 이름은 hvm_(Action을 대표하는 영단어 소문자)로 표기한다.
"""
import json

from util.json_encoder import AlchemyEncoder
from db.models import GnImagesPool, GnMonitorHist, GnHostMachines

__author__ = 'jhjeon'

import datetime
import time
from flask import request, jsonify, session
from service.powershellService import PowerShell
from db.database import db_session
from db.models import GnVmMachines, GnVmImages, GnMonitor, GnMonitorHist
from sqlalchemy import func

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

    name = request.json['vm_name']
    tag = request.json['tag']
    memory = request.json['memory']
    cpu = request.json['cpu']
    hdd = request.json['hdd']

    team_code = session['teamCode']
    author_id = session['userName']

    password = request['password']

    # team_code = request.json['teamCode']
    # author_id = request.json['userName']


    #host machine 선택
    host_ip = None
    host_id = None

    #Gn_host_machines 테이블의 컬럼선택은 변경가능, type컬럼이 아닌 hyper-v 를 select 할 수 있는 컬럼을 선택하여도 된다.
    host_list = db_session.query(GnHostMachines).filter(GnHostMachines.type == "hyper_V").all()

    for host_info in host_list:
        use_sum_info = db_session.query(func.ifnull(func.sum(GnVmMachines.cpu),0).label("sum_cpu"),
                                        func.ifnull(func.sum(GnVmMachines.memory),0).label("sum_mem"),
                                        func.ifnull(func.sum(GnVmMachines.disk),0).label("sum_disk")
                                        ).filter(GnVmMachines.host_id == host_info.id).filter(GnVmMachines.status != "Removed").one_or_none()
        rest_cpu = host_info.max_cpu - use_sum_info.sum_cpu
        rest_mem = host_info.max_mem - use_sum_info.sum_mem
        rest_disk = host_info.max_disk - use_sum_info.sum_disk

        if rest_cpu >= int(cpu) and rest_mem >= int(memory) and rest_disk >= int(hdd):
            host_ip = host_info.ip
            host_id = host_info.id
            break

    if host_ip is None:
        result = {"status":False, "message" : "HOST 머신 리소스가 부족합니다"}
        return jsonify(status=result["status"], message=result["message"])

    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.id == host_id).first()
    image_pool = db_session.query(GnImagesPool).filter(GnImagesPool.host_id == host_id).first()

    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, config.AGENT_REST_URI)

    base_image_info = db_session.query(GnVmImages).filter(GnVmImages.id == request.json['id']).first()

    base_image = base_image_info.filename
    os = base_image_info.os
    os_ver = base_image_info.os_ver
    os_sub_ver = base_image_info.os_subver
    os_bit = base_image_info.os_bit
    #    print session['teamCode']
    #    team_code = session.get('teamCode')

    #vm에 대한 명명규칙
    internal_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    # 새 머신을 만든다. (New-VM)
    # hvm_create test value 1. Path 및 SwitchName은 추후 DB에서 불러올 값들이다.
    SWITCHNAME = "out"
    new_vm = ps.new_vm(Name=internal_name, MemoryStartupBytes=str(memory), Path=image_pool.image_path,
                       SwitchName=SWITCHNAME)


    # 머신이 생성되었는지 확인한다. (New-VM 리턴값 체크)
    if new_vm is not None:
        # 새 머신에서 추가적인 설정을 한다 (Set-VM)
        set_vm = ps.set_vm(VMId=new_vm['VMId'], ProcessorCount=str(cpu))
        #print set_vm
        # 정해진 OS Type에 맞는 디스크(VHD 또는 VHDX)를 가져온다. (Convert-VHD)
        # CONVERT_VHD_PATH 및 SwitchName은 추후 DB에서 불러올 값들이다.
        CONVERT_VHD_DESTINATIONPATH = image_pool.image_path+"/vhdx/base/"+internal_name+".vhdx"
        CONVERT_VHD_PATH = image_pool.image_path+"/vhdx/original/" + base_image  #원본이미지로부터
        # CONVERT_VHD_DESTINATIONPATH = config.DISK_DRIVE+config.HYPERV_PATH+"/vhdx/base/"+internal_name+".vhdx"
        # CONVERT_VHD_PATH = config.DISK_DRIVE+config.HYPERV_PATH+"/vhdx/original/" + base_image  #원본이미지로부터

        convert_vhd = ps.convert_vhd(DestinationPath=CONVERT_VHD_DESTINATIONPATH, Path=CONVERT_VHD_PATH)
        # 가져온 디스크를 가상머신에 연결한다. (Add-VMHardDiskDrive)
        add_vmharddiskdrive = ps.add_vmharddiskdrive(VMId=new_vm['VMId'], Path=CONVERT_VHD_DESTINATIONPATH)

        ''' 이미 생생된 이미지의 패스를 옮겨서 vm과 연결할 때 사용 가능한 스크립트.
        CONVERT_VHD_DESTINATIONPATH = config.DISK_DRIVE + config.HYPERV_PATH + "/vhdx/base/"+internal_name+".vhdx"
        CONVERT_VHD_PATH = config.DISK_DRIVE + config.HYPERV_PATH + "/vhdx/pool/"+os_sub_ver
        ps.move_vhd(CONVERT_VHD_PATH, CONVERT_VHD_DESTINATIONPATH, new_vm['VMId'])
        '''

        # VM을 시작한다.
        start_vm = ps.start_vm(new_vm['VMId'])
        # 생성된 VM의 ip 정보를 가지고 온다

        get_ip_count = 0
        get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])

        while True:
            if len(get_vm_ip) <= 2 and get_ip_count <= 20:
                #print get_vm_ip
                time.sleep(40)
                get_ip_count = get_ip_count + 1
                get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])
            elif get_ip_count > 20:
                return jsonify(status=False, massage="VM에 ip를 할당할 수 없습니다.")
            elif get_vm_ip[:2] == "16":
                time.sleep(40)
                get_ip_count = get_ip_count + 1
                get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])
            else:
                break

        # print get_vm_ip
        # 생성된 VM의 ip 정보를 고정한다

        # ip 고정 부분 , 서버에 올릴시 몇시간정도 서버측에서 접근 거부 에러 발생하여 주석처리
        # 일정시간 지난 후에 다시 생성하면 고정이 가능
        # 만약 같은에러가 계속 발생시
        # try 문으로 set_vm_ip_address() 메소드로 할당은 가능하다. (고정하는 순간 response 없이 무한 대기, timeout 10으로 설정)
        #
        # while True:
        #     try:
        #         time.sleep(20)
        #         dhcp_ip_address = ps.get_ip_address_type(get_vm_ip)
        #         if dhcp_ip_address is True:
        #             try:
        #                 time.sleep(20)
        #                 ps.set_vm_ip_address(get_vm_ip, config.DNS_ADDRESS, config.DNS_SUB_ADDRESS)
        #             except Exception as message:
        #                 print message
        #                 ps.get_ip_address_type(get_vm_ip)
        #                 continue
        #         else:
        #             try:
        #                 vmid = random_string(config.SALT, 8)
        #                 vm = GnVmMachines(vmid, name, tag, 'hyperv', start_vm['VMId'],
        #                                   internal_name,
        #                                   host_id, get_vm_ip, cpu, memory, hdd,
        #                                   os
        #                                   , os_ver, os_sub_ver, os_bit, team_code,
        #                                   author_id, datetime.datetime.now(),
        #                                   datetime.datetime.now(), None, ps.get_state_string(start_vm['State']))
        #
        #                 insert_monitor = GnMonitor(vmid, 'hyperv', 0.0000, 0.0000, 0.0000, 0.0000)
        #                 db_session.add(insert_monitor)
        #                 db_session.add(vm)
        #                 db_session.commit()
        #                 return jsonify(status=True, massage="create vm success")
        #
        #             except:
        #                 db_session.rollback()
        #                 return jsonify(status=False, massage="DB insert fail")
        #     except Exception as message:
        #         print message
        #         continue
        #     finally:
        #         print message


        # powershell service 쪽 추가해야할 스크립트 패스워드 관련
        # todo 1. windows server 2012 r2 는 패스워드를 영문, 숫자, 기호를 혼합하여 입력하도록 강제합니다.
        # todo 2. adminname은 원본 이미지의 user name이다. windows server2012는 디폴드 값이 Administrator 이다.
        #         server 에 맞춰서 Administrator 이라는 계정명으로 통일을 해야 될 것 같습니다.

        ps.set_password(get_vm_ip, password)

        # def change_vm_pwd2(adminname, password):
        #     ps = PowerShell("192.168.1.39", config.AGENT_PORT, config.AGENT_REST_URI)
        #     script = '$user=[adsi]"WinNT://$env:computerName/'+adminname+'";'
        #     script += '$user.setPassword("'+password+'"); '
        #     script += '$user:USERNAME | ConvertTo-Json'
        #     print str(ps.send(script))

        vmid = random_string(config.SALT, 8)
        vm = GnVmMachines(vmid, name, tag, 'hyperv', start_vm['VMId'],
                          internal_name,
                          host_id, get_vm_ip, cpu, memory, hdd,
                          os
                          , os_ver, os_sub_ver, os_bit, team_code,
                          author_id, datetime.datetime.now(),
                          datetime.datetime.now(), None, ps.get_state_string(start_vm['State']))

        insert_monitor = GnMonitor(vmid, 'hyperv', 0.0000, 0.0000, 0.0000, 0.0000)
        db_session.add(insert_monitor)
        db_session.add(vm)
        db_session.commit()
        return jsonify(status=True, massage="create vm success")


#  REST. VM 스냅샷 생성
#  hvm_snapshot 1. VM 정지 (Stop-VM)
#  hvm_snapshot 2. 스냅샷을 생성한다.
#  hvm_snapshot 3. 생성된 스냅샷 이미지 이름 변경 (2번에서 이름 변경이 안 될 경우)
#  hvm_snapshot 4. 생성된 스냅샷 이미지 이름 를 지정된 폴더에 옮긴다. (테스트 때에는 C:\images 로 한다.)
#  hvm_snapshot 5. 생성된 스냅샷의 정보를 데이터베이스에 저장한다.
def hvm_snapshot():

    # 지금은 internal_id 받아야한다
    #org_id = request.json['org_id'] #원본 이미지 아이디
    org_id = db_session.query(GnVmMachines).filter(GnVmMachines.id == request.json['ord_id']).first()

    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.id == org_id.host_id).first()
    image_pool = db_session.query(GnImagesPool).filter(GnImagesPool.host_id == org_id.host_id).first()

    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, config.AGENT_REST_URI)

    stop_vm = ps.stop_vm(org_id.internal_id) #원본 이미지 인스턴스 종료
    if stop_vm['State'] is 3:
        create_snap = ps.create_snap(org_id.internal_id, image_pool.image_path)
        #print create_snap
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
            #author_id = session['userName']
            author_id = request.json['userName']

            os_bit = base_image_info.os_bit
            team_code = request.json['team_code']
            #team_code = session['teamCode']

            insert_image_query = GnVmImages(random_string(config.SALT, 8), name, filename, type, subtype,
                                            icon, os, os_ver, os_subver, os_bit, team_code,
                                            author_id, datetime.datetime.now(), "running", "", "", org_id.host_id)
            db_session.add(insert_image_query)
            db_session.commit()

            start_vm = ps.start_vm(org_id.internal_id)
            if start_vm['State'] is 2:
                return jsonify(status=True, message="성공")
            else:
                return jsonify(status=False, message="실패")
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
    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, config.AGENT_REST_URI)

    type = request.json['type']
    #print vmid.internal_id
    #    vm = GnVmMachines.query.filter_by().first
    if type == "start":
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
    elif type == "reboot":
        restart = ps.restart_vm(vmid.internal_id)
        # resume 1. 가상머신을 재시작한다. (Restart-VM)
        if restart['State'] is 2:
            update = db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == restart['Id']).update(
                {"start_time": datetime.datetime.now(), "stop_time": datetime.datetime.now()})
            db_session.commit()
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

    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, config.AGENT_REST_URI)
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
    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, config.AGENT_REST_URI)
    # Powershell Script를 통해 VM 정보를 가져온다.
    vm = ps.get_vm_one(vmid)
    # todo get-vm. VM 정보를 DB에서 가져온다.
    return jsonify(vm=vm, message="", status=True)


# todo REST. VM 리스트 정보
def hvm_vm_list():
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.name == 'hyperv').first()
    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, config.AGENT_REST_URI)
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

    ps = PowerShell(host_machine.ip, host_machine.host_agent_port, config.AGENT_REST_URI)
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


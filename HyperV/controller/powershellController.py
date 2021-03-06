# -*- coding: utf-8 -*-
"""
Hyper-V를 컨트롤 할 PowerShell Script(서비스의 powershellSerivce에서 제공)를 실행하는 Rest 함수들을 정의한다.
각 Rest 함수들의 이름은 hvm_(Action을 대표하는 영단어 소문자)로 표기한다.
"""
import json

from HyperV.util.json_encoder import AlchemyEncoder
from HyperV.db.models import *
from HyperV.util.logger import logger

__author__ = 'jhjeon'

import datetime
import time
from flask import request, jsonify
from HyperV.service.powershellService import PowerShell
from HyperV.db.database import db_session
from HyperV.db.models import GnVmMachines, GnVmImages, GnMonitor, GnUsers, GnTeam, GnBackup, GnBackupHist

from HyperV.util.config import config
from HyperV.util.hash import random_string

# VM 생성 및 실행
def hvm_create(id, sql_session):
    vm_info = None
    team_name = None
    user_name = None
    host_port = config.AGENT_PORT
    try:
        vm_id = id
        vm_info =sql_session.query(GnVmMachines).filter(GnVmMachines.id == vm_id).first()

        if vm_info is not None:
            team_name = sql_session.query(GnTeam).filter(GnTeam.team_code == vm_info.team_code).one()
            user_name = sql_session.query(GnUsers).filter(GnUsers.user_id == vm_info.author_id).one()

        host_machine = sql_session.query(GnHostMachines).filter(GnHostMachines.id == vm_info.host_id).first()
        if host_machine.ip.find(':') >= 0:
            host_ip = host_machine.ip.split(':')[0]
            host_port = host_machine.ip.split(':')[1]
        else:
            host_ip = host_machine.ip

        #image_pool = sql_session.query(GnImagesPool).filter(GnImagesPool.host_id == host_id).first()
        ps = PowerShell(host_ip, host_port, config.AGENT_REST_URI)

        base_image_info = sql_session.query(GnVmImages).filter(GnVmImages.id == vm_info.image_id).first()

        source_path = "/base/"
        if base_image_info.sub_type == 'snap':
            source_path = "/snapshot/"

        base_image = base_image_info.filename
        os = base_image_info.os
        os_ver = base_image_info.os_ver
        os_sub_ver = base_image_info.os_subver
        os_bit = base_image_info.os_bit
        internal_name = base_image_info.os_ver + '_' + base_image_info.os_bit + '_' + vm_id

        SWITCHNAME = "out"
        print ('internal_name=%s, memory=%s, path=%s' %(internal_name, vm_info.memory, config.MANAGER_PATH))
        new_vm = ps.new_vm(Name=internal_name, MemoryStartupBytes=str(vm_info.memory), Path=config.MANAGER_PATH,
                           SwitchName=SWITCHNAME)

        if new_vm is not None:
            # 새 머신에서 추가적인 설정을 한다 (Set-VM)
            set_vm = ps.set_vm(VMId=new_vm['VMId'], ProcessorCount=str(vm_info.cpu), MemoryMaximumBytes=str(vm_info.memory))
            CONVERT_VHD_DESTINATIONPATH = config.LOCAL_PATH + "/instance/" + internal_name + ".vhdx"

            CONVERT_VHD_PATH = config.NAS_PATH + source_path + base_image  #원본이미지로부터

            convert_vhd = ps.convert_vhd(DestinationPath=CONVERT_VHD_DESTINATIONPATH, Path=CONVERT_VHD_PATH)
            add_vmharddiskdrive = ps.add_vmharddiskdrive(VMId=new_vm['VMId'], Path=CONVERT_VHD_DESTINATIONPATH)

            # hdd 확장
            if vm_info.disk > 21475000000 and base_image_info.sub_type == 'base':
                ps.resize_vhd(config.LOCAL_PATH + "/instance/" + internal_name + ".vhdx", vm_info.disk)

            start_vm = ps.start_vm(new_vm['VMId'])

            get_ip_count = 0

            time.sleep(5)
            get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])
            while len(get_vm_ip) <= 2:
                if get_ip_count >= 100:
                    error_hist = GnErrorHist(type=vm_info.type,action="Create",team_code=vm_info.team_code,
                                             author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name,
                                             cause='cannot get vm ip')
                    sql_session.add(error_hist)
                    vm_info.internal_id=new_vm['VMId']
                    vm_info.internal_name=internal_name
                    vm_info.status = "Error"
                    sql_session.commit()
                    return False
                time.sleep(5)
                get_vm_ip = ps.get_vm_ip_address(new_vm['VMId'])
                get_ip_count += 1

            # password setting without snapshot
            if base_image_info.sub_type != 'snap':
                set_pass_count = 0
                return_val = ps.set_password(get_vm_ip, vm_info.hyperv_pass)
                while len(return_val) <= 2:
                    if set_pass_count > 50:
                        error_hist = GnErrorHist(type=vm_info.type,action="Create",team_code=vm_info.team_code,
                                                 author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name,
                                                 cause='cannot set password')
                        sql_session.add(error_hist)
                        vm_info.internal_id=new_vm['VMId']
                        vm_info.internal_name=internal_name
                        vm_info.status = "Error"
                        sql_session.commit()
                        return False
                    time.sleep(5)
                    return_val = ps.set_password(get_vm_ip, vm_info.hyperv_pass)
                    set_pass_count += 1

            vm_info.internal_id=new_vm['VMId']
            vm_info.internal_name=internal_name
            vm_info.ip = get_vm_ip
            vm_info.os = os
            vm_info.os_ver = os_ver
            vm_info.os_sub_ver = os_sub_ver
            vm_info.os_bit = os_bit
            vm_info.create_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            vm_info.start_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            vm_info.status = ps.get_state_string(start_vm['State'])

            insert_monitor = GnMonitor(vm_id, 'hyperv', 0.0000, 0.0000, 0.0000, 0.0000)
            sql_session.add(insert_monitor)

            # for insert of GN_INSTANCE_STATUS table
            vm_size = sql_session.query(GnVmSize).filter(GnVmSize.id == vm_info.size_id).first()
            instance_status_price = None
            system_setting = sql_session.query(GnSystemSetting).first()
            if system_setting.billing_type == 'D':
                instance_status_price = vm_size.day_price
            elif system_setting.billing_type == 'H':
                instance_status_price = vm_size.hour_price
            else:
                logger.error('invalid price_type : system_setting.billing_type %s' % system_setting.billing_type)

            now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            insert_instance_status = GnInstanceStatus(vm_id=vm_info.id,vm_name=vm_info.name, create_time=now_time
                                                      , delete_time=None, author_id=vm_info.author_id, author_name=user_name.user_name
                                                      , team_code=vm_info.team_code, team_name=team_name.team_name
                                                      , price=instance_status_price,price_type=system_setting.billing_type
                                                      , cpu=vm_info.cpu, memory=vm_info.memory,disk=vm_info.disk)

            sql_session.add(insert_instance_status)

            sql_session.commit()
            return True
    except Exception as e:
        print(e.message)
        if vm_info is None:
            vm_info =sql_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()
        error_hist = GnErrorHist(type=vm_info.type,action="Create",team_code=vm_info.team_code,
                                 author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name,
                                 cause=e.message)
        sql_session.add(error_hist)
        vm_info.status = "Error"
        sql_session.commit()
        return False


def hvm_snapshot():
    host_port = config.AGENT_PORT
    vm_info = db_session.query(GnVmImages).filter(GnVmImages.id == request.json['vm_id']).first()
    org_id = db_session.query(GnVmMachines).filter(GnVmMachines.id == request.json['ord_id']).first()
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.id == org_id.host_id).first()
    # image_pool = db_session.query(GnImagesPool).filter(GnImagesPool.host_id == org_id.host_id).first()
    if host_machine.ip.find(':') >= 0:
        host_ip = host_machine.ip.split(':')[0]
        host_port = host_machine.ip.split(':')[1]
    else:
        host_ip = host_machine.ip

    try:
        ps = PowerShell(host_ip, host_port, config.AGENT_REST_URI)
        create_snap = ps.create_snap(org_id.internal_id, config.MANAGER_PATH, config.NAS_PATH)
        if create_snap['Name'] is not None:
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
                logger.debug('snapshot create Error = %s' % start_vm)
                error_hist = GnErrorHist(type=vm_info.type,action="Snap-create",team_code=vm_info.team_code,
                                         author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name,
                                         cause=start_vm)
                db_session.add(error_hist)
                vm_info.status="Error"
                db_session.commit()
                return jsonify(status=False)
    except Exception as e:
        logger.debug('snapshot create Error = %s' % e.message)
        error_hist = GnErrorHist(type=vm_info.type,action="Snap-create",team_code=vm_info.team_code,
                                 author_id=vm_info.author_id, vm_id=vm_info.id, vm_name=vm_info.name,
                                 cause=e.message)
        db_session.add(error_hist)
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
    host_port=config.AGENT_PORT
    vmid = db_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.id == vmid.host_id).first()

    if host_machine.ip.find(':') >= 0:
        host_ip = host_machine.ip.split(':')[0]
        host_port = host_machine.ip.split(':')[1]
    else:
        host_ip = host_machine.ip

    ps = PowerShell(host_ip, host_port, config.AGENT_REST_URI)

    type = request.json['type']
    #print vmid.internal_id
    #    vm = GnVmMachines.query.filter_by().first
    start_vm = ''
    if type == "Resume":
        try:
            # VM 시작
            # 1. 가상머신을 시작한다. (Start-VM)
            start_vm = ps.start_vm(vmid.internal_id)
            # start_vm
            # print id
            # 2. 가상머신 상태를 체크한다. (Get-VM)

            if start_vm['State'] is 2:
                db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == start_vm['Id'])\
                        .update({"status": "Running", "start_time": datetime.datetime.now().strftime('%Y%m%d%H%M%S')})
                db_session.commit()
                # print start_vm['Id']
                return jsonify(status=True, message="success VM starting")
            else:
                error_hist = GnErrorHist(type=vmid.type,action=type,team_code=vmid.team_code,author_id=vmid.author_id,
                                         vm_id=vmid.id, vm_name=vmid.name, cause=start_vm)
                db_session.add(error_hist)
                db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == start_vm['Id'])\
                        .update({"status": "error"})
                db_session.commit()
                return jsonify(status=False, message="정상적인 결과가 아닙니다.")
        except Exception as err:
            logger.error('hyperv status change error = %s' % err.message)
            error_hist = GnErrorHist(type=vmid.type,action=type,team_code=vmid.team_code,author_id=vmid.author_id,
                                     vm_id=vmid.id, vm_name=vmid.name, cause=start_vm)
            db_session.add(error_hist)
            db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == start_vm['Id']) \
                .update({"status": "error"})
            db_session.commit()
            return jsonify(status=False, message="정상적인 결과가 아닙니다.")

    elif type == "stop" or type == "shutdown" :
        stop = ''
        try:
            # stop 1. 가상머신을 정지한다. (Stop-VM)
            stop = ps.stop_vm(vmid.internal_id)
            # stop 2. 가상머신 상태를 체크한다. (Get-VM)
            if stop['State'] is 3:
                # stop 3. 변경된 가상머신 상태를 DB에 업데이트한다.
                db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == stop['Id'])\
                        .update({"status": "Stop", "stop_time": datetime.datetime.now().strftime('%Y%m%d%H%M%S')})
                db_session.commit()
                return jsonify(status=True, message="VM Stop")
            else:
                logger.error('hyperv status change error(%s) = %s' % (type, stop))
                error_hist = GnErrorHist(type=vmid.type,action=type,team_code=vmid.team_code,author_id=vmid.author_id,
                                         vm_id=vmid.id, vm_name=vmid.name, cause=stop)
                db_session.add(error_hist)
                db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == stop['Id']) \
                        .update({"status": "error"})
                db_session.commit()
                return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
                # return jsonify(status=False, message="상태 미완성")
        except Exception as err:
            logger.error(err)
            error_hist = GnErrorHist(type=vmid.type,action=type,team_code=vmid.team_code,author_id=vmid.author_id,
                                     vm_id=vmid.id, vm_name=vmid.name, cause=err.message)
            db_session.add(error_hist)
            db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == stop['Id']) \
                .update({"status": "error"})
            db_session.commit()
            return jsonify(status=False, message="정상적인 결과가 아닙니다.")

    elif type == "Reboot":
        restart = ''
        try:
            restart = ps.restart_vm(vmid.internal_id)
            # resume 1. 가상머신을 재시작한다. (Restart-VM)
            if restart['State'] is 2:
                db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == restart['Id'])\
                    .update({"start_time": datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
                             "stop_time": datetime.datetime.now().strftime('%Y%m%d%H%M%S')})
                db_session.commit()
                return jsonify(status=True, message="VM Restart")
            else:
                logger.debug('restart error = %s' % restart)
                error_hist = GnErrorHist(type=vmid.type,action=type,team_code=vmid.team_code,author_id=vmid.author_id,
                                         vm_id=vmid.id, vm_name=vmid.name, cause=restart)
                db_session.add(error_hist)
                db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == restart['Id']) \
                    .update({"status": "error"})
                db_session.commit()
                return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
        except Exception as err:
            error_hist = GnErrorHist(type=vmid.type,action=type,team_code=vmid.team_code,author_id=vmid.author_id,
                                     vm_id=vmid.id, vm_name=vmid.name, cause=err.message)
            db_session.add(error_hist)
            logger.error(err)
            db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == restart['Id']) \
                .update({"status": "error"})
            db_session.commit()
            return jsonify(status=False, message="정상적인 결과가 아닙니다.")

    elif type == "Suspend":
        suspend = ''
        try:
            suspend = ps.suspend_vm(vmid.internal_id)
            if suspend['State'] is 9:
                db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == suspend['Id'])\
                    .update({"status": "Suspend"})
                db_session.commit()
                return jsonify(status=True, message="가상머신이 일시정지되었습니다.")
            else:
                error_hist = GnErrorHist(type=vmid.type,action=type,team_code=vmid.team_code,author_id=vmid.author_id,
                                         vm_id=vmid.id, vm_name=vmid.name, cause=suspend)
                db_session.add(error_hist)
                db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == suspend['Id']) \
                    .update({"status": "error"})
                db_session.commit()
                return jsonify(status=False, message="정상적인 결과값이 아닙니다.")
        except Exception as err:
            error_hist = GnErrorHist(type=vmid.type,action=type,team_code=vmid.team_code,author_id=vmid.author_id,
                                     vm_id=vmid.id, vm_name=vmid.name, cause=suspend)
            db_session.add(error_hist)
            logger.error(err)
            db_session.query(GnVmMachines).filter(GnVmMachines.internal_id == suspend['Id']) \
                .update({"status": "error"})
            db_session.commit()
            return jsonify(status=False, message="정상적인 결과가 아닙니다.")

    elif type == "powerdown":
        return jsonify(status=False, message="상태 미완성")
    else:
        logger.debug('undefined status = %s' % type)
        return jsonify(status=False, message="정상적인 상태 정보를 받지 못했습니다.")


# REST. VM 삭제
def hvm_delete(id):
    host_port=config.AGENT_PORT
    vmid = db_session.query(GnVmMachines).filter(GnVmMachines.id == id).first()
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.id == vmid.host_id).first()
    if host_machine.ip.find(':') >= 0:
        host_ip = host_machine.ip.split(':')[0]
        host_port = host_machine.ip.split(':')[1]
    else:
        host_ip = host_machine.ip

    #image_pool = db_session.query(GnImagesPool).filter(GnImagesPool.host_id == vmid.host_id).first()

    try:
        ps = PowerShell(host_ip, host_port, config.AGENT_REST_URI)
        vm_info =ps.get_vm_one(vmid.internal_id)
        #  REST hvm_delete 1. Powershell Script를 통해 VM을 정지한다.
        stop_vm = ps.stop_vm(vmid.internal_id)
        if stop_vm['State'] is 3:
            delete_vm = ps.delete_vm(vmid.internal_id, config.LOCAL_PATH, config.MANAGER_PATH)
            update_vm_machines = db_session.query(GnVmMachines).filter(GnVmMachines.id == id).delete()
            update_instance_status = db_session.query(GnInstanceStatus).filter(GnInstanceStatus.vm_id == vmid.id) \
                .update({"delete_time": datetime.datetime.now().strftime('%Y%m%d%H%M%S')})

            backup_hist_list = db_session.query(GnBackupHist).filter(GnBackupHist.vm_id==id).all()
            filename = ''
            for hist in backup_hist_list:
                ps.delete_backup(hist.filename, config.BACKUP_PATH)

            db_session.query(GnBackupHist).filter(GnBackupHist.vm_id == id).delete()
            db_session.query(GnBackup).filter(GnBackup.vm_id == id).delete()

            db_session.commit()
            # REST hvm_delete 2. VM을 삭제한다.
            # todo REST hvm_delete 3. 삭제된 VM DB 데이터를 삭제 상태로 업데이트한다.
            return jsonify(message="Remove success", status=True)
        else:
            logger.debug("delete vm error: %s" % stop_vm)
            error_hist = GnErrorHist(type=vmid.type,action="Delete",team_code=vmid.team_code,author_id=vmid.author_id,
                                     vm_id=vmid.id, vm_name=vmid.name, cause=stop_vm)
            db_session.add(error_hist)
            db_session.commit()
            return jsonify(message="Remove failure", status=False)
    except Exception as e:
        logger.debug("delete vm error: %s" % e.message)
        error_hist = GnErrorHist(type=vmid.type,action="Delete",team_code=vmid.team_code,author_id=vmid.author_id,
                                 vm_id=vmid.id, vm_name=vmid.name, cause=e.message)
        db_session.add(error_hist)
        db_session.commit()
        return jsonify(message="Remove failure", status=False)


# todo REST. VM 정보
def hvm_vm(vmid):
    host_port=config.AGENT_PORT
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.name == 'hyperv').first()
    if host_machine.ip.find(':') >= 0:
        host_ip = host_machine.ip.split(':')[0]
        host_port = host_machine.ip.split(':')[1]
    else:
        host_ip = host_machine.ip

    ps = PowerShell(host_ip, host_port, config.AGENT_REST_URI)
    # Powershell Script를 통해 VM 정보를 가져온다.
    vm = ps.get_vm_one(vmid)
    # todo get-vm. VM 정보를 DB에서 가져온다.
    return jsonify(vm=vm, message="", status=True)


# todo REST. VM 리스트 정보
def hvm_vm_list():
    host_port=config.AGENT_PORT
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.name == 'hyperv').first()
    if host_machine.ip.find(':') >= 0:
        host_ip = host_machine.ip.split(':')[0]
        host_port = host_machine.ip.split(':')[1]
    else:
        host_ip = host_machine.ip

    ps = PowerShell(host_ip, host_port, config.AGENT_REST_URI)
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
                                    author_id, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    db_session.add(insert_image_query)
    db_session.commit()

    return jsonify(status=True, message="success")


# tdo REST. VM 이미지 수정
def hvm_modify_image(id):
    # null 값이 들어오면 수정 하지 않는 기능으로 구현 .....
    # db값은 frontend 에서 수정함.....
    return jsonify(status=False, message="미구현")


# REST. VM 이미지 삭제 (snapshot)
# 이미지를 백업 폴더로 옮긴다
# 이미지 따로 관리
def hvm_delete_image(id):
    host_port=config.AGENT_PORT
    vhd_Name = db_session.query(GnVmImages).filter(GnVmImages.id == id).first()
    #image_pool = db_session.query(GnImagesPool).filter(GnImagesPool.host_id == vhd_Name.host_id).first()
    host_machine = db_session.query(GnHostMachines).filter(GnHostMachines.id == vhd_Name.host_id).first()
    if host_machine.ip.find(':') >= 0:
        host_ip = host_machine.ip.split(':')[0]
        host_port = host_machine.ip.split(':')[1]
    else:
        host_ip = host_machine.ip

    ps = PowerShell(host_ip, host_port, config.AGENT_REST_URI)
    image_delete = ps.delete_vm_Image(vhd_Name.filename, config.NAS_PATH)

    json_obj = json.dumps(image_delete)
    json_size = len(json_obj)
    if json_size <= 2: #json 크기는 '{}' 포함
        #delete_vm = db_session.query(GnVmImages).filter(GnVmImages.id == id).update({"status": "Removed"})
        delete_vm = db_session.query(GnVmImages).filter(GnVmImages.id == id).delete()
        db_session.commit()
        #update 완료시 리턴값은 1
        if delete_vm == 1:
            return jsonify(status=True, message="image delete complete")
        else:
            logger.debug('delete hyperv images error')
            return jsonify(status=False, message="DB update fail")
    else:
        logger.debug('delete hyperv images error = %s' % json_obj)
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
    host_port=config.AGENT_PORT
    vm_info = sql_session.query(GnVmMachines).filter(GnVmMachines.type == 'hyperv').filter(GnVmMachines.status == 'Running').all()
    for seq in vm_info:
        host = sql_session.query(GnHostMachines).filter(GnHostMachines.id == seq.host_id).first()
        if host.ip.find(':') >= 0:
            host_ip = host.ip.split(':')[0]
            host_port = host.ip.split(':')[1]
        else:
            host_ip = host.ip

        ps = PowerShell(host_ip, host_port, config.AGENT_REST_URI)

        script = 'Get-VM -id '+seq.internal_id+' | Select-Object -Property id, cpuusage, memoryassigned | ConvertTo-Json '
        monitor = ps.send(script)

        script = 'Get-VHD -VMId ' +seq.internal_id+' | Select-Object -Property Filesize, Size | ConvertTo-Json;'
        hdd_usage = ps.send(script)
        #hdd = float(hdd_usage['FileSize'])/float(hdd_usage['Size'])
        hdd = float(hdd_usage['FileSize'])

        mem = float(monitor['MemoryAssigned'])
        cpu = round(float(monitor['CPUUsage'])*float((host.cpu/seq.cpu)), 4)

        script = '$vm = Get-vm -id '+ seq.internal_id+';'
        script += '$ip = Get-VMNetworkAdapter -VM $vm | Select-Object -Property IPAddresses;'
        script += '$ip.IPAddresses.GetValue(0) | ConvertTo-Json ;'
        ip = ps.send(script)

        try:
            monitor_insert = GnMonitorHist(seq.id, "hyperv", datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
                                           cpu, mem, round(hdd, 4), 0.0000)
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
            print 'success monitor'
        except Exception as message:
            print message.message
            sql_session.rollback()



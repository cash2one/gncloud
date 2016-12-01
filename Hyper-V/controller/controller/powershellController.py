# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import request, jsonify
from service.powershellService import PowerShell


def manual():
    script = request.args.get('script')
    ps = PowerShell('60.196.149.135', '8180', 'powershell/execute')

    #return ps.send(script)
    return jsonify(result=ps.send(script))


def hvm_state(vm_name, status):
    # 스냅샷 상태 snap
    # 시작 start
    # 정지 stop
    # 재시작 resume
    # 삭제 delete
    ps = PowerShell('60.196.149.135', '8180', 'powershell/execute')

    if status == "start":
        result = ps.start_vm(vm_name)
        if result['State'] is 2:
            return jsonify(status=True, message="가상머신이 정상적으로 실행되었습니다.")
        elif result['State'] is not 2:
            return jsonify(status=False, message="가상머신이 실행되지 않았습니다.")
        else:
            return jsonify(status=False, message="정상적인 결과가 아닙니다.")

    else:
        return ""

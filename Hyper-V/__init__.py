# -*- coding: utf-8 -*-
import threading

__author__ = 'jhjeon'

from flask import Flask, redirect, url_for
from datetime import timedelta

from controller.powershellController import *
from util.config import config

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)


def monitor_thread():
    while True:
        time.sleep(180)
        vm_monitor()

thread = threading.Thread(name='monitor_thread', target=monitor_thread)
thread.setDaemon(True)
thread.start()

# PowerShell Script Manual 실행: (Script) | ConvertTo-Json
app.add_url_rule("/manual", view_func=manual, methods=['GET'])
# --- VM 함수 --- #
# VM 생성 및 실행
app.add_url_rule("/vm/machine", view_func=hvm_create, methods=['POST'])
# VM 스냅샷 생성
app.add_url_rule("/vm/machine/snapshots", view_func=hvm_snapshot, methods=['POST'])
# VM 상태변경
app.add_url_rule("/vm/machines/<id>", view_func=hvm_state, methods=['PUT'])
# VM 삭제
app.add_url_rule("/vm/machines/<id>", view_func=hvm_delete, methods=['DELETE'])
# VM 정보
app.add_url_rule("/vm/machines/<vmid>", view_func=hvm_vm, methods=['GET'])
# VM 리스트 정보
app.add_url_rule("/vm/machines", view_func=hvm_vm_list, methods=['GET'])
# --- VM 이미지 함수 --- #
# VM 이미지 생성 및 업로드
app.add_url_rule("/vm/images", view_func=hvm_new_image, methods=['POST'])
# VM 이미지 수정
app.add_url_rule("/vm/images/<id>", view_func=hvm_modify_image, methods=['PUT'])
# VM 이미지 삭제
app.add_url_rule("/vm/images/<id>", view_func=hvm_delete_image, methods=['DELETE'])
# VM 이미지 리스트
app.add_url_rule("/vm/images/<type>", view_func=hvm_image_list, methods=['GET'])
# VM 이미지 정보
app.add_url_rule("/vm/images/<type>/<id>", view_func=hvm_image, methods=['GET'])

# @app.route('/test', methods=['POST'])
# def test():
#     request.json['type']
#     return jsonify(status=True, message="success")

# @app.route("/vm/machines/<id>", methods=['PUT'])
# def test1(id):
#     id =id
#     type=request.json['type']
#     team_code = session['teamCode']
#     hvm_state(id, type, team_code)
#     return jsonify(status= True, message="success")


# Controller 상태 확인
@app.route("/service/isAlive")
def isAlive():
    return jsonify(status=True, message='서비스 정상 작동')


# 페이지 리스트
@app.route("/")
def index():
    return redirect(url_for("isAlive"))


if __name__ == '__main__':
    app.config['DEBUG'] = False
    app.run(host=config.CONTROLLER_HOST, port=config.CONTROLLER_PORT)

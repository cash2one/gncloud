# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import Flask, redirect, url_for, jsonify
from controller.powershellController import *
from util.config import config


app = Flask(__name__)

# PowerShell Script Manual 실행: (Script) | ConvertTo-Json
app.add_url_rule("/manual", view_func=manual, methods=['GET'])
# --- VM 함수 --- #
# VM 생성 및 실행
app.add_url_rule("/vm/machine", view_func=hvm_create, methods=['POST'])
# VM 스냅샷 생성
app.add_url_rule("/vm/machine/snapshot", view_func=hvm_snapshot, methods=['POST'])
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

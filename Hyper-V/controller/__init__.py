# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import Flask, redirect, send_file
from controller.powershellController import *
from util.config import config


app = Flask(__name__)

# PowerShell Script Manual 실행: (Script) | ConvertTo-Json
app.add_url_rule("/manual", view_func=manual, methods=['GET'])
# VM 생성 및 실행
app.add_url_rule("/vm/create", view_func=hvm_create, methods=['POST'])
# VM 스냅샷 생성
app.add_url_rule("/vm/<id>/snap", view_func=hvm_snap, methods=['POST'])
# VM 상태변경
app.add_url_rule("/vm/<id>/status", view_func=hvm_state, methods=['POST'])
# VM 정보
app.add_url_rule("/vm/<vmid>", view_func=hvm_vm, methods=['GET'])
# VM 리스트 정보
app.add_url_rule("/vm", view_func=hvm_vm_list, methods=['GET'])


# Controller 상태 확인
@app.route("/service/isAlive")
def isAlive():
    return jsonify(status=True, message='서비스 정상 작동')


# 페이지 리스트
@app.route("/")
def index():
    return send_file("static/html/index.html")


@app.route("/main")
def main():
    return send_file("static/html/main.html")


@app.route("/guestCreate")
def guest_create():
    return send_file("static/html/guestCreate.html")


@app.route("/guestList")
def guest_list():
    return send_file("static/html/guestList.html")


@app.route("/guestLogin")
def guest_login():
    return send_file("static/html/guestLogin.html")


@app.route("/guestRunList")
def guest_run_list():
    return send_file("static/html/guestRunList.html")


@app.route("/guestSnapList")
def guest_snap_list():
    return send_file("static/html/guestSnapList.html")


if __name__ == '__main__':
    app.config['DEBUG'] = False
    app.run(host=config.CONTROLLER_HOST, port=config.CONTROLLER_PORT)

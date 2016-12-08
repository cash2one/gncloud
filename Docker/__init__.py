# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import Flask, redirect, url_for, jsonify
from controller.dockerController import *
from util.config import config


app = Flask(__name__)

# --- VM 함수 --- #
# Container 생성 및 실행
app.add_url_rule("/container/services", view_func=doc_create, methods=['POST'])
# Container 상태변경
app.add_url_rule("/container/services/<id>", view_func=doc_state, methods=['PUT'])
# Container 삭제
app.add_url_rule("/container/services/<id>", view_func=doc_delete, methods=['DELETE'])
# Container 리스트
app.add_url_rule("/container/services", view_func=doc_vm_list, methods=['GET'])
# Container 이미지 생성 및 업로드
app.add_url_rule("/container/images", view_func=doc_new_image, methods=['POST'])
# Container 이미지 수정
app.add_url_rule("/container/images/<id>", view_func=doc_modify_image, methods=['PUT'])
# Container 이미지 삭제
app.add_url_rule("/container/images/<id>", view_func=doc_delete_image, methods=['DELETE'])
# Container 이미지 리스트
app.add_url_rule("/container/images", view_func=doc_image_list, methods=['GET'])


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

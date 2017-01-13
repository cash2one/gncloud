# -*- coding: utf-8 -*-
__author__ = 'jhjeon'
import traceback
from datetime import timedelta
from flask import Flask, redirect, url_for
from apscheduler.scheduler import Scheduler
from util.config import config
from util.logger import logger
from util.json_encoder import AlchemyEncoder
from controller.dockerController import *
from db.database import db_session
from service.monitorService import service_monitoring

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# --- VM 함수 --- #
# Docker Service 생성 및 실행
# create_vm
app.add_url_rule("/vm/machine", view_func=doc_create, methods=['POST'])
# Docker Service 상태변경
# change_status
# app.add_url_rule("/container/services/<id>", view_func=doc_state, methods=['PUT'])
app.add_url_rule("/vm/machines/<id>", view_func=doc_state, methods=['PUT'])
# Docker Service 스냅샷 저장
app.add_url_rule('/vm/machine/snapshots', view_func=doc_snap, methods=['POST'])
# Docker Service 삭제
# delete_vm
app.add_url_rule("/vm/machines/<id>", view_func=doc_delete, methods=['DELETE'])
# Docker Service 리스트
app.add_url_rule("/vm/machines", view_func=doc_vm_list, methods=['GET'])
# Docker 이미지 생성 및 업로드
app.add_url_rule("/vm/images", view_func=doc_new_image, methods=['POST'])
# Docker 이미지 수정
# app.add_url_rule("/container/images/<id>", view_func=doc_modify_image, methods=['PUT'])
# Docker 이미지 삭제
app.add_url_rule("/vm/images/<id>", view_func=doc_delete_image, methods=['DELETE'])
# Docker 이미지 리스트
app.add_url_rule("/vm/images", view_func=doc_image_list, methods=['GET'])
# Docker 이미지 세부정보 입력
app.add_url_rule("/vm/images/detail/<image_id>", view_func=doc_new_image_detail, methods=['POST'])
# Docker 이미지 세부정보 수정
app.add_url_rule("/vm/images/detail/<image_id>/<id>", view_func=doc_update_image_detail, methods=['PUT'])
# Docker 이미지 세부정보 삭제
app.add_url_rule("/vm/images/detail/<image_id>/<id>", view_func=doc_delete_image_detail, methods=['DELETE'])


# Controller 상태 확인
@app.route("/service/isAlive")
def is_alive():
    logger.debug("%s Connection Check" % "/service/isAlive")
    return jsonify(status=True, message='서비스 정상 작동')


# 페이지 리스트
@app.route("/")
def index():
    logger.debug("%s Connection Check" % "/service/isAlive")
    return redirect(url_for("is_alive"))


@app.route('/monitor', methods=['GET'])
def cronMnitor():
    service_monitoring(db_session)
    return jsonify(status=True, message="success")


def interval_status_update():
    service_monitoring(db_session)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.errorhandler(500)
def internal_error(error):
    print(traceback.format_exc())
    return jsonify(status=False, message="서버에 에러가 발생했습니다. 관리자에게 문의해주세요")


if __name__ == '__main__':
    # cron = Scheduler(daemon=True)
    # cron.add_interval_job(interval_status_update, seconds=180)
    # cron.start()
    app.config['DEBUG'] = False
    app.run(host=config.CONTROLLER_HOST, port=config.CONTROLLER_PORT)

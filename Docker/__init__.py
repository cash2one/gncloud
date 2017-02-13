# -*- coding: utf-8 -*-
__author__ = 'jhjeon'
import traceback

from datetime import timedelta
from flask import Flask, redirect, url_for, session, make_response

from Docker.controller.dockerController import *
from Docker.db.database import db_session
from Docker.service.monitorService import service_monitoring
from Docker.util.config import config
from Docker.util.json_encoder import AlchemyEncoder
from Docker.util.logger import logger

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


### cron job start ###

#@timer(seconds=60)
def monitor():
    service_monitoring(db_session)

### cron job end ###


# --- VM 함수 --- #
# Docker Service 생성 및 실행
# create_vm
#app.add_url_rule("/vm/machine", view_func=doc_create, methods=['POST'])
@app.route('/vm/machine', methods=['POST'])
def create_vm():
    team_code = session['teamCode']
    user_id = session['userId']
    id = request.json['id']
    return doc_create(id,db_session)

# Docker Service 상태변경
# change_status
# app.add_url_rule("/container/services/<id>", view_func=doc_state, methods=['PUT'])
app.add_url_rule("/vm/machines/<id>", view_func=doc_state, methods=['PUT'])
# Docker Service 스냅샷 저장
app.add_url_rule('/vm/machine/snapshots', view_func=doc_snap, methods=['POST'])
# Docker Service 삭제
# delete_vm
# app.add_url_rule("/vm/machines/<id>", view_func=doc_delete, methods=['DELETE'])
@app.route('/vm/machines/<id>', methods=['DELETE'])
def delete_vm(id):
    doc_delete(id,db_session)
    return jsonify(status=True)

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


@app.before_request
def before_request():
    if 'userId' not in session and request.path != '/monitor' and request.path != '/service/isAlive' \
            and request.path != '/' and request.path != '/vm/logfilelist' and request.path!='/vm/logfilecontents':
        return make_response(jsonify(status=False),401)


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
def cronMonitor():
    service_monitoring(db_session)
    return jsonify(status=True, message="success")


@app.route('/vm/logfilelist', methods=['GET'])
def get_logfiles():
    vm_id = request.args.get("vm_id")
    #vm_id='9d4c3e58'
    result = get_container_logfiles(vm_id)
    return result


@app.route('/vm/logfilecontents', methods=['GET'])
def get_logfile_contents():
    log_id = request.args.get("vm_id")
    filename = request.args.get("filename")
    worker_name = request.args.get("worker_name")
    # log_id = '9d4c3e58'
    # filename = 'catalina.2017-02-10.log'
    # worker_name = 'worker-2'
    return get_contents(log_id, filename, worker_name)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.errorhandler(500)
def internal_error(error):
    print(traceback.format_exc())
    return jsonify(status=False, message="서버에 에러가 발생했습니다. 관리자에게 문의해주세요")

if __name__ == '__main__':
    #app.run(host=config.CONTROLLER_HOST, port=int(config.CONTROLLER_PORT))
    #app.run(host='192.168.1.101', port=int(config.CONTROLLER_PORT))
    app.run(port=int(config.CONTROLLER_PORT))
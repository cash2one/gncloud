# -*- coding: utf-8 -*-
import traceback

from apscheduler.scheduler import Scheduler
from flask import Flask, jsonify, request, make_response,session
from datetime import timedelta
from gevent.pywsgi import WSGIServer
import datetime

from db.database import db_session
from service.service import server_create, server_change_status, server_monitor \
    , add_user_sshkey, delete_user_sshkey, list_user_sshkey, server_delete, server_create_snapshot \
    , server_image_delete, getsshkey_info
from util.json_encoder import AlchemyEncoder
from util.logger import logger
from kvm.db.models import GnVmMachines, GnHostMachines, GnVmImages, GnMonitor, GnMonitorHist, GnSshKeys, GnId

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


### cron job start ###

def job_function():
    server_monitor(db_session)

### cron job end ###

#####common function start#####


####login check start####

@app.before_request
def before_request():
    if ('userId' not in session) \
            and request.endpoint != 'guestLogout' \
            and request.endpoint != 'account':
        return make_response(jsonify(status=False),401)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.errorhandler(500)
def internal_error(error):
    print(traceback.format_exc())
    return jsonify(status=False, message="서버에 에러가 발생했습니다. 관리자에게 문의해주세")

#####common function end#####

#### rest start ####

@app.route('/vm/machine', methods=['POST'])
def create_vm():
    team_code = session['teamCode']
    user_id = session['userId']
    name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')#request.json['name']
    cpu = request.json['cpu']
    memory = request.json['memory']
    disk = 10#request.json['hdd']
    image_id = request.json['id']
    sshkeys = request.json['sshkeys']
    tag =request.json['tag']
    result = server_create(name ,cpu, memory, disk, image_id, team_code, user_id, sshkeys, tag)
    return jsonify(status=result["status"], message=result["message"])


@app.route('/vm/machines/<id>', methods=['PUT'])
def change_status(id):
    status = request.json['type']
    server_change_status(id, status, db_session)
    return jsonify(status=True, message="success")


@app.route('/vm/machines/<id>', methods=['DELETE'])
def delete_vm(id):
    server_delete(id, db_session)
    return jsonify(status=True, message="success")


@app.route('/vm/machine/snapshots', methods=['POST'])
def create_snap():
    user_id = session['userId'] # session
    team_code = session['teamCode']  # session
    ord_id = request.json['ord_id']
    name = request.json['name']
    server_create_snapshot(ord_id, name, user_id, team_code)
    return jsonify(status=True, message="success")


@app.route('/vm/images/<id>', methods=['DELETE'])
def delete_vm_image(id):
    server_image_delete(id, db_session)
    return jsonify(status=True, message="success")


@app.route('/account/keys', methods=['POST'])
def add_sshKey():
    team_code = session['teamCode']
    name = request.json['name']
    add_user_sshkey(team_code, name)
    return jsonify(status=True, message="success")


@app.route('/account/keys/<id>', methods=['DELETE'])
def delete_sshKey(id):
    team_code = session['teamCode']
    delete_user_sshkey(id)
    return jsonify(status=True, message="success")


@app.route('/account/keys', methods=['GET'])
def list_sshKey():
    team_code = session['teamCode']
    return jsonify(status=True, message="success", list=list_user_sshkey(team_code, db_session))


@app.route('/user/sshkey/download/<id>', methods=['GET'])
def download_sshKey(id):
    headers = {"Content-Disposition": "attachment; filename=sshkey"}
    sshkey_path = getsshkey_info(id)
    with open(sshkey_path.path, 'r') as f:
        body = f.read()
    return make_response((body, headers))

#### rest end ####

#### error handler start####

# @app.errorhandler(Exception)
# def internal_error(error):
#     app.logger.error(error)
#     logger.error('%s -- 500 ERROR', error)
#     return jsonify(status=False, message="서버에 에러가 발생했습니다. 관리자에게 문의해주세")


#### error handler end####



if __name__ == '__main__':
    # 로그 설정
    cron = Scheduler(daemon=True)
    cron.add_interval_job(job_function, seconds=60) #minites=1)
    cron.start()
    #app.run(debug=True)
    http_server = WSGIServer(('', 8081), app)
    http_server.serve_forever()

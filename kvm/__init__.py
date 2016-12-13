# -*- coding: utf-8 -*-

import atexit
import logging
from flask import Flask, send_file, jsonify, request, make_response
from db.database import db_session
from service.service import server_create, server_change_status, server_image_list, server_monitor \
    , add_user_sshkey, delete_user_sshkey, list_user_sshkey, server_delete, server_create_snapshot \
    , server_image_delete, getsshkey_info
from datetime import timedelta
from kvm.util.json_encoder import AlchemyEncoder
from kvm.util.logger import logger
from apscheduler.scheduler import Scheduler
from gevent.wsgi import WSGIServer
from kvm.db.models import GnVmMachines, GnHostMachines, GnVmImages, GnMonitor, GnMonitorHist, GnSshKeys, GnId


app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder


### cron job start ###

def job_function():
    server_monitor()

### cron job end ###

#### rest start ####


@app.route('/vm/machine', methods=['POST'])
def create_vm():
    team_code = "1"  # session
    user_id = "2"  # session
    name = request.json['name']
    cpu = request.json['cpu']
    memory = request.json['memory']
    disk = request.json['hdd']
    image_id = request.json['id']
    sshkeys = request.json['sshkeys']
    server_create(name, cpu, memory, disk, image_id, team_code, user_id, sshkeys)
    return jsonify(status=True, message="sucess")


@app.route('/vm/machines/<id>', methods=['PUT'])
def change_status(id):
    status = request.json['type']
    server_change_status(id, status)
    return jsonify(status=True, message="success")


@app.route('/vm/machines/<id>', methods=['DELETE'])
def delete_vm(id):
    server_delete(id)
    return jsonify(status=True, message="success")


@app.route('/vm/machine/snapshots', methods=['POST'])
def create_snap():
    ord_id = request.json['ord_id']
    name = request.json['name']
    user_id = "yhkwak"  # session
    team_code = "1"  # session
    server_create_snapshot(ord_id, name, user_id, team_code)
    return jsonify(status=True, message="success")


@app.route('/vm/images/<sub_type>', methods=['GET'])
def list_volume(sub_type):
    return jsonify(status=True, message="success", list=server_image_list(sub_type))


@app.route('/vm/images/<id>', methods=['DELETE'])
def delete_vm_image(id):
    server_image_delete(id)
    return jsonify(status=True, message="success")


@app.route('/account/keys', methods=['POST'])
def add_sshKey():
    team_code = 1
    name = request.json['name']
    add_user_sshkey(team_code, name)
    return jsonify(status=True, message="success")


@app.route('/account/keys/<id>', methods=['DELETE'])
def delete_sshKey(id):
    team_code = 1
    delete_user_sshkey(id)
    return jsonify(status=True, message="success")


@app.route('/account/keys', methods=['GET'])
def list_sshKey():
    team_code = 1
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
# def all_exception_handler(error):
#     logger.info('%s -- 500 ERROR', error)
#     return jsonify(status=False, message="서버에 에러가 발생했습니다. 관리자에게 문의해주세")

@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    logger.error('%s -- 500 ERROR', exception)
    return jsonify(status=False, message="서버에 에러가 발생했습니다. 관리자에게 문의해주세")


#### error handler end####

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    # cron = Scheduler(daemon=True)
    # cron.add_interval_job(job_function, seconds=20) #minites=1)
    # cron.start()
    app.run(debug=True)
    # http_server = WSGIServer(('', 5000), app)
    # http_server.serve_forever()

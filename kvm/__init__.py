# -*- coding: utf-8 -*-

import atexit
import logging
from flask import Flask, send_file, jsonify, request
from kvm.db.database import db_session
from kvm.service.service import server_create, server_list, server_change_status, server_image_list, server_monitor, \
    add_user_sshkey, delete_user_sshkey, list_user_sshkey
from datetime import timedelta
from kvm.util.json_encoder import AlchemyEncoder
from apscheduler.scheduler import Scheduler
from gevent.wsgi import WSGIServer


app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder


### cron job start ###
def job_function():
    server_monitor()
### cron job end ###

#### rest start ####

@app.route('/vm', methods=['GET'])
def list():
    return jsonify(status=True, message="success", list=server_list())


@app.route('/vm', methods=['POST'])
def create():
    name = request.json['name']
    cpu = request.json['cpu']
    memory = request.json['memory']
    disk = request.json['hdd']
    image_id = request.json['id']
    team_name = "1"
    return jsonify(status=True, message=server_create(name, cpu, memory, disk, image_id, team_name))


@app.route('/vm/<id>', methods=['PUT'])
def change_status(id):
    status = request.json['type']
    server_change_status(id, status)
    return jsonify(status=True, message="success")


@app.route('/vm/<id>/snap', methods=['PUT'])
def create_snap(id):
    status = request.json['status']
    server_change_status(id, status)
    return jsonify(status=True, message="success")


@app.route('/vm/images/list/<type>', methods=['GET'])
def list_volume(type):
    return jsonify(status=True, message="success", list=server_image_list(type))


@app.route('/user/sshkey', methods=['POST'])
def add_sshKey():
    team_name = 1
    sshkey = request.json['sshkey']
    name = request.json['name']
    add_user_sshkey(team_name, sshkey, name)
    return jsonify(status=True, message="success")


@app.route('/user/sshkey/<id>', methods=['DELETE'])
def delete_sshKey(id):
    team_name = 1
    delete_user_sshkey(id, team_name)
    return jsonify(status=True, message="success")


@app.route('/user/sshkey', methods=['GET'])
def list_sshKey():
    team_name = 1
    return jsonify(status=True, message="success", list=list_user_sshkey(team_name))

#### rest end ####

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    # cron = Scheduler(daemon=True)
    # cron.add_interval_job(job_function, minutes=5)
    # cron.start()
    # app.run(debug=True)
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()

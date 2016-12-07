# -*- coding: utf-8 -*-

import atexit
import logging
from flask import Flask, send_file, jsonify, request
from kvm.db.database import db_session
from kvm.service.service import server_create, server_list, server_change_status, server_image_list, server_monitor
from datetime import timedelta
from kvm.util.json_encoder import AlchemyEncoder
#from apscheduler.scheduler import Scheduler

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
    image_id = request.json['image_id']
    return jsonify(status=True, message=server_create(name, cpu, memory, disk, image_id))


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


#### rest end ####

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    # cron = Scheduler(daemon=True)
    # cron.add_interval_job(job_function, minutes=5)
    # cron.start()
    app.run(debug=True)

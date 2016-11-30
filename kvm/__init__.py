# -*- coding: utf-8 -*-

import atexit
import logging
from flask import Flask, send_file, jsonify, request
from kvm.db.database import db_session
from kvm.service.service import server_create, server_list, server_change_status, server_image_list, server_monitor
from datetime import timedelta
from kvm.util.json_encoder import AlchemyEncoder
from apscheduler.scheduler import Scheduler

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
    hdd = request.json['hdd']
    base = request.json['base']
    return jsonify(status=True, message=server_create(name, cpu, memory, hdd, base))


@app.route('/vm/status/<vm_name>/<status>', methods=['PUT'])
def change_status(vm_name, status):
    server_change_status(vm_name, status)
    return jsonify(status=True, message="success")


@app.route('/vm/images/<type>', methods=['GET'])
def list_volume(type):
    return jsonify(status=True, message="success", list=server_image_list(type))


#### rest end ####

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    # cron = Scheduler(daemon=True)
    # cron.add_interval_job(job_function, seconds=10)
    # cron.start()
    app.run()


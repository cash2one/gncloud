# -*- coding: utf-8 -*-

import atexit
import logging
from flask import Flask, send_file, jsonify, request
from Manager.db.database import db_session
from Manager.util.json_encoder import AlchemyEncoder
from datetime import timedelta
from service.service import test_list, login_list

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder


#### rest start ####
@app.route('/vm', methods=['GET'])
def run_list():
    return jsonify(status=True, message="success", list=test_list())


@app.route('/vm/guestLogin', methods=['POST'])
def login():
    user_id = request.json['user_id']
    password = request.json['password']
    return jsonify(status=True, message="정보가 잘못되었습니다", list=login_list(user_id, password))


#### rest stop ####

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run(port=8080)

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


#### rest start ####

#### rest end ####

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run()

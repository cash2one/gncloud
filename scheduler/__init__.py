# -*- coding: utf-8 -*-
__author__ = 'nhcho'
import json
from datetime import timedelta
from flask import Flask, jsonify
from controller.schdule_controller import ScheduleController
from util.config import config


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

app.ScheduleController = ScheduleController()
app.ScheduleController.run()

# 페이지 리스트
@app.route("/")
def index():
    return jsonify(status=True, message='서비스 정상 작동')

@app.route("/monitor/restart")
def monitor_restart():
    return app.ScheduleController.monitor.restart_monitor()

@app.route("/invoice_calc/force")
def invoice_calc_force():
    return app.ScheduleController.invoice.invoice_calc()

@app.route("/backup/force")
def backup_force():
    return app.ScheduleController.backup.backup()

@app.route("/backupdelete/force")
def backup_delete_force():
    return app.ScheduleController.backup_delete.backup_delete()

if __name__ == '__main__':
    app.run(host=config.CONTROLLER_HOST,port=int(config.CONTROLLER_PORT))
# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import Flask, redirect
from controller.powershellController import *
from util.config import config


app = Flask(__name__)

app.add_url_rule("/manual", view_func=manual, methods=['GET', 'POST'])
app.add_url_rule("/vm/status/<vm_name>/<status>", view_func=hvm_state, methods=['GET', 'POST'])


# Controller 상태 확인
@app.route("/service/isAlive")
def isAlive():
    return jsonify(status=True, message='서비스 정상 작동')


@app.route("/")
def index():
    return redirect("/service/isAlive")


if __name__ == '__main__':
    app.config['DEBUG'] = False
    app.run(host=config.CONTROLLER_HOST, port=config.CONTROLLER_PORT)

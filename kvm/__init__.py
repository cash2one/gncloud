# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from kvm.conn.kvm_libvirt import server_list, server_create, server_change_status
from datetime import timedelta

app = Flask(__name__)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

@app.route('/list')
def list():
    return jsonify(lists=server_list())

@app.route('/create')
def create():
    server_create("service3", "1524288","2")
    return "ok"

@app.route('/change_status/<vm_name>/<status>')
def change_status(vm_name, status):
    server_change_status(vm_name, status)
    return "ok"

if __name__ == '__main__':
    app.run()

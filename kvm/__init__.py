# -*- coding: utf-8 -*-

from flask import Flask, send_file, jsonify, request
from kvm.conn.kvm_libvirt import server_list, server_create, server_change_status
from datetime import timedelta

app = Flask(__name__)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

@app.route('/list')
def list():
    return jsonify(lists=server_list())

@app.route('/create', methods=['POST'])
def create():
    name = request.form.get('name')
    cpu = request.form.get('cpu')
    memory = request.form.get('memory')
    server_create(name, cpu, memory)
    return "ok"

@app.route('/change_status/<vm_name>/<status>')
def change_status(vm_name, status):
    server_change_status(vm_name, status)
    return "ok"

@app.route("/view/create")
def view_create():
    return send_file("static/html/create.html")

@app.route("/view/list")
def view_list():
    return send_file("static/html/list.html")

if __name__ == '__main__':
    app.run()

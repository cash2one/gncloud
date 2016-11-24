# -*- coding: utf-8 -*-

from flask import Flask, send_file, jsonify, request
from kvm.service.kvm_libvirt import  server_volume_list, server_create_snap
from kvm.service.service import server_create, server_list, server_change_status
from datetime import timedelta
from kvm.util.json_encoder import AlchemyEncoder

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder

@app.route('/guest_list')
def list():
    return jsonify(status=True, message="success", list=server_list())

@app.route('/guest_create', methods=['POST'])
def create():
    name = request.form['name']
    cpu = request.form['cpu']
    memory = request.form['memory']
    hdd = request.form['hdd']
    return jsonify(message=server_create(name, cpu, memory, hdd))

@app.route('/change_status/<vm_name>/<status>')
def change_status(vm_name, status):
    server_change_status(vm_name, status)
    return "ok"

@app.route('/list_volume')
def list_volume():
    return jsonify(lists=server_volume_list())

@app.route('/create_snap', methods=['POST'])
def create_snap():
    name_volume = request.form['name_volume']
    name_snap = request.form['name_snap']
    return jsonify(message=server_create_snap(name_volume, name_snap))

@app.route("/view/<page>")
def view_list(page):
    return send_file("static/html/" + page + ".html")

if __name__ == '__main__':
    # app.debug = True
    app.run()

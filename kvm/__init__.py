# -*- coding: utf-8 -*-

from flask import Flask, send_file, jsonify, request
from kvm.service.kvm_libvirt import server_create_snap
from kvm.service.service import server_create, server_list, server_change_status, server_snap_list
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
    name = request.json['name']
    cpu = request.json['cpu']
    memory = request.json['memory']
    hdd = request.json['hdd']
    base = request.json['base']
    return jsonify(message=server_create(name, cpu, memory, hdd, base))

@app.route('/change_status/<vm_name>/<status>')
def change_status(vm_name, status):
    server_change_status(vm_name, status)
    return "ok"


@app.route('/list_guest_snap', methods=['GET'])
def list_volume():
    return jsonify(status=True, message="success", list=server_snap_list(request.args.get('type')))

@app.route("/view/<page>")
def view_list(page):
    return send_file("static/html/" + page + ".html")

if __name__ == '__main__':
    # app.debug = True
    app.run()

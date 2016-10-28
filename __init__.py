# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from conn.kvm import init_kvm_conn, server_list, server_create, server_delete
app = Flask(__name__)


@app.route('/list')
def list():
    return jsonify(lists=server_list())

@app.route('/create')
def create():
    server_create()
    return "ok"

@app.route('/delete')
def delete():
    server_delete()
    return "ok"


if __name__ == '__main__':
    app.run()

# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import Flask
from controller.powershellController import *


app = Flask(__name__)

app.add_url_rule("/manual", view_func=manual, methods=['GET', 'POST'])
app.add_url_rule("/vm/status/<vm_name>/<status>", view_func=hvm_state, methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run()

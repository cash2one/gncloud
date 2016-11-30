# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

from flask import Flask
from controller.powershellController import *


app = Flask(__name__)

app.add_url_rule("/vm", view_func=newVm, methods=['POST'])


if __name__ == '__main__':
    app.run()

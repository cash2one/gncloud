# -*- coding: utf-8 -*-
__author__ = 'gncloud'

import urllib, json
import requests

class PowerShell():

    def __init__(self, address, port, uri):
        self.address = address
        self.port = port
        self.uri = uri

    def send(self):
        address = self.address
        port = str(self.port)
        uri = self.uri
        #URL = "http://60.196.149.135:8180/powershell/execute?script=Get-VM%20%7C%20Convertto-Json"
        URL = address
        URL += ":"
        URL += port
        URL += "/"
        URL += uri

        data = {'param1': 'value1', 'param2': 'value'}
        response = requests.post(URL, data = json.dumps(data))
        #print URL
        print response.json()

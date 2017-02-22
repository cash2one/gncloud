# -*- coding: utf-8 -*-

__author__ = 'NaDa'

import json
import os
import subprocess

import humanfriendly
import requests
from flask import render_template
from pexpect import pxssh
from sqlalchemy import func,or_

from Manager.db.database import db_session
from Manager.db.models import *
from Manager.util.config import config
from Manager.util.hash import random_string, convertToHashValue, convertsize



#_________________________과금______________________________________________________________#

def team_price_lsit(team_code,page,sql_session):
    page_size = 10
    page = int(page)-1
    total_query = sql_session.query(func.count(GnInvoiceResult.team_code).label("count"))
    list_query = sql_session.query(GnInvoiceResult)
    if team_code != "000":
        total_query = total_query.filter(GnInvoiceResult.team_code == team_code)
        list_query = list_query.filter(GnInvoiceResult.team_code == team_code)
    total_page= total_query.one()
    list=list_query.limit(page_size).offset(page*page_size).all()
    for vm in list:
        vm.invoice_data=json.loads(vm.invoice_data)
    total=int(total_page.count)/10
    return {"list":list, "total_page":total_page.count,"total":total, "page":page}

    return list

def team_price_lsit_info(year,month,team_code,sql_session):
    list = sql_session.query(GnInvoiceResult).filter(GnInvoiceResult.year==year).filter(GnInvoiceResult.month == month) \
        .filter(GnInvoiceResult.team_code==team_code).one()
    team_name = sql_session.query(GnTeam).filter(GnTeam.team_code == team_code).one()
    instance=json.loads(list.invoice_data)
    team = sql_session.query(GnTeam).filter(GnTeam.team_code == list.team_code).one()
    return {"list":list, "instance":instance, "team_code":team_name}



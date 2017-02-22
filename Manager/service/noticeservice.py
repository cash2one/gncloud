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

#-------------공지사항 관련 start ------------------------------------#

def notice_list(page,sql_session):
    page_size=10
    page=int(page)-1
    list = sql_session.query(GnNotice).order_by(GnNotice.write_date.desc()).limit(page_size).offset(page*page_size).all()
    total_page= sql_session.query(func.count(GnNotice.id).label("count")).one()
    total=int(total_page.count)/10
    for vm in list:
        vm.write_date = vm.write_date.strftime('%Y-%m-%d %H:%M')
    return {"list":list, "total_page":total_page.count,"total":total, "page":page}

def notice_info(id,sql_session):
    list = sql_session.query(GnNotice).filter(GnNotice.id ==id).one()
    list.write_date = list.write_date.strftime('%Y-%m-%d %H:%M')
    return list

def notice_create(title, text, sql_session):
    notice_info = GnNotice(title=title, text=text,write_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(notice_info)
    sql_session.commit()

def notice_change(id ,text, sql_session):
    notice_info=sql_session.query(GnNotice).filter(GnNotice.id == id).one()
    notice_info.text = text
    sql_session.commit()

def notice_delete(id, sql_session):
    sql_session.query(GnNotice).filter(GnNotice.id == id).delete()
    sql_session.commit()

    #-------------공지사항 관련 END ------------------------------------#
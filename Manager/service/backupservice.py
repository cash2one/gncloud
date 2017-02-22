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


#_________________________백업______________________________________________________________#
def backup_list(page,sql_session):
    page_size = 10
    page = int(page)-1
    total_page= sql_session.query(func.count(GnBackup.vm_id).label("count")).one()
    list=sql_session.query(GnBackup).order_by(GnBackup.backup_time.desc()).limit(page_size).offset(page*page_size).all()
    total=int(total_page.count)/10
    for vm in list:
        vm.backup_time = vm.backup_time.strftime('%Y-%m-%d %H:%M')
    return {"list":list, "total_page":total_page.count,"total":total, "page":page}

def backup_hist(vm_id, sql_session):
    vm_info = sql_session.query(GnBackup).filter(GnBackup.vm_id == vm_id).one()
    hist_info = sql_session.query(GnBackupHist).filter(GnBackupHist.vm_id == vm_id).order_by(GnBackupHist.backup_time.desc()).all()
    total = len(hist_info)
    for hist in hist_info:
        hist.backup_time = hist.backup_time.strftime('%Y-%m-%d %H:%M')
    return {"vm_info":vm_info,"hist_info":hist_info,"total":total}

def team_backup_list(page,team_code,sql_session):
    page_size = 10
    page = int(page)-1
    total_page= sql_session.query(func.count(GnBackup.vm_id).label("count")).filter(GnBackup.team_code == team_code).one()
    list=sql_session.query(GnBackup).filter(GnBackup.team_code == team_code).order_by(GnBackup.backup_time.desc()).limit(page_size).offset(page*page_size).all()
    total=int(total_page.count)/10
    for vm in list:
        vm.backup_time = vm.backup_time.strftime('%Y-%m-%d %H:%M')
    return {"list":list, "total_page":total_page.count,"total":total, "page":page}
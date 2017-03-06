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


def qna_list(page,team_code,syscheck,sql_session):
    qna_count=[]
    if syscheck =='sysowner':
        team_info = sql_session.query(GnTeam).filter(GnTeam.team_code == team_code).one()
        page_size=10
        page=int(page)-1
        qna_info = sql_session.query(GnQnA).filter(GnQnA.farent_id == None) \
            .order_by(GnQnA.create_date.desc()).limit(page_size).offset(page*page_size).all()
        total_page = total_page= sql_session.query(func.count(GnQnA.id).label("count")) \
            .filter(GnQnA.farent_id==None).one()
        total=int(total_page.count)/10
        for qna in qna_info:
            qna.create_date = qna.create_date.strftime('%Y-%m-%d %H:%M')
            qna.author_id = qna.gnUser.user_name
            qna_count.append(len(sql_session.query(GnQnA).filter(GnQnA.farent_id ==qna.id).all()))
    else:
        team_info = sql_session.query(GnTeam).filter(GnTeam.team_code == team_code).one()
        page_size=10
        page=int(page)-1
        qna_info = sql_session.query(GnQnA).filter(GnQnA.farent_id == None) \
            .order_by(GnQnA.create_date.desc()).filter(GnQnA.team_code==team_code).limit(page_size).offset(page*page_size).all()
        total_page = sql_session.query(func.count(GnQnA.id).label("count")) \
            .filter(GnQnA.farent_id==None).filter(GnQnA.team_code==team_code).one()
        total=int(total_page.count)/10
        for qna in qna_info:
            qna.create_date = qna.create_date.strftime('%Y-%m-%d %H:%M')
            qna.author_id = qna.gnUser.user_name
            qna_count.append(len(sql_session.query(GnQnA).filter(GnQnA.farent_id ==qna.id).all()))
    return {"list":qna_info, "total_page":total_page.count,"total":total, "page":page, "team_info":team_info,"qna_count":qna_count}

def qna_info_list(id,sql_session):
    qna_info = sql_session.query(GnQnA).filter(GnQnA.id ==id).one()
    qna_info.author_id = qna_info.gnUser.user_name
    qna_ask = sql_session.query(GnQnA).filter(GnQnA.farent_id ==id).all()
    for qna in qna_ask:
        qna.author_id = qna.gnUser.user_name
    qna_info.create_date = qna_info.create_date.strftime('%Y-%m-%d %H:%M')
    return {"qna_info":qna_info, "qna":qna_ask}

def qna_ask(title,text,user_id,team_code,sql_session):
    qna_ask_inf = GnQnA(title=title, text=text,author_id=user_id, team_code=team_code,create_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(qna_ask_inf)
    sql_session.commit()

def qna_ask_reply(id, text, user_id,team_code ,sql_session):
    qna_ask_replys=GnQnA(farent_id=id ,text=text,author_id=user_id,team_code=team_code,create_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(qna_ask_replys)
    sql_session.commit()

def qna_ask_reply_change(id,user_id ,text, sql_session):
    qna_ask_replys= sql_session.query(GnQnA).filter(GnQnA.id==id).one()
    qna_ask_replys.text = text
    sql_session.commit()

def qna_ask_change(id, user_id , text, sql_session):
    qna_ask_info = sql_session.query(GnQnA).filter(GnQnA.id == id).filter(GnQnA.farent_id == None).one()
    qna_ask_info.text =text
    sql_session.commit()

def qna_ask_delete(id, sql_session):
    sql_session.query(GnQnA).filter(GnQnA.id==id).delete()
    sql_session.query(GnQnA).filter(GnQnA.farent_id==id).delete()
    sql_session.commit()

def qna_ask_reply_delete(id , sql_session):
    sql_session.query(GnQnA).filter(GnQnA.id==id).delete()
    sql_session.commit()
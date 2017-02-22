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


def login_list(user_id, password, sql_session):
    password = convertToHashValue(password)
    user_info = sql_session.query(GnUser, GnUserTeam) \
        .outerjoin(GnUserTeam, GnUserTeam.user_id == GnUser.user_id) \
        .filter(GnUser.user_id == user_id) \
        .filter(GnUser.password == password) \
        .one_or_none()
    if user_info != None:
        if(user_info.GnUserTeam != None):
            login_hist=GnLoginHist(user_id=user_info.GnUser.user_id, action='login',team_code=user_info.GnUserTeam.team_code,action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            sql_session.add(login_hist)
            sql_session.commit()
        else:
            login_hist=GnLoginHist(user_id=user_info.GnUser.user_id, action='login',action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            sql_session.add(login_hist)
            sql_session.commit()
    return user_info

def logout_info(user_id, team_code, sql_session):
    logout = GnLoginHist(user_id=user_id, team_code=team_code, action='logout', action_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    sql_session.add(logout)
    sql_session.commit()


def teamwon_list(user_id,team_code,team,sql_session):
    list =sql_session.query(GnUser, GnUserTeam).join(GnUserTeam, GnUserTeam.user_id == GnUser.user_id).filter(GnUserTeam.team_code == team_code) \
        .filter(GnUserTeam.team_owner==team).order_by(GnUserTeam.team_owner.desc()).all()
    if len(list) ==0:
        list = None
    team_list = len(sql_session.query(GnUserTeam).filter(GnUserTeam.team_code == team_code).all())
    infor = {"list":list, "info":team_list}
    return infor

def teamwoninfo_list(user_id,sql_session):
    list = sql_session.query(GnUser,GnUserTeam).join(GnUserTeam, GnUserTeam.user_id == GnUser.user_id).filter(GnUserTeam.user_id == user_id).all()
    for vm in list:
        vm[1].apply_date = vm[1].apply_date.strftime('%Y-%m-%d %H:%M:%S')
        if(vm[1].approve_date != None):
            vm[1].approve_date = vm[1].approve_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            vm[1].approve_date = "-"
    return list

def teamcheck_list(teamcode):
    return db_session.query(GnUser).filter(GnUser.team_code == teamcode).all()


def tea(user_id, team_code, sql_session):
    sub_stmt = sql_session.query(GnUserTeam.user_id).filter(GnUserTeam.team_code == team_code)
    list = sql_session.query(GnUser).filter(GnUser.user_id.in_(sub_stmt)).all()
    return list


def teamcheck_list(user_id,sql_session):
    list = sql_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).all()
    return list


def sign_up(user_name, user_id, password, password_re):
    check = db_session.query(GnUser).filter(GnUser.user_id == user_id).one_or_none()
    if(password == password_re):
        if(check == None):
            password_sha = convertToHashValue(password_re)
            sign_up_info = GnUser(user_id = user_id, password = password_sha,user_name = user_name,tel="-",email="-",start_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            db_session.add(sign_up_info)
            db_session.commit()
            return 'success'
        else:
            return 'user_id'
    else:
        return 'password'

def repair(user_id, password, password_new, password_re, tel, email,user_name ,sql_session):
    test = sql_session.query(GnUser).filter(GnUser.user_id == user_id).one()
    if password != "":
        password = convertToHashValue(password)
        list = sql_session.query(GnUser).filter(GnUser.user_id == user_id).filter(GnUser.password==password).one_or_none()
        if (list != None and password_re == password_new):
            list.password = convertToHashValue(password_re)
        else:
            return 1
    if user_name != "":
        test.user_name = user_name
    test.tel = tel
    test.email = email
    sql_session.commit()
    return 2

def team_list(user_id, sql_sesssion):
    list= sql_sesssion.query(GnUser).filter(GnUser.user_id ==user_id).one()
    return list

def teamsignup_list(comfirm, user_id):
    if(comfirm == 'N'):
        com= db_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).all()
        com.comfirm = 'Y'
        db_session.commit()
    return 1
def teamset(team_code, sql_session):
    list = sql_session.query(GnUser,GnUserTeam).join(GnUserTeam, GnUserTeam.user_id == GnUser.user_id).filter(GnUserTeam.team_code == team_code).all()
    for vm in list:
        vm[0].start_date = vm[0].start_date.strftime('%Y-%m-%d %H:%M:%S')
        vm[1].apply_date = vm[1].apply_date.strftime('%Y-%m-%d %H:%M:%S')
        if(vm[1].approve_date != None):
            vm[1].approve_date = vm[1].approve_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            vm[1].approve_date = "-"
    return list

def approve_set(user_id,code,type,user_name,sql_session):
    if(type == 'approve'):
        list = sql_session.query(GnUserTeam).filter(GnUserTeam.user_id==user_id).filter(GnUserTeam.team_code == code).first()
        if(list.comfirm == 'Y'):
            return False
        list.comfirm = "Y"
        list.team_owner='user'
        sql_session.commit()
        return 1
    if(type == 'change'):
        list = sql_session.query(GnUserTeam).filter(GnUserTeam.user_id== user_id).first()
        if(list.team_owner == 'owner'):
            list.team_owner = 'user'
            sql_session.commit()
            return 4
        elif(list.team_owner == 'user'):
            list.team_owner = 'owner'
            sql_session.commit()
            return 2
    if(type == 'reset'):
        list = sql_session.query(GnUser).filter(GnUser.user_id==user_id).first()
        list.password = convertToHashValue('11111111')
        sql_session.commit()
        return 3

def team_delete(id ,code):
    db_session.query(GnUserTeam).filter(GnUserTeam.user_id == id).filter(GnUserTeam.team_code == code).delete()
    db_session.commit()
    return True

def signup_team(team_code,user_id,sql_session):
    list = sql_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).one_or_none()
    if(list ==None):
        vm = GnUserTeam(user_id= user_id, team_code= team_code, comfirm = 'N',apply_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'),team_owner='user')
        db_session.add(vm)
        db_session.commit()
        return 1
    return 2

def comfirm_list(user_id, sql_session):
    team =sql_session.query(GnUserTeam).filter(GnUserTeam.user_id == user_id).one()
    team.apply_date = team.apply_date.strftime('%Y-%m-%d')
    if(team.comfirm != 'Y'):
        list =sql_session.query(GnTeam).filter(GnTeam.team_code ==team.team_code).one()
        team_info = {'user_id' : user_id, 'apply_date': team.apply_date, 'team_name':list.team_name, 'team_code': team.team_code}
    return team_info


def createteam_list(user_id,team_name, team_code, author_id, sql_session):
    if(sql_session.query(GnTeam).filter(GnTeam.team_name == team_name).one_or_none() == None):
        if(sql_session.query(GnTeam).filter(GnTeam.team_code == team_code).one_or_none() == None):
            vm = GnTeam(team_code= team_code, team_name=team_name, author_id=author_id,cpu_quota=4,mem_quota=4294967296,disk_quota= 42949672960, create_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            tm = GnUserTeam(user_id=user_id, team_code=team_code, comfirm='Y', apply_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'),approve_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'), team_owner='owner')
            db_session.add(vm)
            db_session.add(tm)
            db_session.commit()
            return 'success'
        else:
            return 'team_code'
    else:
        return 'team_name'
def select(sql_session ):
    return sql_session.query(GnTeam).filter(GnTeam.author_id != 'System').all()

def select_info(team_code, sql_session): #팀 프로필 팀생성일/ 이름 개인설정 팀프로필 팀 생성일 /이름
    list =sql_session.query(GnTeam).filter(GnTeam.team_code == team_code).order_by(GnTeam.create_date.desc()).one()
    list.create_date = list.create_date.strftime('%Y-%m-%d %H:%M:%S')
    return list

def select_put(team_name, team_code): #팀 수정
    lit =db_session.query(GnTeam).filter(GnTeam.team_code== team_code).one()
    lit.team_name = team_name
    db_session.commit()
    return True

def select_putsys(team_name, team_code, team_cpu, team_memory, team_disk): #팀 시스템 수정 / cpu / memory / disk
    lit =db_session.query(GnTeam).filter(GnTeam.team_code== team_code).one()
    try:
        if team_name != "":
            lit.team_name = team_name
        if team_cpu !="":
            lit.cpu_quota = team_cpu
        if team_memory != "":
            lit.mem_quota = convertsize(team_memory)
        if team_disk != "":
            lit.disk_quota = convertsize(team_disk)
        db_session.commit()
        return True
    except:
        return False
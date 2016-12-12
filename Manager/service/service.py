__author__ = 'NaDa'
# -*- coding: utf-8 -*-
import datetime

from Manager.db.models import GnVmMachines, GnUser
from Manager.db.database import db_session
from Manager.util.hash import random_string


def test_list():
    runlist = GnVmMachines.query.all()
    return runlist

def login_list(user_id, password, team_code):
    password = random_string(password)
    return db_session.query(GnUser).filter(GnUser.team_code == team_code).filter(GnUser.user_id == user_id).filter(GnUser.password == password).one_or_none()


def me_list(myuser):
    return db_session.query(GnUser).filter(GnUser.user_id == myuser).one()

def teamcheck_list(teamcode):
    return db_session.query(GnUser).filter(GnUser.team_code == teamcode).all()

def sign_up(user_name, user_id, password, password_re):
    check = db_session.query(GnUser).filter(GnUser.user_id == user_id).one_or_none()
    print check
    if(password == password_re):
        if(check == None):
            password_sha = random_string(password_re)
            sign_up_info = GnUser(user_id = user_id, password = password_sha,user_name = user_name,start_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            db_session.add(sign_up_info)
            db_session.commit()
            return True
        else:
            return None
    else:
        return None

def repair(user_id, password, password_new, password_re, tel, email):
    test = db_session.query(GnUser).filter(GnUser.user_id == user_id).one_or_none()
    if password != "":
        password = random_string(password)
        test = db_session.query(GnUser).filter(GnUser.user_id == user_id).filter(GnUser.password==password).one_or_none()
        if (test != None and password_re == password_new):
              test.password = random_string(password_re)
        else:
                return 1


    if tel != "":
        test.tel = tel

    if email != "":
        test.eamil = email

    db_session.commit()
    return 2
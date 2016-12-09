__author__ = 'NaDa'
import datetime

from manager.db.models import GnVmMachines, GnUser
from manager.db.database import db_session


def test_list():
    runlist = GnVmMachines.query.all()
    return runlist

def login_list(user_id, password, team_code):
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
            sign_up_info = GnUser(user_id = user_id, password = password,user_name = user_name,start_date=datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            db_session.add(sign_up_info)
            db_session.commit()
            return True
        else:
            return None
    else:
        return None

def repair(user_id,user_name,team_code ,password, password_new, password_re, tel, email):
    test = db_session.query(GnUser).filter(GnUser.user_id == user_id).filter(GnUser.password == password).one_or_none()
    if(test != None):
        if(password_new == password_re):
            repair_info=GnUser(user_name=user_name,password= password_new, tel = tel, email = email)
            db_session.add(repair_info)
            db_session.commit()
            return True
        else:
            return 1
    else:
        pass
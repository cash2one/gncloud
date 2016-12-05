__author__ = 'NaDa'
from Manager.db.models import GnVmMachines, GnUser
from Manager.db.database import db_session

def test_list():
    runlist = GnVmMachines.query.all()
    return runlist

def login_list(user_id, password):
    user = db_session.query(GnUser).filter(GnUser.user_id == user_id).one_or_none()
    #user = GnUser.query.all()
    if(user == password):
        status = True
    else:
        status = False
    return status

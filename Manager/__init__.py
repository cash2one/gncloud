# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, session, escape
from datetime import timedelta

from Manager.db.database import db_session
from Manager.util.json_encoder import AlchemyEncoder
from service.service import test_list, login_list, me_list, teamcheck_list, sign_up, repair, getQuotaOfTeam, server_list, server_image_list

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#### rest start ####
@app.route('/')
def index():
    if 'userId' in session:
        return jsonify(status=True, message='Logged in as %s'% escape(session['user_id']))
    return jsonify(status=False, message='You are not logged in')

@app.route('/vm', methods=['GET'])
def run_list():
    return jsonify(status=True, message="success", list=test_list())


@app.route('/vm/account', methods=['POST'])
def login():
    user_id = request.json['user_id']
    password = request.json['password']
    team_code = request.json['team_code']
    user_info = login_list(user_id, password, team_code)
    if user_info != None:
        session['userId'] = user_info.user_id;
        session['userName'] = user_info.user_name;
        session['teamCode'] = user_info.team_code;
        return jsonify(status=True, message="login as "+user_id)
    else:
        return jsonify(status=False, message="정보가 잘못되었습니다")

@app.route('/vm/guestLogout', methods=['GET'])
def logout():
    # print session['userId']
    session.clear()
    return jsonify(status=True, message="success")

@app.route('/vm/logincheck', methods=['GET'])
def logincheck():
    if session.get('userId',None):
        return jsonify(status= 1, message=session['userName'])
    else:
        return jsonify(status= 2)

@app.route('/vm/guestMeList', methods=['GET'])
def my_list():
    if session.get('userId',None):
        myuser = session['userId']
        return jsonify(status=True, message="success", list=me_list(myuser))
    else:
        pass

@app.route('/vm/account/users', methods=['GET'])
def teamcheck():
    if session.get('userId',None):
        teamcode=session['teamCode']
        return jsonify(status=True, message="success", list=teamcheck_list(teamcode))

@app.route('/vm/account/users', methods=['POST'])
def signup_list():
    user_name = request.json['user_name']
    user_id = request.json['user_id']
    password = request.json['password']
    password_re = request.json['password_re']
    if(sign_up(user_name,user_id,password,password_re)!=None):
        return  jsonify(status=True, message="success")
    else:
        return jsonify(status = False, message = "false")

@app.route('/vm/account/users/list', methods=['PUT'])
def repair_list():
    password=""
    password_new=""
    password_ret=""
    tel=""
    email=""
    if request.json == None:
        return jsonify(status=False, message = 'False')
    if 'password' in request.json:
        password = request.json['password']
    if 'password_new' in request.json:
        password_new = request.json['password_new']
    if 'password_ret' in request.json:
        password_ret = request.json['password_ret']
    if 'tel' in request.json:
        tel = request.json['tel']
    if 'email' in request.json:
        email = request.json['email']
    if session.get('userId', None):
        user_id=session['userId']
        user_name =session['userName']
        team_code = session['teamCode']
        test = repair(user_id, password, password_new,password_ret, tel, email)
        if test == 2:
            return jsonify(status=2, message='success')
        elif test == 1:
            return jsonify (status=1, message = '비밀번호가 틀렸습니다.')
        else:
            return jsonify(status=False, message = 'False')

@app.route('/useinfo', methods=['GET'])
def quota_info():
    team_code = "004"
    return jsonify(status=True, message = 'success',list=getQuotaOfTeam(team_code))


@app.route('/vm/machines', methods=['GET'])
def list():
    return jsonify(status=True, message="success", list=server_list(db_session))

@app.route('/vm/images/<type>/<sub_type>', methods=['GET'])
def list_volume(type, sub_type):
    return jsonify(status=True, message="success", list=server_image_list(type, sub_type))

#### rest stop ####

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run(port=8080)

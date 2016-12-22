# -*- coding: utf-8 -*-
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, request, session, escape, make_response
from datetime import timedelta

from Manager.db.database import db_session
from Manager.util.json_encoder import AlchemyEncoder
from service.service import vm_list, vm_info, login_list, teamwon_list, teamcheck_list, sign_up, repair, getQuotaOfTeam, server_image_list\
                            , vm_update_info, vm_info_graph, server_image_list, teamsignup_list, team_list, server_image, container, tea, teamset, approve_set \
                            , team_delete, createteam_list, comfirm_list, teamwon_list, checkteam, signup_team, select, select_list, select_put, team_table \
                            , pathimage
from db.database import db_session

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


#####common function start#####


# @app.before_request
# def before_request():
#     if ('userId' not in session) \
#             and request.endpoint != 'guestLogout' \
#             and request.endpoint != 'account':
#         return make_response(jsonify(status=False),401)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


#####common function end#####


#### rest start ####
@app.route('/')
def index():
    return jsonify(status=True, message='Logged in as %s'% escape(session['user_id']))


@app.route('/vm/machines', methods=['GET'])
@login_required
def guest_list():
    return jsonify(status=True, message="success", list=vm_list(db_session))


@app.route('/vm/machines/<id>', methods=['GET'])
def guest_info(id):
    return jsonify(status=True, message="success", info=vm_info(db_session, id))


@app.route('/vm/machines/<id>/graph', methods=['GET'])
def guest_info_graph(id):
    return jsonify(status=True, message="success", info=vm_info_graph(db_session, id))


@app.route('/vm/account', methods=['POST'])
def login():
    user_id = request.json['user_id']
    password = request.json['password']
    user_info = login_list(user_id, password)
    team_info = checkteam(user_id)
    if(user_info != None and team_info == None ):
        session['userId'] = user_info.user_id
        session['userName'] = user_info.user_name
        return jsonify(status=True, message="login as "+user_id, test='no')
    elif(user_info != None and team_info.comfirm == "Y"):
        session['userId'] = user_info.user_id
        session['userName'] = user_info.user_name
        session['teamCode'] = team_info.team_code
        return jsonify(status=True, message="login as "+user_id, test='yes')

    elif(user_info != None and team_info.comfirm == "N" ):
        session['userId'] = user_info.user_id
        session['userName'] = user_info.user_name
        return jsonify(status=True, message="login as "+user_id, test='noyes')
    else:
        return jsonify(status=False, message="정보가 잘못되었습니다")


@app.route('/vm/guestLogout', methods=['GET'])
def logout():
    session.clear()
    return jsonify(status=True, message="success")


@app.route('/vm/logincheck', methods=['GET'])
def logincheck():
    if session.get('userId',None):
        return jsonify(status= 1, message=session['userName'])
    else:
        return jsonify(status= 2)


@app.route('/vm/account/users', methods=['GET'])
def teamcheck():
    if session.get('userId',None):
        return jsonify(status=True, message="success", list=teamcheck_list(session['userId']))


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
    return jsonify(status=True, message = 'success',list=getQuotaOfTeam(team_code, db_session))


@app.route('/vm/machines', methods=['GET'])
def list():
    return jsonify(status=True, message="success", list=vm_list(db_session))


@app.route('/vm/images/<type>/<sub_type>', methods=['GET'])
def list_volume(type, sub_type):
    return jsonify(status=True, message="success", list=server_image_list(type, sub_type, db_session))


@app.route('/vm/images/<type>', methods=['GET'])
def volume(type):
    return jsonify(status=True, message="success", list=server_image(type, db_session))


@app.route('/vm/account/users/list', methods=['GET'])
def team():
    if session.get('userId', None):
        return jsonify(status=True, message="success", list=team_list(session['userId']))


@app.route('/vm/account/team', methods=['GET'])
def my_list():
    team_owner = 'owner'
    if session.get('userId',None):
        return jsonify(status=True, message="success", list=teamwon_list(session['userId'],session['teamCode'],team_owner ,db_session))


@app.route('/vm/acoount/teamlist', methods=['GET'])
def tea_list():
    session_id = ''
    team_id = "002"
    return jsonify(status=True, message="success", list=tea(session_id, team_id))


@app.route('/vm/container/services', methods=['GET'])
def container_list():
    return jsonify(status=True, message="success", list=container(db_session))


@app.route('/vm/account/teamset',methods=['GET'])
def teamwon():
    user_id = session['userId']
    team_code = "002"
    return jsonify(status=True, message="success", list=teamset(user_id, team_code, db_session))

@app.route('/vm/account/teamset/<id>/<code>',methods=['PUT'])
def approve(id,code):
    type = request.json['type']
    user_name = session['userName']
    approve_set(id, code, type, user_name)
    return jsonify(status=True, message="success")


@app.route('/vm/account/teamset/<id>/<code>',methods=['DELETE'])
def delete(id,code):
    id = session['userId']
    team_delete(id, code)
    return jsonify(status=True, message="success")


@app.route('/vm/images/<sub_type>', methods=['GET'])
def list_subtype_volume(sub_type):
    return jsonify(status=True, message="success", list=server_image_list(sub_type,db_session))


@app.route('/vm/machines/<id>/<type>', methods=['PUT'])
def update_guest_name(id, type):
    change_value = request.json['value']
    vm_update_info(id,type,change_value,db_session)
    return jsonify(status=True, message="success")


@app.route('/vm/account/selectteam', methods=['GET'])
def selectteam():
    return jsonify(status=True, message="success", list=select())


@app.route('/vm/account/selectteam', methods=['POST'])
def teamsignup():
    team_code = request.json['team_code']
    user_id = session['userId']
    signup_team(team_code, user_id)
    return jsonify(status=True, message="success")


@app.route('/vm/account/teamcomfirm', methods=['GET'])
def comfirm():
    user_id = session['userId']
    return jsonify(status=True, message="success", list=comfirm_list(user_id))


@app.route('/vm/account/createteam', methods=['POST'])
def createteam():
    team_name = request.json['team_name']
    team_code = request.json['team_code']
    author_id = session['userName']
    return jsonify(status=True, message="success", list=createteam_list(team_name, team_code, author_id))

@app.route('/vm/account/teamname', methods=['GET'])
def teamname():
    return jsonify(status=True, message="success", list=select_list(session['teamCode']))

@app.route('/vm/account/teamname', methods=['PUT'])
def changeteamname():
    team_name = request.json['team_name']
    return jsonify(status=True, message="success", list=select_put(team_name,session['teamCode']))

@app.route('/vm/account/teamtable', methods=['GET'])
def teamshow():
    return jsonify(status=True, message="success", list=team_table(db_session))

@app.route('/vm/systems/path', methods=['GET'])
def systembase():
    return jsonify(status=True, message="success", list=pathimage(db_session))
#### rest end ####


if __name__ == '__main__':

    # 로그 설정
    formatter = logging.Formatter('[%(asctime)s %(levelname)s] (%(filename)s:%(lineno)s) %(message)s')
    handler = RotatingFileHandler('manager.log', maxBytes=2000000, backupCount=5)
    handler.setFormatter(formatter)
    handler.setLevel(logging.WARNING)

    app.run(port=8080)
    #http_server = WSGIServer(('', 8080), app)
    #http_server.serve_forever()

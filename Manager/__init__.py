# -*- coding: utf-8 -*-
import traceback

from flask import Flask, jsonify, request, session, escape, make_response
from datetime import timedelta

from Manager.db.database import db_session
from Manager.util.json_encoder import AlchemyEncoder
from service.service import vm_list, vm_info, login_list, teamwon_list, teamcheck_list, sign_up, repair, getQuotaOfTeam, server_image_list\
                            , vm_update_info, vm_info_graph, teamsignup_list, team_list, server_image, container, tea, teamset, approve_set \
                            , team_delete, createteam_list, comfirm_list, teamwon_list, checkteam, signup_team, select, select_put, team_table \
                            , pathimage, select_info, delteam_list, containers, server_create, server_change_status, server_create_snapshot\
                            , hostMachineList \
                            , pathimage, select_info, delteam_list, containers, server_create, server_change_status, server_create_snapshot, teamwoninfo_list
from db.database import db_session

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


#####common function start#####


@app.before_request
def before_request():
    if ('userId' not in session) and request.path != '/vm/logincheck' and request.path != '/vm/guestLogout' and request.path != '/vm/account' and (request.path!= 'vm/account/users' and request.method !='POST') and  request.path != '/vm/account/testtest':
        return make_response(jsonify(status=False),401)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.errorhandler(500)
def internal_error(error):
    print(traceback.format_exc())
    return jsonify(status=False, message="서버에 에러가 발생했습니다. 관리자에게 문의해주세")

#####common function end#####


#### rest start ####
@app.route('/')
def index():
    return jsonify(status=True, message='Logged in as %s'% escape(session['user_id']))

@app.route('/vm/machine', methods=['POST'])
def create_vm():
    password=""
    sshkeys=""
    team_code = session['teamCode']
    user_id = session['userId']
    name = request.json['vm_name']
    cpu = request.json['cpu']
    memory = request.json['memory']
    disk = request.json['hdd']
    image_id = request.json['id']
    if 'sshkeys' in request.json:
        sshkeys = request.json['sshkeys']
    tag =request.json['tag']
    type =request.json['type']
    if 'password' in request.json:
        password = request.json['password']
    result = server_create(name, cpu, memory, disk, image_id, team_code, user_id, sshkeys, tag, type, password, db_session)
    return jsonify(status=result["status"], value=result["value"])

@app.route('/vm/machine/snapshots', methods=['POST'])
def create_snapshots():
    team_code = session['teamCode']
    user_id = session['userId']
    name= request.json['vm_name']
    image_id = request.json['ord_id']
    type =request.json['type']
    result= server_create_snapshot(image_id, name, user_id, team_code, type, db_session)
    return jsonify(status=result["status"], value=result["value"], snap_id=result["snap_id"])

@app.route('/vm/machine', methods=['PUT'])
def change_status():
    id = request.json['id']
    status = request.json['status']
    server_change_status(id, status, db_session)
    return jsonify(status=True, message="success")

@app.route('/vm/machines', methods=['GET'])
def guest_list():
    team_code = session['teamCode']
    return jsonify(status=True, message="success", list=vm_list(db_session, team_code))


@app.route('/vm/machines/<id>', methods=['GET'])
def guest_info(id):
    return jsonify(status=True, message="success", info=vm_info(db_session, id))


@app.route('/vm/machines/<id>/graph', methods=['GET'])
def guest_info_graph(id):
    return jsonify(status=True, message="success", info=vm_info_graph(db_session, id))


@app.route('/vm/account', methods=['POST'])
def login():
    user_id = request.json['login_id']
    password = request.json['login_pw']
    user_info = login_list(user_id, password, db_session)
    team_info = checkteam(user_id, db_session)
    if(user_info != None and team_info == None ):
        session['userId'] = user_info.user_id
        session['userName'] = user_info.user_name
        session['teamOwner'] = ""
        session['teamCode'] = ""
        return jsonify(status=True, test='no')
    elif(user_info != None and team_info.comfirm == "Y"):
        session['userId'] = user_info.user_id
        session['userName'] = user_info.user_name
        session['teamCode'] = team_info.team_code
        session['teamOwner'] = team_info.team_owner
        return jsonify(status=True, test='yes')

    elif(user_info != None and team_info.comfirm == "N" ):
        session['userId'] = user_info.user_id
        session['userName'] = user_info.user_name
        session['teamOwner'] = ""
        session['teamCode'] = ""
        return jsonify(status=True, test='noyes')
    else:
        return jsonify(status=True, test='noo')

@app.route('/vm/account/users', methods=['POST'])
def signup_list():
    user_name = request.json['user_name']
    user_id = request.json['user_id']
    password = request.json['password']
    password_re = request.json['password_re']
    if(user_id != "" and user_name != "" and password != "" and password_re != ""):
        check=sign_up(user_name,user_id,password,password_re)
        if(check == 'success'):
            return  jsonify(status=True, test='success')
        elif(check == 'password'):
            return jsonify(status=True, test='password')
        elif(check =='user_id'):
            return jsonify(status=True, test='user_id')
    return jsonify(status=False, test='not')
@app.route('/vm/guestLogout', methods=['GET'])
def logout():
    session.clear()
    return jsonify(status=True, message="success")


@app.route('/vm/logincheck', methods=['GET'])
def logincheck():
    user_info = {"name":session['userName'],"user_id": session['userId'], "authority":session['teamOwner'], "team_code":session['teamCode']}
    return jsonify(status= True, info=user_info)


@app.route('/vm/account/users', methods=['GET'])
def teamcheck():
    return jsonify(status=True, message="success", list=teamcheck_list(session['userId'],db_session))


@app.route('/vm/account/users/list', methods=['PUT'])
def repair_list():
    password=""
    password_new=""
    password_ret=""
    tel=""
    email=""
    if request.json == None:
        return jsonify(status=False, message='False')
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
        test = repair(user_id, password, password_new,password_ret, tel, email, db_session)
        if test == 2:
            return jsonify(status=2, message='success')
        elif test == 1:
            return jsonify (status=1, message = '비밀번호가 틀렸습니다.')
        else:
            return jsonify(status=False, message = 'False')


@app.route('/useinfo', methods=['GET'])
def quota_info():
    team_code = session['teamCode']
    return jsonify(status=True, message = 'success',list=getQuotaOfTeam(team_code, db_session))

@app.route('/useinfo/<code>', methods=['GET'])
def quota(code):
    return jsonify(status=True, message = 'success',list=getQuotaOfTeam(code, db_session))

@app.route('/vm/machines', methods=['GET'])
def list():
    return jsonify(status=True, message="success", list=vm_list(db_session))


@app.route('/vm/images/<type>/<sub_type>', methods=['GET'])
def list_volume(type, sub_type):
    team_code = session['teamCode']
    return jsonify(status=True, message="success", list=server_image_list(type, sub_type, db_session, team_code))


@app.route('/vm/images/<type>', methods=['GET'])
def volume(type):
    team_code = session['teamCode']
    return jsonify(status=True, message="success", list=server_image(type, db_session, team_code))


@app.route('/vm/account/users/list', methods=['GET'])
def team():
    return jsonify(status=True, message="success", list=team_list(session['userId'],db_session))



@app.route('/vm/account/team', methods=['GET']) #팀 프로필
def my_list():
    team_owner = 'owner'
    return jsonify(status=True, message="success", list=teamwon_list(session['userId'],session['teamCode'],team_owner ,db_session))

@app.route('/vm/account/team/<code>', methods=['GET']) #시스템 팀 상세 프로필
def mydetail_list(code):
    team_owner = 'owner'
    team_code = code
    return jsonify(status=True, message="success", list=teamwon_list(session['userId'],team_code,team_owner ,db_session))

@app.route('/vm/account/won/<id>', methods=['GET'])
def teamwondetail_list(id,):
    user_id = id
    return jsonify(status=True, message="success", list=teamwoninfo_list(user_id, db_session))

@app.route('/vm/acoount/teamlist', methods=['GET'])
def tea_list():
    session_id = session['userId']
    team_id = session['teamCode']
    return jsonify(status=True, message="success", list=tea(session_id, team_id, db_session))


@app.route('/vm/container/services/<type>', methods=['GET'])
def container_list(type):
    return jsonify(status=True, message="success", list=container(type,session['teamCode'],db_session))

@app.route('/vm/container/services', methods=['GET'])
def containers_lit():
    return jsonify(status=True, message="success", list=containers(db_session))

@app.route('/vm/account/teamset',methods=['GET'])
def teamwon():
    team_code = session['teamCode']
    return jsonify(status=True, message="success", list=teamset(team_code, db_session))

@app.route('/vm/account/teamset/<code>',methods=['GET'])
def teamwon1(code):
    return jsonify(status=True, message="success", list=teamset(code, db_session))

@app.route('/vm/account/teamset/<id>/<code>',methods=['PUT'])
def approve(id,code):
    type = request.json['type']
    user_name = session['userName']
    approve_set(id, code, type, user_name, db_session)
    return jsonify(status=True, message="success")


@app.route('/vm/account/teamset/<id>/<code>',methods=['DELETE'])
def delete(id, code):
    team_delete(id, code)
    return jsonify(status=True, message="success")


@app.route('/vm/images/<type>', methods=['GET'])
def list_subtype_volume(type):
    team_code = request.json['team_code']
    return jsonify(status=True, message="success", list=server_image_list(type,"",db_session,team_code))


@app.route('/vm/machines/<id>/<type>', methods=['PUT'])
def update_guest_name(id, type):
    change_value = request.json['value']
    vm_update_info(id,type,change_value,db_session)
    return jsonify(status=True, message="success")


@app.route('/vm/account/selectteam', methods=['GET'])
def selectteam():
    return jsonify(status=True, message="success", list=select(db_session))


@app.route('/vm/account/selectteam', methods=['POST'])
def teamsignup():
    team_code = request.json['team_code']
    user_id = session['userId']
    signup_team(team_code, user_id)
    return jsonify(status=True, message="success")


@app.route('/vm/account/teamcomfirm', methods=['GET'])
def comfirm():
    user_id = session['userId']
    return jsonify(status=True, message="success", list=comfirm_list(user_id,db_session))


@app.route('/vm/account/createteam', methods=['POST'])
def createteam():
    user_id = session['userId']
    team_name = request.json['team_name']
    team_code = request.json['team_code']
    author_id = session['userName']
    session['teamCode']=team_code
    teamnamecheck=createteam_list(user_id, team_name, team_code, author_id, db_session)
    if(teamnamecheck=='success'):
        return jsonify(status=True, test='success')
    elif(teamnamecheck=='team_code'):
        return jsonify(status=True, test='id')
    elif(teamnamecheck=='team_name'):
        return jsonify(status=True, test='team')

@app.route('/vm/account/teamname', methods=['GET'])
def teamname():
    return jsonify(status=True, message="success", list=select_info(session['teamCode'],db_session))

@app.route('/vm/account/teamname/<code>', methods=['GET'])
def teamnamecode(code):
    return jsonify(status=True, message="success", list=select_info(code,db_session))

@app.route('/vm/account/teamname/', methods=['PUT'])
def changeteamname():
    team_name=request.json['team_name']
    return jsonify(status=True, message="success", list=select_put(team_name,session['teamCode']))

@app.route('/vm/account/teamname/<code>', methods=['PUT'])
def changeteamnamesystem(code):
    team_name=request.json['team_name']
    return jsonify(status=True, message="success", list=select_put(team_name,code))

@app.route('/vm/account/teamtable', methods=['GET'])
def teamshow():
    return jsonify(status=True, message="success", list=team_table(db_session))

@app.route('/vm/systems/path', methods=['GET'])
def systembase():
    return jsonify(status=True, message="success", list=pathimage(db_session))

@app.route('/vm/account/maketeam', methods=['POST'])
def maketeam():
    return jsonify(status=True, message="success")

@app.route('/vm/account/deleteteam/<code>', methods=['DELETE'])
def delteam(code):
    team_code = code
    hist= delteam_list(team_code,db_session)
    if(hist == 1):
        return jsonify(status=True, message="팀이 삭제 되었습니다")
    elif(hist ==2):
        return jsonify(status=False, message="인스턴스가 남아있어 팀을 삭제 할 수 없습니다")

@app.route('/vm/host',methods=['GET'])
def getHostMachines():
    return jsonify(status=True, message="success", info=hostMachineList(db_session))

# @app.route('/vm/host/',methods=['POST'])
# def approve(id,code):
#     endpoint = request.json['endpoint']
#     type = request.json['type']
#     node = request.json['node']
#
#     return jsonify(status=True, message="success", info=hostMachineList(db_session))

#### rest end ####


if __name__ == '__main__':
    app.run(port=8080)


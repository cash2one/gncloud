# -*- coding: utf-8 -*-

import os
import traceback

from datetime import timedelta
from flask import Flask, jsonify, request, session, escape, make_response

from Manager.db.database import db_session
from Manager.util.config import config
from Manager.util.json_encoder import AlchemyEncoder
from db.database import db_session
from service.service import *

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.json_encoder = AlchemyEncoder
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

#####common function start#####


@app.before_request
def before_request():
    if ('userId' not in session) and request.path != '/vm/logincheck' and request.path != '/vm/guestLogout' and request.path != '/vm/account' and (request.path!= 'vm/account/users' and request.method !='POST') and  request.path != '/vm/account/testtest':
        return make_response(jsonify(status=False),401)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
    if exception and db_session.is_active:
        db_session.rollback()

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
    name=""
    size_id=""
    image_id=""
    type = ""
    sub_type =""
    backup="false"
    team_code = session['teamCode']
    user_id = session['userId']
    if 'backup' in request.json:
        backup = request.json['backup']
    if 'vm_name' in request.json:
        name = request.json['vm_name']
    if 'size_id' in request.json:
        size_id = request.json['size_id']
    if 'id' in request.json:
        image_id = request.json['id']
    if 'sshkeys' in request.json:
        sshkeys = request.json['sshkeys']
    tag =request.json['tag']
    if 'type' in request.json:
        type =request.json['type']
    if 'password' in request.json:
        password = request.json['password']
    if 'sub_type' in request.json:
        sub_type = request.json['sub_type']
    if name !="":
        if type != "":
            if image_id !="":
                if size_id !="":
                    if type=="hyperv" and password != "" and sub_type=="base":
                        result = server_create(name,size_id, image_id, team_code, user_id, sshkeys, tag, type, password,backup ,db_session)
                        return jsonify(status=result["status"], value=result["value"])
                    elif type =="kvm" and sshkeys != "":
                        result = server_create(name, size_id, image_id, team_code, user_id, sshkeys, tag, type, password,backup, db_session)
                        return jsonify(status=result["status"], value=result["value"])
                    elif type =="docker":
                        result = server_create(name, size_id, image_id, team_code, user_id, sshkeys, tag, type, password,backup, db_session)
                        return jsonify(status=result["status"], value=result["value"])
                    elif type =="hyperv" and sub_type=="snap":
                        result = server_create(name, size_id, image_id, team_code, user_id, sshkeys, tag, type, password,backup, db_session)
                        return jsonify(status=result["status"], value=result["value"])
                    else:
                        return jsonify(status=True, value="password")
                else:
                    return jsonify(status=True, value="size_id")
            else:
                return jsonify(status=True, value="image_id")
        else:
            return jsonify(status=True, value="type")
    else:
        return jsonify(status=True, value="name")

@app.route('/vm/machine/snapshots', methods=['POST'])
def create_snapshots():
    team_code = session['teamCode']
    user_id = session['userId']
    name= request.json['vm_name']
    image_id = request.json['ord_id']
    type =request.json['type']
    result= server_create_snapshot(image_id, name, user_id, team_code, type, db_session)
    return jsonify(status=result["status"], ord_id=result["ord_id"], snap_id=result["snap_id"])

@app.route('/vm/machine', methods=['PUT'])
def change_status():
    id = request.json['id']
    status = request.json['status']
    list=server_change_status(id, status, db_session)
    if(list == True):
        return jsonify(status=True, message="success")
    else:
        return jsonify(status=False)

@app.route('/vm/machines', methods=['GET'])
def guest_list():
    team_code = session['teamCode']
    return jsonify(status=True, message="success", list=vm_list(db_session, team_code))

@app.route('/vm/snaplist', methods=['GET'])
def guest_list_snap():
    team_code = session['teamCode']
    return jsonify(status=True, message="success", list=vm_list_snap(db_session, team_code))

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
    if(user_info != None and user_info.GnUserTeam == None ):
        session['userId'] = user_info.GnUser.user_id
        session['userName'] = user_info.GnUser.user_name
        session['teamOwner'] = ""
        session['teamCode'] = ""
        session['teamCheck']="N"
        return jsonify(status=True, test='no')
    elif(user_info != None and user_info.GnUserTeam.comfirm == "Y"):
        session['userId'] = user_info.GnUser.user_id
        session['userName'] = user_info.GnUser.user_name
        session['teamCode'] = user_info.GnUserTeam.team_code
        session['teamOwner'] = user_info.GnUserTeam.team_owner
        session['teamCheck']=""
        return jsonify(status=True, test='yes')

    elif(user_info != None and user_info.GnUserTeam.comfirm == "N" ):
        session['userId'] = user_info.GnUser.user_id
        session['userName'] = user_info.GnUser.user_name
        session['teamOwner'] = ""
        session['teamCode'] = ""
        session['teamCheck']="Y"
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
    logout_info(session['userId'],session['teamCode'],db_session)
    session.clear()
    return jsonify(status=True, message="success")


@app.route('/vm/logincheck', methods=['GET'])
def logincheck():
    user_info = {"name":session['userName'],"user_id": session['userId'], "authority":session['teamOwner'], "team_code":session['teamCode'],"team_check":session['teamCheck']}
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

@app.route('/vm/account/teamset/<id>/<code>/<type>',methods=['PUT'])
def approve(id, code, type):
    user_name = session['userName']
    list= approve_set(id, code, type, user_name, db_session)
    if(list == 1):
        return jsonify(status=True, message="의 가입이 승인되었습니다.")
    elif(list == 2):
        return jsonify(status=True, message="이 관리자가 되었습니다.")
    elif(list == 3):
        return jsonify(status=True, message="의 비밀번호가 초기화 되었습니다.")
    elif(list == 4):
        return jsonify(status=True, message="이 팀원이 되었습니다.")
    else:
        return jsonify(status=True, message="의 변경할 것이 없습니다.")

@app.route('/vm/account/teamset/<id>/<code>',methods=['DELETE'])
def delete(id, code):
    team_delete(id, code)
    session['teamCheck']='N'
    return jsonify(status=True, message="을 탈퇴 시켰습니다.")


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
    lits=signup_team(team_code, user_id, db_session)
    if(lits==1):
        session['teamCheck'] ="Y"
        return jsonify(status=True)
    elif(lits==2):
        return jsonify(status=False)

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
    teamnamecheck=createteam_list(user_id, team_name, team_code, author_id, db_session)
    if(teamnamecheck=='success'):
        session['teamCode']=team_code
        session['teamOwner']="owner"
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
    team_cpu =request.json['cpu']
    team_memory = request.json['mem']
    team_disk = request.json['disk']
    list=select_putsys(team_name,code,team_cpu, team_memory, team_disk)
    if(list == 'True'):
        return jsonify(status=True, message="success")
    else:
        return jsonify(status=False)

@app.route('/vm/account/teamtable', methods=['GET'])
def teamshow():
    return jsonify(status=True, message="success", list=team_table(db_session))

@app.route('/vm/account/teamtable/<code>', methods=['GET'])
def teamshowlist(code):
    return jsonify(status=True, message="success", list=team_table_info(code, db_session))

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

@app.route('/vm/cluster',methods=['GET'])
def getHostMachines():
    return jsonify(status=True, message="success", info=hostMachineList(db_session))

@app.route('/vm/cluster/<id>',methods=['GET'])
def getHostMachineInfo(id):
    return jsonify(status=True, message="success", info=hostMachineInfo(id,db_session))

@app.route('/vm/images/<id>', methods=['PUT'])
def snapshotsdelete(id):
    id =id
    check = snapshot_delete(id, db_session)
    if(check == True):
        return jsonify(status=True)
    else:
        return jsonify(status=False)
@app.route('/vm/cluster/node/<id>',methods=['DELETE'])
def removeHostMachine(id):
    deleteHostMachine(id,db_session)
    return jsonify(status=True, message="success")

@app.route('/vm/cluster',methods=['POST'])
def saveCluster():
    ip = request.json['ip']

    if 'id' in request.json:
        updateClusterInfo(request.json['id'],ip,db_session)
    else:
        type = request.json['type']
        insertClusterInfo(type,ip,db_session)

    return jsonify(status=True, message="success")

@app.route('/vm/host',methods=['POST'])
def saveHostMachine():
    cpu = request.json['cpu']
    mem = request.json['mem']
    disk = request.json['disk']
    ip = request.json['ip']
    type = request.json['type']
    disk_size = request.json['disk_size']
    mem_size = request.json['mem_size']
    insertHostInfo(ip,cpu,mem,mem_size,disk,disk_size,type,db_session)
    return jsonify(status=True, message="success")


@app.route('/vm/cluster/<id>',methods=['DELETE'])
def removeCluster(id):
    deleteCluster(id,db_session);
    return jsonify(status=True, message="success")


@app.route('/vm/image/<id>',methods=['DELETE'])
def deleteBaseImage(id):
    deleteImageInfo(id, db_session)
    return jsonify(status=True, message="success")

@app.route('/vm/image/<id>',methods=['GET'])
def getBaseImage(id):
    return jsonify(status=True, message="success",info=selectImageInfo(id, db_session))

@app.route('/vm/image/file',methods=['POST'])
def saveBaseImageImportFile():
    file = request.files['file']
    if file and allowed_file(file.filename):
        icon = secure_filename(file.filename)
        file.save(os.path.join(config.IMAGE_PATH, icon))

    type = request.form['type']
    os_name = request.form['os']
    os_ver = request.form['os_ver']
    os_bit = request.form['os_bit']
    filename = request.form['filename']

    if 'id' in request.form:
        updateImageInfo(request.form['id'],type,os_name,os_ver,os_bit,filename,icon,db_session)
    else:
        insertImageInfo(type,os_name,os_ver,os_bit,filename, icon, db_session)


    return jsonify(status=True, message="success")

@app.route('/vm/createsize', methods=['GET'])
def createsize():
    return jsonify(status=True, list=create_size(db_session))

@app.route('/vm/image',methods=['POST'])
def saveBaseImageExceptFile():
    type = request.json['type']
    os_name = request.json['os']
    os_ver = request.json['os_ver']
    os_bit = request.json['os_bit']
    filename = request.json['filename']

    if 'id' in request.json:
        updateImageInfo(request.json['id'],type,os_name,os_ver,os_bit,filename,"",db_session)
    else:
        insertImageInfo(type,os_name,os_ver,os_bit,filename, "", db_session)

    return jsonify(status=True, message="success")


@app.route('/vm/dockerimage/<id>',methods=['GET'])
def getBaseImageDocker(id):
    return jsonify(status=True, message="success",info=selectImageInfoDocker(id, db_session))

@app.route('/vm/dockerimage/file',methods=['POST'])
def saveBaseImageImportFileDocker():
    file = request.files['file']
    if file and allowed_file(file.filename):
        icon = secure_filename(file.filename)
        file.save(os.path.join(config.IMAGE_PATH, icon))

    name = request.form['view_name']
    os_ver = request.form['os_ver']
    tag = request.form['tag']
    port = request.form['port']
    env = request.form['env']
    vol = request.form['vol']

    if 'id' in request.form:
        updateImageInfoDocker(request.form['id'],name,os_ver,tag,icon,port,env,vol,db_session)
    else:
        insertImageInfoDocker(name,os_ver,tag,icon,port,env,vol,db_session)

    return jsonify(status=True, message="success")

@app.route('/vm/dockerimage',methods=['POST'])
def saveBaseImageExceptFileDocker():
    name = request.json['view_name']
    os_ver = request.json['os_ver']
    tag = request.json['tag']
    port = request.json['port']
    env = request.json['env']
    vol = request.json['vol']

    if 'id' in request.json:
        updateImageInfoDocker(request.json['id'],name,os_ver,tag,"",port,env,vol,db_session)
    else:
        insertImageInfoDocker(name,os_ver,tag,"",port,env,vol,db_session)

    return jsonify(status=True, message="success")

@app.route('/vm/price',methods=['GET']) #시스템 > 리소스 단위 관리
def Price_info():
    return jsonify(status=True, message="success", list=price_list(db_session))

@app.route('/vm/price',methods=['POST']) #시스템 > 리소스 단위 관리 입력
def Price_info_put():
    cpu = request.json['cpu']
    mem = request.json['mem']
    disk = request.json['disk']
    price = request.json['won']
    price_hour = request.json['won_hour']
    disk_size = request.json['disk_size']
    mem_size = request.json['mem_size']
    return jsonify(status=True, message="success", list=price_put(cpu,mem,disk,price,disk_size,mem_size,price_hour,db_session))

@app.route('/vm/price/<id>', methods=['DELETE'])
def price_info_delete(id):
    return jsonify(status=True, message="success", list=price_del(id,db_session))

@app.route('/vm/dockerimage/<id>',methods=['DELETE'])
def deleteBaseImageDocker(id):
    deleteImageInfoDocker(id, db_session)
    return jsonify(status=True, message="success")

@app.route('/vm/snapshot/list/<id>',methods=['GET']) #스냅샷 모달창
def snaplistinfo(id):
    return jsonify(status=True, message="success", list=snap_list_info(id, db_session))

@app.route('/vm/loginhist', methods=['GET']) #login hist
def login_hist():
    page= request.args.get("page")
    return jsonify(status=True, message="success", list=login_history(page,db_session))

@app.route('/vm/backup/<id>', methods=['PUT'])
def backup_change(id):
    backup=['backup']
    return jsonify(status=True, list=backupchnage(id, backup, db_session))

@app.route('/vm/money',methods=['GET'])
def setting():
    return jsonify(status=True, list=setting_list(db_session))

@app.route('/vm/money/monitor',methods=['PUT'])
def monitoring_time():
    monitor_period =request.json['monitor_period']
    return jsonify(status=True, list=monitoring_time_change(monitor_period,db_session))

@app.route('/vm/day',methods=['PUT'])
def billing_time():
    billing = request.json['bills']
    return jsonify(status=True, list=billing_time_change(billing,db_session))

@app.route('/vm/backup', methods=['PUT'])
def backup_time():
    type = request.json['type']
    day= request.json['value']
    return jsonify(status=True, list=backup_time_change(type, day, db_session))
@app.route('/vm/notice', methods=['GET'])
def Notice():
    page= request.args.get("page")
    return jsonify(status=True, list=notice_list(page,db_session))

@app.route('/vm/notice/<id>', methods=['GET'])
def Notice_info(id):
    return jsonify(status=True, list=notice_info(id,db_session))

@app.route('/vm/notice',methods=['POST'])
def Notice_create():
    title=request.json['title']
    text = request.json['text']
    return jsonify(status=True, list=notice_create(title,text,db_session))

@app.route('/vm/notice',methods=['PUT'])
def Notice_change():
    id = request.json['id']
    text = request.json['text1']
    return jsonify(status=True, list=notice_change(id,text,db_session))

@app.route('/vm/notice/<id>',methods=['DELETE'])
def Notice_delete(id):
    return jsonify(status=True, list=notice_delete(id,db_session))

def secure_filename(filename):
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S') +"."+ filename.rsplit('.', 1)[1]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


#### rest end ####


if __name__ == '__main__':
    app.run(port=8080)


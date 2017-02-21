angular
    .module('gncloud')
    .controller('guestTeamWonCtrl', function ($scope, $http, dateModifyService, $rootScope, notification) {
        $scope.team_profile=function(){
            $http({
                method: 'GET',
                url: '/api/manager/vm/account/teamname',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.teamname = data.list; //유저팀에 대한 정보

                    } else {
                        if(data.message != null) {
                            notification.sendMessage("error",data.message);
                        }
                    }

                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.team_profile();
        $scope.teamwon_list={};
        $scope.infolist=function(id){
            $http({
                method: 'GET',
                url: '/api/manager/vm/account/won/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        var teamwonArr = new Array();
                        data.list[0][0].approve_date = data.list[0][1].approve_date;
                        data.list[0][0].apply_date = data.list[0][1].apply_date;
                        if(data.list[0][1].comfirm == 'Y'){
                            var confirm_re = '승인';
                        } else {
                            var confirm_re = '대기';
                        }//승인 한글화
                        if(data.list[0][1].team_owner == 'owner') {
                            var team_owner = '관리자';
                        }else {
                            var team_owner='팀원';
                        }
                        data.list[0][0].team_owner = team_owner;
                        data.list[0][0].confirm = confirm_re;
                        teamwonArr.push(data.list[0][0]);
                        $scope.teamwon_list = teamwonArr;

                    } else {
                        if(data.message != null) {
                            notification.sendMessage("error",data.message);
                        }
                    }

                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.teamtable=function(){
            $scope.won_list ={};
            $http({
                method: 'GET',
                url: '/api/manager/vm/account/teamset',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        var teamArr = new Array();
                        for(var i = 0 ; i < data.list.length ; i++) {
                            if(data.list[i][1].comfirm == 'Y'){
                                var comfirm_re = '승인';
                            } else {
                                var comfirm_re = '대기';
                            }//승인 한글화
                            if(data.list[i][1].team_owner == 'owner') {
                                var team_owner = '관리자';
                            }else {
                                var team_owner='팀원';
                            }
                            if(data.list[i][0].user_id == $rootScope.user_info.user_id){
                                data.list[i][0].user_name = data.list[i][0].user_name+"\n(YOU)";
                                data.list[i][0].set= 1;
                            }else{
                                data.list[i][0].sett=0;
                            }
                            data.list[i].user_id = data.list[i][0].user_id;
                            data.list[i].user_name = data.list[i][0].user_name;
                            data.list[i].team_code = data.list[i][1].team_code;
                            data.list[i].tel = data.list[i][0].tel;
                            data.list[i].email = data.list[i][0].email;
                            data.list[i].comf = comfirm_re;
                            data.list[i].team_owner = team_owner;
                            data.list[i].team_check = data.list[i][1].comfirm;
                            data.list[i].sett = data.list[i][0].sett;
                            //날짜 카운팅
                            teamArr.push(data.list[i])
                        }
                        $scope.won_list=teamArr;
                        $scope.won_list.total = data.list.length;
                    }else{
                        notification.sendMessage("error",data.message);
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.teamtable();
        $scope.lits={};
        $scope.update = function (id, code, action, name, owner) {  //팀장이 팀원 등급권한
            var url = '/api/manager/vm/account/teamset/'+id+'/'+code+'/'+action;
            var method = "PUT";
            $scope.lits.type=action;
            if (action == "dropout") {
                var returnvalue = confirm(name+"을 탈퇴시키겠습니까 ?");
                if (returnvalue == true){
                    $http({
                        method:'DELETE',
                        url:'/api/manager/vm/account/teamset/'+id+'/'+code,
                        headers: {'Content-Type': 'application/json; charset=utf-8'}
                    })
                        .success(function(data, status, headers, config) {
                            if (data.status == true) {
                                notification.sendMessage("success",name + data.message);
                                $scope.teamtable();
                            } else {
                                //alert(data.message);
                            }
                        })
                        .error(function(data, status, headers, config) {
                            console.log(status);
                        });
                }else{

                }

            }else if(action == "approve"){
                var returnvalue = confirm(name + "의 가입을 승인하시겠습니까 ?");
                if(returnvalue==true){
                    $http({
                        method: method,
                        url: url,
                        headers: {'Content-Type': 'application/json; charset=utf-8'}
                    })
                        .success(function(data, status, headers, config) {
                            if (data.status == true) {
                                notification.sendMessage("success",name + data.message);
                                $scope.teamtable();
                            } else {
                                //alert(data.message);
                            }
                        })
                        .error(function(data, status, headers, config) {
                            console.log(status);
                        });
                }
            }else if(action == 'change'){
                if(owner == '관리자'){
                    var retrunvalue = confirm(name+"을 팀원으로 변경하시겠습니까 ?");
                }else{
                    var retrunvalue = confirm(name+"을 관리자로 변경하시겠습니까 ?");
                }

                if(retrunvalue == true){
                    $http({
                        method: method,
                        url: url,
                        headers: {'Content-Type': 'application/json; charset=utf-8'}
                    })
                        .success(function(data, status, headers, config) {
                            if (data.status == true) {
                                notification.sendMessage("success",name + data.message);
                                $scope.teamtable();
                            } else {
                                //alert(data.message);
                            }
                        })
                        .error(function(data, status, headers, config) {
                            console.log(status);
                        });
                }
            }else if(action == "reset"){
                var retrunvalue = confirm(name+"의 비밀번호를 초기화 시키겠습니까 ?");
                if(retrunvalue == true){
                    $http({
                        method: method,
                        url: url,
                        headers: {'Content-Type': 'application/json; charset=utf-8'}
                    })
                        .success(function(data, status, headers, config) {
                            if (data.status == true) {
                                notification.sendMessage("success",name + data.message);
                                $scope.teamtable();
                            } else {
                                //alert(data.message);
                            }
                        })
                        .error(function(data, status, headers, config) {
                            console.log(status);
                        });
                }
            }



        };

        $scope.user_info = $rootScope.user_info;

        $rootScope.$on('init', function () {
            $scope.user_info = $rootScope.user_info;
        });
    });
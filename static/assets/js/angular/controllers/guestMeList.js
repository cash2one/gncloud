angular
    .module('gncloud')
    .controller('guestMeListCtrl', function ($scope, $http, dateModifyService) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $("#key-sett").hide();
        $("#profile-team").hide();
        $("#team-reso").hide();
        $("#team-group").hide();
        $("#profile-system").hide();
        $("#team-sett").hide();
        $("#cluster-sett").hide();
        $("#image-sett").hide();
        $http({
            method: 'GET',
            url: '/api/manager/vm/account/users/list',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.te_list = data.list; // 유저 부분 리스트

                } else {
                    alert(data.message);
                }

            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $http({
            method: 'GET',
            url: '/api/manager/vm/account/teamname',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.teamname = data.list; //유저팀에 대한 정보

                } else {
                    alert(data.message);
                }

            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.team_list = {};
        $http({
            method: 'GET',
            url: '/api/manager/vm/account/team',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.team_list = data.list; // 팀원들에 대한 정보

                } else {
                    alert(data.message);
                }

            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

        $http({
            method: 'GET',
            url: '/api/kvm/account/keys',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {
                    $scope.data_list = data.list; //ssh키에 대한 정보
                }
                else {
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.path={};
        $http({
            method: 'GET',
            url: '/api/manager/vm/systems/path',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {

                    var imageArr = new Array();
                    for (var i = 0; i < data.list.length; i++) {
                        var path = data.list[i][0].image_path;
                        data.list[i][1].image_path = path;
                        data.list[i][1].create_time_diff = dateModifyService.modifyDate(data.list[i][1].create_time);
                        imageArr.push(data.list[i][1]);
                    }

                    $scope.paths = imageArr; //이미지 관리 리스트
                }
                else {
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.won_list ={};
        $http({
            method: 'GET',
            url: '/api/manager/vm/account/teamset',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.won_list = data.list; //팀장 팀원에 대한 정보
                    $scope.won_list[0][0].total = data.list.length;
                    for(var i = 0 ; i < data.list.length ; i++) {
                        $scope.won_list[i][1].comf = data.list[i][1].comfirm;
                        if($scope.won_list[i][1].comf == 'Y'){
                           var comfirm_re = '승인'
                        } else {
                           var comfirm_re = '비승인'
                        }//승인 한글화
                        $scope.won_list[i][1].comf = comfirm_re;
                        //날짜 카운팅
                        $scope.won_list[i][1].create_time_diff = dateModifyService.modifyDate(data.list[i][1].apply_date);
                        $scope.won_list[i][1].create_time_diff1 = dateModifyService.modifyDate(data.list[i][1].approve_date);
                    }
                } else {
                    alert(data.message);
                }

            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.table={};
        $http({
            method: 'GET',
            url: '/api/manager/vm/account/teamtable',
            headers: {'Content-Type': 'application/json; charset=utf-8'} //시스템 관리자의 팀관리
        })
            .success(function (data, status, headers, config) {
                if (data) {

                    var newArr = new Array();
                    for (var i = 0; i < data.list.length; i++) {
                        data.list[i].team_info.create_time_diff = dateModifyService.modifyDate(data.list[i].team_info.create_date); // 날짜 설정
                        for (var j = 0; j < data.list[i].user_list.length; j++) {
                            if (data.list[i].user_list[j][0].team_owner == 'owner') { //팀장찾는 곳
                                var owner_id = data.list[i].user_list[j][1].user_id;
                                var owner_name = data.list[i].user_list[j][1].user_name;

                            } // user 부분 태그 필요
                            //else{
                            //    var user_id = data.list[i].user_list[j][1].user_id;
                            //    var user_name = data.list[i].user_list[j][1].user_name;
                            //}
                            data.list[i].team_info.owner_id = owner_id;
                            data.list[i].team_info.owner_name = owner_name;
                        }
                        newArr.push(data.list[i].team_info);
                    }

                    $scope.table = newArr;


                }
                else {
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $http({
            method: 'GET',
            url: '/api/manager/vm/container/services',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {
                    for (var i = 0; i < data.list.length; i++) {
                        data.list[i].create_time_diff = dateModifyService.modifyDate(data.list[i].create_time);//날짜변경
                    }
                    $scope.contain_list = data.list;
                }
                else {
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.submit = function() {
            $http({
                method  : 'PUT',
                url: '/api/manager/vm/account/users/list',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8' // 개인설정 비밀번호 변경등
                }
            })
                .success(function(data) {
                    if (data.status == 2) {
                        alert("success");

                    }
                    else if(data.status == 1){
                        alert("비밀번호가 틀렸습니다");
                    }
                    else {
                        alert(data.message)
                    }
                });
        };
        $scope.actions = [
            {name: '승인', type: 'approve'},
            {name: '등급변경', type: 'change'},
            {name: '비밀번호초기화', type: 'reset'},
            {name: '팀탈퇴', type: 'dropout'}
        ];
        $scope.data={};
        $scope.update = function (id, code, action) {  //팀장이 팀원 등급권한
            var url = '/api/manager/vm/account/teamset/'+id+'/'+code;
            var method = "PUT";
            if (action.type == "dropout") {
                url = '/api/manager/vm/account/teamset/'+id+'/'+code;
                method = 'DELETE';
            }

            $http({
                method: method,
                url: url,
                data: action,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        alert(name + " guest의 상태가 변경되었습니다");
                    } else {
                        alert(data.message);
                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });

            };
        $scope.change = function () { //팀이름 변경
            $http({
                method  : 'PUT',
                url: '/api/manager/vm/account/teamname',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                }
            })
                .success(function(data) {
                    if (data.status == true) {
                        alert("변경되었습니다")
                    }
                    else {
                        alert(data.message)
                    }
                });
        }
        $scope.download = function (id) { //ssh키의 다운로드
            $http({
                method: 'GET',
                url: "/api/kvm/account/keys/download/"+id,
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8',
                }
            })
                .success(function (data, status, headers, config) {
                    var header = headers(); // We set Content-disposition with filename in Controller.
                    var fileName = header['content-disposition'].split("=")[1].replace(/\"/gi,'');
                    var blob = new Blob([data],
                        {type : 'application/octet-stream;charset=UTF-8'});
                    var objectUrl = (window.URL || window.webkitURL).createObjectURL(blob);
                    var link = angular.element('<a/>');
                    link.attr({
                        href : objectUrl,
                        download : "sshkey"
                    })[0].click();
                });
        };
        $scope.click =function(ty){
            if(ty == 'profile'){
                $("#profile").fadeIn();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").hide();
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
            }
            else if(ty == 'key-sett'){
                $("#profile").hide();
                $("#key-sett").fadeIn();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").hide();
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
            }
            else if(ty == 'profile-team'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").fadeIn();
                $("#team-reso").hide();
                $("#team-group").hide();
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
            }
            else if(ty == 'team-reso'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").fadeIn();
                $("#team-group").hide();
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
            }
            else if(ty == 'team-group'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").fadeIn();
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
            }
            else if(ty == 'profile-system'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").hide();
                $("#profile-system").fadeIn();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
            }
            else if(ty == 'team-sett'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").fadeIn();
                $("#team-group").hide();
                $("#profile-system").hide();
                $("#team-sett").fadeIn();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
            }
            else if(ty == 'cluster-sett'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").hide();
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").fadeIn();
                $("#image-sett").hide();
            }
            else if(ty == 'image-sett'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").hide();
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").fadeIn();
                $("#container").hide();
            }
        }
        $scope.imageset = function(ty){
            if(ty == 'container'){
                $("#machine").hide();
                $("#container").fadeIn();
            }
            else if(ty == 'machine'){
                $("#container").hide();
                $("#machine").fadeIn();
            }
        }
        });
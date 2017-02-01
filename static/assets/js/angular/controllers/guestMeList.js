angular
    .module('gncloud')
    .controller('guestMeListCtrl', function ($scope, $http, dateModifyService, $rootScope) {

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
        $("#price").hide();
        $scope.close=function () {
            $(':input').val('');
        }
        $scope.profile=function(){
            $http({
                method: 'GET',
                url: '/api/manager/vm/account/users/list',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.te_list = data.list; // 유저 부분 리스트

                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }

                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.profile();
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
                            alert(data.message)
                        }
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
                        var newArr = new Array();
                        var team_code="";

                        for(var i = 0 ; i < data.list.list.length ; i++) {
                            data.list.list[i].user_id = data.list.list[i][0].user_name;
                            newArr.push(data.list.list[i]);
                        }

                        $scope.team_list = newArr; // 팀원들에 대한 정보
                        $scope.team_list.total = data.list.info

                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }

                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }


        $scope.sshkey=function(){
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
        }

        $scope.sshkey_save=function(){
            $http({
                method: 'POST',
                url: '/api/kvm/account/keys',
                data:'{"name":"'+$("#sshkey_name").val()+'"}',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.sshkey();
                        $(':input').val('');
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
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
                        teamwonArr.push(data.list[0][0]);
                        $scope.teamwon_list = teamwonArr;

                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }

                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.teamtable=function(){
            //$http({
            //    method: 'GET',
            //    url: '/api/manager/vm/logincheck',
            //    headers: {'Content-Type': 'application/json; charset=utf-8'}
            //})
            //    .success(function (data, status, headers, config) {
            //        $rootScope.user_info = data.info;
            //        $rootScope.$emit('init');
            //    })
            //    .error(function (data, status, headers, config) {
            //        console.log("checking success!!");
            //    });
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
                        alert("error");
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

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
                        alert("변경되었습니다.");
                        $scope.profile();
                        $(':input').val('');
                    }
                    else if(data.status == 1){
                        alert("비밀번호가 틀렸습니다");
                    }
                    else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }
                });
        };
        $scope.lits={};
        $scope.update = function (id, code, action, name) {  //팀장이 팀원 등급권한
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
                                alert(name + data.message);
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
                                alert(name + data.message);
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
                var retrunvalue = confirm(name+"을 관리자로 변경하시겠습니까 ?");
                if(retrunvalue == true){
                    $http({
                        method: method,
                        url: url,
                        headers: {'Content-Type': 'application/json; charset=utf-8'}
                    })
                        .success(function(data, status, headers, config) {
                            if (data.status == true) {
                                alert(name + data.message);
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
                if(returnvalue == true){
                    $http({
                        method: method,
                        url: url,
                        headers: {'Content-Type': 'application/json; charset=utf-8'}
                    })
                        .success(function(data, status, headers, config) {
                            if (data.status == true) {
                                alert(name + data.message);
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
                        alert("변경되었습니다");
                        $scope.team_profile();
                        $(':input').val('');
                    }
                    else {
                        if(data.message != null) {
                            alert(data.message)
                        }
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
        $scope.sshkey_delete = function (id,index) { //ssh키의 다운로드
            $http({
                method: 'DELETE',
                url: "/api/kvm//account/keys/"+id,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8',
                }
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        alert(name + "상태가 변경되었습니다");
                        $scope.data_list.splice(index, 1);
                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }
                });
        };
        $scope.click =function(ty){
            if(ty == 'profile'){
                $("#profile").fadeIn();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").hide();
                $("#price").hide();

            }
            else if(ty == 'key-sett'){
                $("#profile").hide();
                $("#key-sett").fadeIn();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").hide();
                $("#price").hide();
                $scope.sshkey();
            }
            else if(ty == 'profile-team'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").fadeIn();
                $("#team-reso").hide();
                $("#team-group").hide();
                $("#price").hide();
                $scope.team_profile();

            }
            else if(ty == 'team-reso'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").fadeIn();
                $("#team-group").hide();
                $("#price").hide();
                $scope.reso();

            }
            else if(ty == 'team-group'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").fadeIn();
                $("#price").hide();
                $scope.teamtable();

            }else if(ty == 'price'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").hide();
                $("#price").fadeIn();
                $scope.price();
            }

        }

        $scope.reso = function(){
            //**********리소스*************//
            $http({
                method: 'GET',
                url: '/api/manager/useinfo',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        new Chart(document.getElementById("cpu_chart").getContext("2d"), $scope.getConfig(data.list.cpu_per, "cpu"));
                        new Chart(document.getElementById("memory_chart").getContext("2d"), $scope.getConfig(data.list.mem_per, "mem"));
                        new Chart(document.getElementById("disk_chart").getContext("2d"), $scope.getConfig(data.list.disk_per, "disk"));

                        $("#cpu_per").html(data.list.cpu_per[0]);
                        $("#cpu_use_cnt").html(data.list.cpu_cnt[0]);
                        $("#cpu_total_cnt").html(data.list.cpu_cnt[1]);
                        $("#mem_per").html(data.list.mem_per[0]);
                        $("#mem_use_cnt").html(data.list.mem_cnt[0]);
                        $("#mem_total_cnt").html(data.list.mem_cnt[1]);
                        $("#disk_per").html(data.list.disk_per[0]);
                        $("#disk_use_cnt").html(data.list.disk_cnt[0]);
                        $("#disk_total_cnt").html(data.list.disk_cnt[1]);
                    }
                    else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });

            $scope.getConfig = function (data, type) {
                var config = null;
                var rgb1 = null;
                var rgb2 = "rgb(204, 204, 204)";
                if(type == 'cpu'){
                    rgb1 = "rgb(255, 167, 22)"
                }else if(type == 'mem'){
                    rgb1 = "rgb(83, 200, 173)"
                }else if(type == 'disk'){
                    rgb1 = "rgb(87, 161, 246)"
                }


                if (type == 'cpu' || type == 'mem' || type == 'disk' ) {
                    config = {
                        type: 'doughnut',
                        data: {
                            datasets: [{
                                data: data,
                                backgroundColor: [
                                    rgb1,
                                    rgb2
                                ],
                            }],
                            labels: [
                                "사용중",
                                "미사용"
                            ]
                        },
                        options: {
                            responsive: true,
                            legend: true
                        }
                    }
                }
                return config;
            }
        }
        $scope.price=function () {
            $http({
                method: 'GET',
                url: '/api/manager/price',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.price =data.list;
                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }
                });
        }
        $scope.price_list_info=function (year, month, team_code) {
            $scope.data={};
            $scope.data.year = year;
            $scope.data.month = month;
            $scope.data.team_code = team_code;
            $http({
                method: 'GET',
                url: '/api/manager/price/list',
                params:$scope.data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.price_list =data.list.list;
                        $scope.price_invoice = data.list.instance;

                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }
                });
        }
        $scope.user_info = $rootScope.user_info;

        $rootScope.$on('init', function () {
            $scope.user_info = $rootScope.user_info;
        });
        $scope.refresh = function(){
            $scope.won_list = Array.prototype.slice.call($scope.won_list).reverse();
        }
    }).directive('tooltip', function(){
        return {
            restrict: 'A',
            link: function(scope, element, attrs){
                $(element).hover(function(){
                    $(element).tooltip('show');
                }, function(){
                    $(element).tooltip('hide');
                });
            }
        };




    });
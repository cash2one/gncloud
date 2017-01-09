angular
    .module('gncloud')
    .controller('guestTeamDetailCtrl', function ($scope, $http, $routeParams, dateModifyService) {
        $scope.profile=function(){
        $http({
            method: 'GET',
            url: '/api/manager/vm/account/teamname/'+$routeParams.code,
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

            $http({
                method: 'GET',
                url: '/api/manager/vm/account/team/'+$routeParams.code,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        var newArr = new Array();
                        for(var i = 0 ; i < data.list.list.length ; i++) {
                            data.list.list[i].user_id = data.list.list[i][0].user_name;
                            newArr.push(data.list.list[i]);
                        }

                        $scope.team_list = newArr; // 팀원들에 대한 정보
                        $scope.team_list.total = data.list.info

                    } else {
                        alert(data.message);
                    }

                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.profile();

        $scope.teamtable=function() {
            $scope.won_list = {};
            $http({
                method: 'GET',
                url: '/api/manager/vm/account/teamset/' + $routeParams.code,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        var teamArr = new Array();
                        for (var i = 0; i < data.list.length; i++) {
                            if (data.list[i][1].comfirm == 'Y') {
                                var comfirm_re = '승인';
                            } else {
                                var comfirm_re = '대기';
                            }//승인 한글화
                            if (data.list[i][1].team_owner == 'owner') {
                                var team_owner = '팀장';
                            } else {
                                var team_owner = '팀원';
                            }
                            data.list[i].user_id = data.list[i][0].user_id;
                            data.list[i].user_name = data.list[i][0].user_name;
                            data.list[i].tel = data.list[i][0].tel;
                            data.list[i].email = data.list[i][0].email;
                            data.list[i].team_check = data.list[i][1].comfirm;
                            data.list[i].apply_date = data.list[i][1].apply_date;
                            data.list[i].approve_date = data.list[i][1].approve_date;
                            data.list[i].comf = comfirm_re;
                            data.list[i].team_owner = team_owner;
                            //날짜 카운팅
                            data.list[i].create_time_diff = dateModifyService.modifyDate(data.list[i][1].apply_date);
                            data.list[i].create_time_diff1 = dateModifyService.modifyDate(data.list[i][1].approve_date);
                            teamArr.push(data.list[i])
                        }
                        $scope.won_list = teamArr;
                        $scope.won_list.total = data.list.length;
                    } else {
                        alert("error");
                    }
                });
        }
        $scope.teamtable();
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
                        alert("변경되었습니다");
                        $scope.teamtable();
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
                url: '/api/manager/vm/account/teamname/'+$routeParams.code,
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                }
            })
                .success(function(data) {
                    if (data.status == true) {
                        alert("변경되었습니다")
                        $scope.profile();
                    }
                    else {
                        alert(data.message)
                    }
                });
        }


        //**********리소스*************//
        $http({
            method: 'GET',
            url: '/api/manager/useinfo/'+$routeParams.code,
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
                    alert(data.message)
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.delete=function(){
            $http({
                method: 'DELETE',
                url:'/api/manager/vm/account/deleteteam/'+$routeParams.code,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        alert(data.message);
                        location.href="#/guestSystemList?id=team-sett";
                    } else {
                        alert(data.message);
                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });

        };
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
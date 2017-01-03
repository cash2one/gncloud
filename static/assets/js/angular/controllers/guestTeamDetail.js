angular
    .module('gncloud')
    .controller('guestTeamDetailCtrl', function ($scope, $http, $routeParams, dateModifyService) {

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
                    $scope.team_list = data.list; // 팀원들에 대한 정보

                } else {
                    alert(data.message);
                }

            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.won_list ={};
        $http({
            method: 'GET',
            url: '/api/manager/vm/account/teamset/'+$routeParams.code,
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
                        alert(name + "삭제되었습니다");
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

    });
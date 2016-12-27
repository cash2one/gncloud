angular
    .module('gncloud')
    .controller('guestTeamDetailCtrl', function ($scope, $http, dateModifyService) {

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
            url: '/api/manager/useinfo',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    new Chart(document.getElementById("cpu_chart").getContext("2d"), $scope.getConfig(data.list.cpu_per, "quota"));
                    new Chart(document.getElementById("memory_chart").getContext("2d"), $scope.getConfig(data.list.mem_per, "quota"));
                    new Chart(document.getElementById("disk_chart").getContext("2d"), $scope.getConfig(data.list.disk_per, "quota"));

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

        $scope.getConfig = function (data, type) {
            var config = null;
            if (type == 'quota') {
                config = {
                    type: 'doughnut',
                    data: {
                        datasets: [{
                            data: data,
                            backgroundColor: [
                                "rgb(233, 30, 99)",
                                "rgb(204, 204, 204)"
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
            }else if (type == 'status') {
                config = {
                    type: 'pie',
                    data: {
                        datasets: [{
                            data: data,
                            backgroundColor: [
                                "rgb(233, 30, 99)",
                                "rgb(255, 193, 7)"
                            ],
                        }],
                        labels: [
                            "실행",
                            "정지"
                        ]
                    },
                    options: {
                        responsive: true,
                        legend: true
                    }
                }
            }else if (type == 'type') {
                config = {
                    type: 'pie',
                    data: {
                        datasets: [{
                            data: data,
                            backgroundColor: [
                                "rgb(233, 30, 99)",
                                "rgb(255, 193, 7)"
                            ],
                        }],
                        labels: [
                            "kvm",
                            "hiperv"
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
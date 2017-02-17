angular
    .module('gncloud')
    .controller('guestTeamListCtrl', function ($scope, $http, $routeParams, dateModifyService) {
        $scope.table = {};
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

                            var owner_id = "";
                            var owner_name = "";
                            var users = "";
                            var usersfirst = "";
                            var usersfirstid = "";
                            for (var j = 0; j < data.list[i].user_list.length; j++) {
                                if (data.list[i].user_list[j][0].team_owner == 'owner') { //팀장찾는 곳
                                    owner_name = data.list[i].user_list[j][1].user_name;

                                } else {
                                    users += data.list[i].user_list[j][1].user_name + "/";
                                }

                            }

                            data.list[i].team_info.userslen = data.list[i].user_list.length > 0 ? (data.list[i].user_list.length - 1) : 0;
                            data.list[i].team_info.usersfirstid = usersfirstid;
                            data.list[i].team_info.usersfirst = usersfirst;
                            data.list[i].team_info.users = users;
                            data.list[i].team_info.owner_id = owner_id;
                            data.list[i].team_info.owner_name = owner_name;
                            data.list[i].team_info.cpu_use_per = data.list[i].quto_info.cpu_per[0];
                            data.list[i].team_info.cpu_use_cnt = data.list[i].quto_info.cpu_cnt[0];
                            data.list[i].team_info.cpu_tot_cnt = data.list[i].quto_info.cpu_cnt[1];
                            data.list[i].team_info.mem_use_per = data.list[i].quto_info.mem_per[0];
                            data.list[i].team_info.mem_use_cnt = data.list[i].quto_info.mem_cnt[0];
                            data.list[i].team_info.mem_tot_cnt = data.list[i].quto_info.mem_cnt[1];
                            data.list[i].team_info.disk_use_per = data.list[i].quto_info.disk_per[0];
                            data.list[i].team_info.disk_use_cnt = data.list[i].quto_info.disk_cnt[0];
                            data.list[i].team_info.disk_tot_cnt = data.list[i].quto_info.disk_cnt[1];
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
        $scope.diskusage = function (code) {
            $http({
                method: 'GET',
                url: '/api/manager/vm/account/teamtable/' + code,
                headers: {'Content-Type': 'application/json; charset=utf-8'} //시스템 관리자의 팀관리
            })
                .success(function (data, status, headers, config) {
                    if (data) {

                        data.list[0].team_info.create_time_diff = dateModifyService.modifyDate(data.list[0].team_info.create_date); // 날짜 설정
                        var owner_id = "";
                        var owner_name = "";
                        var users = "";
                        var usersfirst = "";
                        var usersfirstid = "";
                        for (var j = 0; j < data.list[0].user_list.length; j++) {
                            if (data.list[0].user_list[j][0].team_owner == 'owner') { //팀장찾는 곳
                                owner_name = data.list[0].user_list[j][1].user_name;

                            } else {
                                users += data.list[0].user_list[j][1].user_name + '/';
                            }
                            data.list[0].team_info.userslen = data.list[0].user_list.length > 0 ? (data.list[0].user_list.length - 1) : 0;
                            data.list[0].team_info.users = users;
                            data.list[0].team_info.owner_name = owner_name;
                            data.list[0].team_info.cpu_use_per = data.list[0].quto_info.cpu_per[0];
                            data.list[0].team_info.cpu_use_cnt = data.list[0].quto_info.cpu_cnt[0];
                            data.list[0].team_info.cpu_tot_cnt = data.list[0].quto_info.cpu_cnt[1];
                            data.list[0].team_info.mem_use_per = data.list[0].quto_info.mem_per[0];
                            data.list[0].team_info.mem_use_cnt = data.list[0].quto_info.mem_cnt[0];
                            data.list[0].team_info.mem_tot_cnt = data.list[0].quto_info.mem_cnt[1];
                            data.list[0].team_info.disk_use_per = data.list[0].quto_info.disk_per[0];
                            data.list[0].team_info.disk_use_cnt = data.list[0].quto_info.disk_cnt[0];
                            data.list[0].team_info.disk_tot_cnt = data.list[0].quto_info.disk_cnt[1];
                        }


                        $scope.select = data.list[0].team_info;
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
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

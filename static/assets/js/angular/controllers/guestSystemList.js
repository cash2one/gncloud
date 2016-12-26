angular
    .module('gncloud')
    .controller('guestSystemListCtrl', function ($scope, $http, dateModifyService) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $("#container").hide();
        $("#team-sett").hide();
        $("#cluster-sett").hide();
        $("#image-sett").hide();
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
                        var usersfirst ="";
                        var usersfirstid ="";
                        for (var j = 0; j < data.list[i].user_list.length; j++) {
                            if (data.list[i].user_list[j][0].team_owner == 'owner') { //팀장찾는 곳
                                owner_id = data.list[i].user_list[j][1].user_id;
                                owner_name = data.list[i].user_list[j][1].user_name;

                            }else if(j==1){
                                usersfirst = data.list[i].user_list[j][1].user_name;
                                usersfirstid="("+data.list[i].user_list[j][1].user_id+")";
                            }else{
                                users +=data.list[i].user_list[j][1].user_name+"("+data.list[i].user_list[j][1].user_id+")/";
                            }

                        }
                        data.list[i].team_info.userslen = users.split('/').length-1;
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
        $scope.refresh = function(){
            $scope.table = Array.prototype.slice.call($scope.table).reverse();
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
        $scope.click=function(ty){
            if(ty == 'profile-system') {
                $("#profile-system").fadeIn();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
            }
            else if(ty == 'team-sett'){
                $("#profile-system").hide();
                $("#team-sett").fadeIn();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
            }
            else if(ty =='cluster-sett'){
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").fadeIn();
                $("#image-sett").hide();
            }
            else if(ty =='image-sett'){
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").fadeIn();
            }
        }



});

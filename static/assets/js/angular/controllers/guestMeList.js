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
        $http({
            method: 'GET',
            url: '/api/manager/vm/account/users/list',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.te_list = data.list;

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
                    $scope.teamname = data.list;

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
                    $scope.team_list = data.list;

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
                    $scope.data_list = data.list;
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
                    $scope.won_list = data.list;
                    $scope.won_list[0][0].total = data.list.length;
                    for(var i = 0 ; i < data.list.length ; i++) {
                        $scope.won_list[i][1].comf = data.list[i][1].comfirm;
                        if($scope.won_list[i][1].comf == 'Y'){
                           var comfirm_re = '승인'
                        } else {
                           var comfirm_re = '비승인'
                        }
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
        $scope.submit = function() {
            $http({
                method  : 'PUT',
                url: '/api/manager/vm/account/users/list',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
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
        $scope.update = function (id, code, action) {
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
        $scope.change = function () {
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
        $scope.download = function (id) {
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
                $("#profile").show();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").hide();
            }
            else if(ty == 'key-sett'){
                $("#profile").hide();
                $("#key-sett").show();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").hide();
            }
            else if(ty == 'profile-team'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").show();
                $("#team-reso").hide();
                $("#team-group").hide();
            }
            else if(ty == 'team-reso'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").show();
                $("#team-group").hide();
            }
            else if(ty == 'team-group'){
                $("#profile").hide();
                $("#key-sett").hide();
                $("#profile-team").hide();
                $("#team-reso").hide();
                $("#team-group").show();
            }
        }
        });
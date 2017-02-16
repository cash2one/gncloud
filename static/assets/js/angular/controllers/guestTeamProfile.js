angular
    .module('gncloud')
    .controller('guestTeamProfileCtrl', function ($scope, $http, dateModifyService, $rootScope, notification) {
        $scope.team_profile=function(){
            $http({
                method: 'GET',
                url: '/api/manager/vm/account/teamname',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.teamname = data.list; //유저팀에 대한 정보
                        $("#team_name").val($scope.teamname.team_name);

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
                        if(data.list.list !=null){
                            for(var i = 0 ; i < data.list.list.length ; i++) {
                                data.list.list[i].user_id = data.list.list[i][0].user_name;
                                newArr.push(data.list.list[i]);
                            }
                            $scope.check_list = 2;
                            $scope.team_list = newArr; // 팀원들에 대한 정보
                        }else{
                            $scope.check_list = 1;
                        }

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
        $scope.team_profile();
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
                        notification.sendMessage("success","팀이름 변경되었습니다");
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
    });

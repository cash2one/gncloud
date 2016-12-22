angular
    .module('gncloud')
    .controller('guestReadyTeamCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $scope.team_list = {};
        $http({
            method: 'GET',
            url: '/api/manager/vm/account/teamcomfirm',
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
        $scope.sh_list = {};
        $http({
            method: 'GET',
            url: '/api/manager/vm/account/users',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.sh_list = data.list;


                } else {
                    alert(data.message);
                }

            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.delete= function(id, code, $location){
            $http({
                method : 'DELETE',
                url : '/api/manager/vm/account/teamset/'+id+'/'+code,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        alert("가입취소되었습니다");
                        location.href="/main/#/guestSelectTeam"
                    } else {
                        alert(data.message);
                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });
        }

    });
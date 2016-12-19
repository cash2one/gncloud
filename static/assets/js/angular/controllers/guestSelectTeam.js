angular
    .module('gncloud')
    .controller('guestSelectTeamCtrl', function ($scope, $http, $location) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $('[data-toggle="tooltip"]').tooltip();
        $scope.list = {};

        $http({
            method: 'GET',
            url: '/api/manager/vm/account/selectteam',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.list = data.list;
                    //alert($scope.guest_list.id);

                } else {
                    alert(data.message);
                }

            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.data = {};
        $scope.update_image = function (data) {
            if (data != null) {
                $scope.data.team_code = data.team_code;
            }
        };
        $scope.submit=function($location){
            $http({
                method: 'POST',
                url:'/api/manager/vm/account/selectteam' ,
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8',
                }
            })
                .success(function (data) {
                    if (data.status == true) {
                        alert("가입이 신청이 완료되었습니다");
                        $location.path('/guestReadyTeam');

                    } else {
                        alert(data.message);
                    }
                });
        }

    });
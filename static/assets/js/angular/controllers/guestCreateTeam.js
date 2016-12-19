angular
    .module('gncloud')
    .controller('guestCreateTeamCtrl', function ($scope, $http) {
        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $scope.submit = function() {
            $http({
                method  : 'POST',
                url: '/api/manager/vm/account/createteam',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                }
            })
                .success(function(data) {
                    if (data.message == "ok") {
                        alert("팀생성이 완료되었습니다.");
                    } else {
                        alert(data.message)
                    }
                });
        };


    });
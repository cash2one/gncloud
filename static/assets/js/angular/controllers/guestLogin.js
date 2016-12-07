angular
    .module('gncloud')
    .controller('guestLoginCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');


        $scope.data = {};
        $scope.submit = function () {
            $http({
                method: 'POST',
                url: '/monitor/vm/guestLogin',
                data: $scope.data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data) {
                    if (data.message == "True") {
                        alert("로그인이 되었습니다.");
                    } else {
                        alert(data.message)
                    }
                });
        };

        $scope.update_image = function (list) {
            if (list != null) $scope.data.baseImage = list.name;
        };

    });
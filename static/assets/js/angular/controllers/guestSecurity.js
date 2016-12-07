angular
    .module('gncloud')
    .controller('guestSecurityCtrl', function ($scope, $http) {
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
                url: '/api/kvm/user/sshkey',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8',
                }
            })
                .success(function (data) {
                    if (data.message == "ok") {
                        alert("SSH key 추가되었습니다");
                    } else {
                        alert(data.message)
                    }
                });
        };

    });
angular
    .module('gncloud')
    .controller('guestSignUpCtrl', function ($scope, $http) {
        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $scope.submit = function() {
            $http({
                method  : 'POST',
                url: '/manager/vm/guestSignUp',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                }
            })
                .success(function(data) {
                    if (data.message == "ok") {
                        alert("회원가입이 되었습니다.");
                    } else {
                        alert(data.message)
                    }
                });
        };


    });
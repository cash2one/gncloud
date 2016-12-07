angular
    .module('gncloud')
    .controller('guestLoginCtrl', function ($scope, $http, $location) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');


        $scope.data = {};
        $scope.submit = function() {
            $http({
                method  : 'POST',
                url: '/manager/vm/guestLogin',
                data: $scope.data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data) {
                        if (data.status == true) {
                            $location.url('/#')
                            alert(data.message)
                        } else {
                            alert(data.message)
                        }
                    });



        };



    });
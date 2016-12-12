angular
    .module('gncloud')
    .controller('guestRunListCtrl', function ($scope, $http, $interval) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $scope.test_list = {};
        $http({
            method: 'GET',
            url: '/vm',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })

            .success(function (data, status, headers, config) {
                if (data) {
                    $scope.test_list = data.list;
                }
                else {
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        //$interval(function(){
        //    $http({
        //        method: 'GET',
        //        url: '/monitor/vm',
        //        headers: {'Content-Type': 'application/json; charset=utf-8'}
        //    })
        //        .success(function (data, status, headers, config) {
        //            if (data) {
        //                $scope.test_list = data.list;
        //            }
        //            else {
        //
        //            }
        //        })
        //        .error(function (data, status, headers, config) {
        //            console.log(status);
        //        });
        //},5000);

    });
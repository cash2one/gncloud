angular
    .module('gncloud')
    .controller('guestMeListCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        //$scope.Me_list = {};

        $http({
            method: 'GET',
            url: '/manager/vm/guestMeList',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.Me_list = data.list;

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
            url: '/manager/vm/guestTeam',
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
        //
        //$scope.update = function (id, action, index) {
        //    var url = '/manager/vm/guestMeList/' + id;
        //    var method = "PUT";
        //    if (action.type == "repair") {
        //        url = '/manager/vm/guestMeList' + id;
        //        method = 'PUT';
        //    }
        //
        //    $http({
        //        method: method,
        //        url: url,
        //        data: action,
        //        headers: {'Content-Type': 'application/json; charset=utf-8'}
        //    })
        //        .success(function(data, status, headers, config) {
        //            if (data.status == true) {
        //                alert(name + " guest의 상태가 변경되었습니다");
        //                $scope.guest_list.splice(index, 1);
        //            } else {
        //                alert(data.message);
        //            }
        //        })
        //        .error(function(data, status, headers, config) {
        //            console.log(status);
        //        });
        //
        //}
    });
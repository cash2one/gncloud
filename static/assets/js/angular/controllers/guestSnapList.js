angular
    .module('gncloud')
    .controller('guestSnapListCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $http({
            method: 'GET',
            url: '/api/kvm/vm/images/snap',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {
                    $scope.guest_snap_list = data.list;
                }
                else {
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

        $scope.update = function (id, index) {
            $http({
                method: 'DELETE',
                url: '/api/kvm/vm/images/' + id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    $scope.guest_snap_list.splice(index, 1);
                    alert("삭제되었습니다");
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });


        }


    });
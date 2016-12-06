angular
    .module('gncloud')
    .controller('guestKeyListCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $http({
            method: 'GET',
            url: '/api/kvm/user/sshkey',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {
                    $scope.data_list = data.list;
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
                url: '/api/kvm/user/sshkey/' + id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    alert(name + " guest의 상태가 변경되었습니다");
                    $scope.data_list.splice(index, 1);
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });


        }
    });
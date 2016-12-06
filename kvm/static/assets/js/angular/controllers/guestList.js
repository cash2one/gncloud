angular
    .module('gncloud')
    .controller('guestListCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $scope.guest_list = {};

        $http({
            method: 'GET',
            url: '/api/kvm/vm',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function(data, status, headers, config) {
                if( data ) {
                    $scope.guest_list = data.list;
                }
                else {
                }
            })
            .error(function(data, status, headers, config) {
                console.log(status);
            });

        $scope.actions = [
            {name: '시작', type: 'resume'},
            {name: '정지', type: 'suspend'},
            {name: '재시작', type: 'reboot'},
            {name: '삭제', type: 'delete'},
            {name: '스냅샷', type: 'snap'}
        ];

        $scope.update = function (id, action, index) {
            $http({
                method: 'PUT',
                url: '/api/kvm/vm/' + id,
                data: action,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    alert(name+" guest의 상태가 변경되었습니다");
                    $scope.guest_list.splice(index, 1);
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });

        }
    });
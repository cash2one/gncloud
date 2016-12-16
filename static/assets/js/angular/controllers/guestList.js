angular
    .module('gncloud')
    .controller('guestListCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $('[data-toggle="tooltip"]').tooltip();
        $scope.guest_list = {};

        $http({
            method: 'GET',
            url: '/api/manager/vm/machines',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.guest_list = data.list;
                    //alert($scope.guest_list.id);

                } else {
                    alert(data.message);
                }

            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

        $scope.actions = [
            {name: '시작', type: 'resume'},
            {name: '정지', type: 'suspend'},
            {name: '재시작', type: 'reboot'}
        ];

        $scope.update = function (id, action, index) {
            var url = '/api/kvm/vm/machines/' + id;
            var method = "PUT";
            if (action.type == "delete") {
                url = '/api/kvm/vm/machines/' + id;
                method = 'DELETE';
            }

            $http({
                method: method,
                url: url,
                data: action,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        alert(name + " guest의 상태가 변경되었습니다");
                        $scope.guest_list.splice(index, 1);
                    } else {
                        alert(data.message);
                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });

        }

        $scope.desc = function(){

        }
    });
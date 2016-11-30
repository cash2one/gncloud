angular
    .module('gncloud')
    .controller('guestCreateCtrl', function ($scope, $http) {
        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $http({
            method: 'GET',
            url: '/gncloud/vm/images/kvm_snap',
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


        $scope.data = {};
        $scope.data.baseImage = "";
        $scope.submit = function() {
            $http({
                method  : 'POST',
                url: '/gncloud/vm',
                data: $scope.data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data) {
                    if (data.message == "ok") {
                        alert("VM이 생성되었습니다");
                    } else {
                        alert(data.message)
                    }
                });
        };

        $scope.update_image = function (list) {
            if (list != null) $scope.data.baseImage = list.name;
        };

    });
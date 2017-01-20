angular
    .module('gncloud')
    .controller('guestLoginHistCtrl', function ($scope, $http, dateModifyService,$routeParams,Upload) {
        $scope.getClusterList=function() {
            $http({
                method: 'GET',
                url: '/api/manager/vm/loginhist',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.login_hist = data.list;
                        for (var i = 0; i < data.list.length; i++) {
                            $scope.login_hist[i].create_time_diff = data.list[i].action_time.splice(0,6);
                        }
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.getClusterList();
    });
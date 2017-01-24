angular
    .module('gncloud')
    .controller('guestMoneyCtrl', function ($scope, $http, dateModifyService,$routeParams,Upload) {
        $scope.List = function() {
            $http({
                method: 'GET',
                url: '/api/manager/vm/money',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.list = data.list;

                    } else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        };
        $scope.List();
        $scope.submit=function (data) {
            $scope.data={}
            $scope.data.monitor_period = data;
            $http({
                method: 'PUT',
                url: '/api/manager/vm/money/monitor',
                data:$scope.data,
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        alert("저장되었습니다.");
                        $scope.List();

                    } else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        }
    });
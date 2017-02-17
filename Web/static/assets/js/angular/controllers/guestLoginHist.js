angular
    .module('gncloud')
    .controller('guestLoginHistCtrl', function ($scope, $http) {

        $scope.data={};
        $scope.page=function (page) {
            $scope.data.page=page;
            $http({
                method: 'GET',
                url: '/api/manager/vm/loginhist',
                params:$scope.data//,
                //headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.login_hist = data.list.list;
                        $scope.page_hist =data.list.page+1;
                        $scope.page_total =data.list.total+1;
                        $scope.prev_page = page - 1;
                        $scope.next_page = page + 1;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.page(1);
    });
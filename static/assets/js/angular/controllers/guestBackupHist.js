angular
    .module('gncloud')
    .controller('guestBackupHistCtrl', function ($scope, $http, dateModifyService,$routeParams,Upload) {
        $scope.data={};
        $scope.page=function (page) {
            $scope.data.page=page;
            $http({
                method: 'GET',
                url: '/api/manager/vm/backuphist',
                params:$scope.data//,
                //headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.backup = data.list.list;
                        $scope.total_page=data.list.total_page;
                        $scope.page_hist =data.list.page+1;
                        $scope.page_total =data.list.total+1;
                        $scope.prev_page = page - 1;
                        $scope.next_page = page + 1;
                        $scope.this_page = data.list.page*10;
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
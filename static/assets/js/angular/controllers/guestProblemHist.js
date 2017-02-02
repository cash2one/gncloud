angular
    .module('gncloud')
    .controller('guestProblemHistCtrl', function ($scope, $http) {

        $scope.data={};
        $scope.page=function(page) {
            $scope.data.page=page;
            $http({
                method: 'GET',
                url: '/api/manager/vm/errorhist',
                params:$scope.data//,
                //headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.error_hist = data.list.list;
                        $scope.total_count = data.list.total_count;
                        $scope.solve_count = data.list.solve_count;
                        $scope.not_solve_count = data.list.not_solve_count;
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
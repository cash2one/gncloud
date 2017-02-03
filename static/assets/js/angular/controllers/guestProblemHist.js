angular
    .module('gncloud')
    .controller('guestProblemHistCtrl', function ($scope, $http) {
        var d = new Date();

        $scope.data={"year":d.getFullYear(),"month":(d.getMonth() + 1), "solve":true, "notsolve":true};
        $scope.month_list = [
            {value: 1},
            {value: 2},
            {value: 3},
            {value: 4},
            {value: 5},
            {value: 6},
            {value: 7},
            {value: 8},
            {value: 9},
            {value: 10},
            {value: 11},
            {value: 12}
        ];
        $scope.year_list = [
            {name: d.getFullYear() - 1 , value: d.getFullYear() - 1},
            {name: d.getFullYear(), value: d.getFullYear()}
        ];


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

        $scope.select_error_info=function(id) {
            $http({
                method: 'GET',
                url: '/api/manager/vm/errorhist/'+id,
                params:$scope.select_data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.error_info = data.info;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
    });
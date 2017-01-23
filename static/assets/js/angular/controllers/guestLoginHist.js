angular
    .module('gncloud')
    .controller('guestLoginHistCtrl', function ($scope, $http, dateModifyService,$routeParams,Upload) {
        $scope.getLoginList=function() {
            $http({
                method: 'GET',
                url: '/api/manager/vm/loginhist',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.login_hist = data.list.list;
                        $scope.page_hist =data.list.page;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.getLoginList();
        $scope.data={};
        $scope.page=function (type) {

            if(type == 'next'){
                $scope.data.page=$scope.page_hist+1;
            }else if(type=='before'){
                if($scope.login_hist.page_info != 0){
                    $scope.data.page=$scope.page_hist-1;
                }

            }

            $http({
                method: 'PUT',
                url: '/api/manager/vm/loginhist/page',
                data:$scope.data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.login_hist = data.list.list;
                        $scope.page_hist =data.list.page;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
    });
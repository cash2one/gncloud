angular
    .module('gncloud')
    .controller('guestPriceCtrl', function ($scope, $http, dateModifyService, $rootScope) {
        $scope.price=function(){
            $http({
                method: 'GET',
                url: '/api/manager/vm/price',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.price_list = data.list;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.price();
        $scope.data={}
        $scope.mem=[
            {name:'GB'},
            {name:'MB'}
        ]
        $scope.disk=[
            {name:'GB'},
            {name:'TB'}
        ]
        $scope.sizemem=function (data) {
            $scope.data.mem_size = data.name;
        }
        $scope.sizedisk=function (data) {
            $scope.data.disk_size = data.name;
        }
        $scope.savesize=function(){
            $http({
                method: 'POST',
                url: '/api/manager/vm/price',
                data: $scope.data
            })
                .success(function (data, status, headers, config) {
                    if (data.status==true) {
                        $scope.price();
                        $scope.data={};
                    } else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.actions = [
            {name: '삭제', type: 'delete'}
        ];
        $scope.update=function(id){
            $http({
                method: 'DELETE',
                url: '/api/manager/vm/price/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        alert("삭제 되었습니다.");
                        $scope.price();
                    } else {
                        alert(data.message);
                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });
        }
    });
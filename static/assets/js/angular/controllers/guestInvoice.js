angular
    .module('gncloud')
    .controller('guestInvoiceCtrl', function ($scope, $http, dateModifyService, $rootScope) {
        $scope.price=function () {
            $http({
                method: 'GET',
                url: '/api/manager/price',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.pricelist =data.list;
                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }
                });
        }
        $scope.price();
        $scope.price_list_info=function (year, month, team_code) {
            $scope.data={};
            $scope.data.year = year;
            $scope.data.month = month;
            $scope.data.team_code = team_code;
            $http({
                method: 'GET',
                url: '/api/manager/price/list',
                params:$scope.data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.price_list =data.list.list;
                        $scope.team_code = data.list.team_code;
                        $scope.price_invoice = data.list.instance;
                        var pricInfo = new Array;
                        for(var i = 0 ;i< data.list.instance.each_user.length;i++){
                            for(var j =0;j<data.list.instance.each_user[i].instance_list.length;j++){
                                data.list.instance.each_user[i].instance_list[j].user_id = data.list.instance.each_user[i].user_id;
                                pricInfo.push(data.list.instance.each_user[i].instance_list[j]);
                            }

                        }
                        $scope.price_info =pricInfo;

                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }
                });
        }

    });
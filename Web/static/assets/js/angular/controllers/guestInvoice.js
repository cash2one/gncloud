angular
    .module('gncloud')
    .controller('guestInvoiceCtrl', function ($scope, $http, dateModifyService, $rootScope) {
        $scope.data={};
        $scope.page=function (page) {
            $scope.data.page=page;
            $http({
                method: 'GET',
                url: '/api/manager/price',
                params:$scope.data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        for(var i = 0; i < data.list.list.length;i++){
                            data.list.list[i].totalprice = data.list.list[i].invoice_data.team_price;
                        }
                        $scope.pricelist =data.list.list;

                        $scope.page_hist = data.list.page+1;
                        $scope.page_total =data.list.total+1;
                        $scope.prev_page = page - 1;
                        $scope.next_page = page + 1;
                    } else {
                        if(data.message != null) {
                            notification.sendMessage("error",data.message);
                        }
                    }
                });
        }
        $scope.page(1);
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
                            notification.sendMessage("error",data.message);
                        }
                    }
                });
        }

    });
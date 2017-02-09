angular
    .module('gncloud')
    .controller('guestServiceListCtrl', function ($scope, $http, $interval,$timeout, dateModifyService, $rootScope, notification) {
        var stop;
        $scope.selectGuestList = function() {
            $http({
                method: 'GET',
                url: '/api/manager/vm/services',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.guest_list = data.list.guest_list;

                        for (var i = 0; i < data.list.guest_list.length; i++) {
                            var tagArr = data.list.guest_list[i].tag.split(",");
                            if (tagArr.length - 1 > 0) {
                                $scope.guest_list[i].tagFirst = tagArr[0];
                                $scope.guest_list[i].tagcount = "+" + (tagArr.length - 1);
                            } else {
                                $scope.guest_list[i].tagFirst = data.list.guest_list[i].tag;
                            }
                            $scope.guest_list[i].create_time_diff = dateModifyService.modifyDate(data.list.guest_list[i].create_time);
                        }

                        if(data.list.retryCheck == false) {
                            $interval.cancel(stop);
                            stop = undefined;
                        }


                    } else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        };
        $scope.selectGuestList();
        stop = $interval($scope.selectGuestList,10000);


    }).directive('tooltip', function(){
        return {
            restrict: 'A',
            link: function(scope, element, attrs){
                $(element).hover(function(){
                    $(element).tooltip('show');
                }, function(){
                    $(element).tooltip('hide');
                });
            }
        };
    });
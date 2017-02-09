angular
    .module('gncloud')
    .controller('guestListCtrl', function ($scope, $http, $interval,$timeout, dateModifyService, $rootScope, notification) {
        var stop;
        $scope.selectGuestList = function() {
            $http({
                method: 'GET',
                url: '/api/manager/vm/machines',
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

        $scope.actions = [
            {name: '시작', type: 'Resume'},
            {name: '정지', type: 'Suspend'},
            {name: '재시작', type: 'Reboot'}
        ];

        $scope.update = function (id, action, sh, index) {
            console.log(index);
            $http({
                method: "POST",
                url: "/api/manager/vm_hist/machines/" + id,
                data: action,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        $scope.guest_list[index].status = "Starting"
                    } else {
                    }
                })

            $http({
                method: "PUT",
                url: "/api/"+ sh +"/vm/machines/" + id,
                data: action,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        notification.sendMessage("success",$scope.guest_list[index].name+" 인스턴스가 "+action.name +"되었습니다.");
                        $scope.selectGuestList();
                    } else {
                        notification.sendMessage("error",$scope.guest_list[index].name+" 인스턴스 "+action.name +"중에 에러가 발생하였습니다.");
                    }
                })

        }

        $scope.refresh = function(){
            $scope.guest_list = Array.prototype.slice.call($scope.guest_list).reverse();
        }
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
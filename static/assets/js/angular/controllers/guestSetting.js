angular
    .module('gncloud')
    .controller('guestSettingCtrl', function ($scope, $http) {

        $scope.weeked = [
            { "name" : "월", "checked" : false },
            { "name" : "화", "checked" : false },
            { "name" : "수", "checked" : false },
            { "name" : "목", "checked" : false },
            { "name" : "금", "checked" : false },
            { "name" : "토", "checked" : false },
            { "name" : "일", "checked" : false }
        ];

        $scope.List = function() {
            $http({
                method: 'GET',
                url: '/api/manager/vm/money',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.monitor = data.list.list;
                        $scope.bills = data.list.billing;
                        $scope.backup_type= data.list.backup_type;
                        $scope.backup_days = data.list.backup_days;
                        if(data.list.backup_type == 'W'){
                            for(var i=0;i<data.list.backup_week.length;i++){
                                if(data.list.backup_week[i] == 1){
                                    $scope.weeked[i].checked = true;
                                }else{
                                    $scope.weeked[i].checked = false;
                                }

                            }
                            $scope.day=0;
                        }else{
                            $scope.day = data.list.backup_week;
                        }
                        $("#day").val($scope.day);
                        $("#monitor").val($scope.monitor);
                        $("#dayforback").val($scope.backup_days);
                    } else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        };
        $scope.model={
            roles:[

            ]
        };
        $scope.List();
        $scope.submit=function (data) {
            $scope.data={}
            $scope.data.monitor_period = data;
            $http({
                method: 'PUT',
                url: '/api/manager/vm/money/monitor',
                data:$scope.data
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        alert("저장되었습니다.");
                        $scope.List();

                    } else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        }

        $scope.day_submit=function () {
            $scope.data={};
            var bills=$(':radio[name=day]:checked').val();
            $scope.data.bills=bills
            $http({
                method:'PUT',
                url:'/api/manager/vm/day',
                data:$scope.data
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        alert("저장되었습니다.");
                        $scope.List();

                    } else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        }
        $scope.backup_day=function () {
            var type=$(':radio[name=select]:checked').val();
            $scope.data={};
            if(type == 'W'){
                $scope.data.type=type;
                $scope.data.value ="";
                for(var i=0;i<$scope.weeked.length;i++){
                    $scope.data.value += $scope.weeked[i].checked == true ? "1":"0";
                }
                $scope.data.backday= $scope.backday;
            }else{
                $scope.data.type=type;
                $scope.data.value= $scope.changeday;
                $scope.data.backday= $scope.backday;
            }
            $http({
                method:'PUT',
                url:'/api/manager/vm/backup',
                data:$scope.data
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        alert("저장되었습니다.");
                        $scope.List();

                    } else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        }
    });
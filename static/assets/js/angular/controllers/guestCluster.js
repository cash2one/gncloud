angular
    .module('gncloud')
    .controller('guestClusterCtrl', function ($scope, $http, dateModifyService,$routeParams,Upload) {
        $scope.registYn = "Y";
        $scope.getClusterList=function() {
            $http({
                method: 'GET',
                url: '/api/manager/vm/cluster',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.cluster_list = data.info;
                        for (var i = 0; i < $scope.cluster_list.length; i++) {
                            $scope.cluster_list[i].create_time_diff = dateModifyService.modifyDate(data.info[i].create_time);
                        }

                        if ($scope.cluster_list.length == 3) {
                            $scope.registYn = "N";
                        }
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.getClusterList();
        $scope.cluster={};
        $scope.host={}
        $scope.getCluster=function(id){
            $http({
                method: 'GET',
                url: '/api/manager/vm/cluster/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.cluster = data.info;
                        for (var i = 0; i < data.info.gnHostMachines.length; i++) {
                            $("hostlist").html($("hostlist").html()+data.info.gnHostMachines[i].ip);
                        }
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.deleteNode=function(id){
            $http({
                method: 'DELETE',
                url: '/api/manager/vm/cluster/node/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.getCluster($scope.cluster.id);
                        $scope.getClusterList();
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.saveCluster=function(){
            alert($scope.cluster.type);
            $http({
                method: 'POST',
                url: '/api/manager/vm/cluster',
                data:$scope.cluster,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.getClusterList();
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.deleteCluster=function(id){
            $http({
                method: 'DELETE',
                url: '/api/manager/vm/cluster/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.getClusterList();
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.saveHost=function(){

            if($scope.host.ip == null){
                alert("ip를 입력하세요");
                return false;
            }

            $http({
                method: 'POST',
                url: '/api/manager/vm/host',
                data:$scope.host,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        if($scope.cluster.node == null){
                            $scope.cluster.node = $scope.host.ip;
                        }else{
                            $scope.cluster.node += $scope.host.ip;
                        }
                        $scope.host = {};
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
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

angular
    .module('gncloud')
    .controller('guestClusterCtrl', function ($scope, $http, dateModifyService,$routeParams,Upload) {

        //****기본 변수 세팅*****//
        $scope.registYn = "N";
        $scope.cluster_type_list = [
             {"name":"Hyper-V","type":"hyperv","viewYn":"Y"}
            ,{"name":"Kvm","type":"kvm", "viewYn":"Y"}
            ,{"name":"Docker","type":"docker", "viewYn":"Y"}
        ]
        $scope.cluster={};
        $scope.host={};
        $scope.mem=[
            {name:'GB'},
            {name:'MB'}
        ]
        $scope.disk=[
            {name:'GB'},
            {name:'TB'}
        ]


        //****클러스터 리스트,클러스터 정보 조회 조회*****//
        $scope.getClusterList=function() {
            $http({
                method: 'GET',
                url: '/api/manager/vm/cluster',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.cluster_list = data.info;

                        for(var j =0 ; j < $scope.cluster_type_list.length ; j++){
                            $scope.cluster_type_list[j].viewYn = "Y";
                        }

                        for (var i = 0; i < $scope.cluster_list.length; i++) {
                            $scope.cluster_list[i].create_time_diff = dateModifyService.modifyDate(data.info[i].create_time);

                            for(var j =0 ; j < $scope.cluster_type_list.length ; j++){
                                if($scope.cluster_type_list[j].type == $scope.cluster_list[i].type){
                                    $scope.cluster_type_list[j].viewYn = "N";
                                }
                            }
                        }
                        var clusterCount = 0
                        for(var j =0 ; j < $scope.cluster_type_list.length ; j++){
                            if($scope.cluster_type_list[j].viewYn == "Y") clusterCount++;
                        }
                        if (clusterCount >  0) {
                            $scope.registYn = "Y";
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

                        $("#input_host").hide();
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        //****클러스터, 노드 삭제***//
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

        //****클러스터, 노드 저장****//
        $scope.saveCluster=function(){
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
        $scope.saveHost=function(){
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
                        $scope.getClusterList();
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }


        //****폼 리셋****//
        $scope.clear=function(){
            $scope.cluster = {};
        }

        //****노드 추가시 타입 셋팅****//
        $scope.addNode=function(type){
            $scope.host={};
            $scope.memsize={};
            $scope.disksize={};
            $scope.host.type = type;
        }

        //****라디오버튼*****//
        $scope.sizemem=function (data) {
            $scope.host.mem_size = data.name;
        }
        $scope.sizedisk=function (data) {
            $scope.host.disk_size = data.name;
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

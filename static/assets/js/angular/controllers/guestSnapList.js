angular
    .module('gncloud')
    .controller('guestSnapListCtrl', function ($scope, $http, dateModifyService, $timeout, $interval) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $("#container").hide();
        $("#snap").hide();
        $scope.snap =function(data){
            if(data == 'mac'){
                $("#tab").fadeIn();
                $("#sab").fadeIn();
                $("#snap").hide();
                $("#image").fadeIn();
                $("#container").hide();
            }
            if(data == 'snap'){
                $("#snap").fadeIn();
                $("#image").hide();
                $("#container").hide();
                $scope.snapList();
            }
            if(data == 'image') {
                $("#snap").hide();
                $("#image").fadeIn();
                $("#container").hide();
            }
            if(data == 'container'){
                $("#tab").hide();
                $("#sab").hide();
                $("#snap").hide();
                $("#image").hide();
                $("#container").fadeIn();
                $scope.container();
            }
        }
        $http({
            method: 'GET',
            url: '/api/manager/vm/images/base',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {
                    $scope.base_list = data.list.guest_list;
                }
                else {
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

        var stop;
        $scope.snapList = function() {
            $http({
                method: 'GET',
                url: '/api/manager/vm/images/snap',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.snap_list = data.list.guest_list;
                        for(var i = 0 ; i < data.list.guest_list.length ; i++){
                            $scope.snap_list[i].create_time_diff = dateModifyService.modifyDate(data.list.guest_list[i].create_time);
                        }

                    }
                    if(data.list.retryCheck == false){
                        $interval.cancel(stop);
                        stop = undefined;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
            $http({
                method: 'GET',
                url: '/api/manager/vm/snaplist',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.list = data.list.guest_list;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        stop = $interval($scope.snapList,10000);


        $scope.container=function(){
            $http({
                method: 'GET',
                url: '/api/manager/vm/container/services/base',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.contain_list = data.list;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });

        }

        $scope.actions = [
            {name: '삭제', type: 'delete'}
        ];
        $scope.update = function (id, action, ty,index) {
            if (action.type == "delete") {
                 var  url = '/api/'+ty+'/vm/images/' + id;
                 var  method = 'DELETE';
            }

            $http({
                method: method,
                url: url,
                data: action,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        alert(name + "상태가 변경되었습니다");
                        $scope.snap_list.splice(index, 1);
                    } else {
                        alert(data.message);
                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });

        };

        $scope.data = {};
        $scope.update_image = function (data) {
            if (data != null) {
                $scope.data.ord_id = data.id;
                $scope.data.type = data.type;
            }
        };
        $scope.submit= function(){
            $http({
                method : 'POST',
                url : '/api/manager/vm/machine/snapshots',
                data: $scope.data,
                headers:{
                    'Content-Type': 'application/json; charset=utf-8'
                }
            })
                .success(function(data){
                if(data.status ==true){
                    $scope.createSnap(data.value, data.snap_id);
                }else{
                    if(data.value != null) {
                        alert(data.value)
                    }
                }
            })
        }
        $scope.createSnap = function (ord_id,vm_id) {
            $timeout(function(){
                $scope.snapList();
            },1000,true);
            $http({
                method: 'POST',
                url: "/api/" + $scope.data.type + "/vm/machine/snapshots",
                data: '{"ord_id":"'+ord_id+'", "vm_id":"'+vm_id+'"}',//ord_id = 머신id vm_id = 스냅샷 아이디
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data) {
                    if (data.status == true) {
                        $scope.snapList();
                    } else {
                        alert(data.message);
                    }
                });
        };
        $scope.refresh = function(){
            $scope.snap_list = Array.prototype.slice.call($scope.snap_list).reverse();
        }


    });
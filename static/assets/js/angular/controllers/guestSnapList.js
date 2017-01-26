angular
    .module('gncloud')
    .controller('guestSnapListCtrl', function ($scope, $http, dateModifyService, $timeout, $interval, $rootScope) {
        $scope.user_info = $rootScope.user_info;
        $rootScope.$on('init', function () {
            $scope.user_info = $rootScope.user_info;
        });

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
                $("#container").hide();
                $("#machine").fadeIn();
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
                $("#machine").hide();
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
                        for(var i = 0 ; i < $scope.snap_list.length ; i++){
                            $scope.snap_list[i].create_time_diff = dateModifyService.modifyDate(data.list.guest_list[i].create_time);
                        }
                        console.log(data.list.guest_list.length);
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
                        for (var i = 0; i < data.list.length; i++) {
                            var tagArr = data.list[i].tag.split(",");
                            if (tagArr.length - 1 > 0) {
                                $scope.contain_list[i].tagFirst = tagArr[0];
                                $scope.contain_list[i].tagcount = "+" + (tagArr.length - 1);
                            } else {
                                $scope.contain_list[i].tagFirst = data.list[i].tag;
                            }
                        }
                    }else {
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
            $http({
                method: 'PUT',
                url: '/api/manager/vm/images/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        $scope.snapshotsdelete(ty,id);
                    } else {
                        alert("삭제 되었습니다.");
                        $scope.snapList();
                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });
        };
        $scope.snapshotsdelete=function(ty,id){
            $timeout(function(){
                $scope.snapList();
            },2000,true);
            $http({
                method: 'DELETE',
                url: '/api/'+ty+'/vm/images/' + id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        alert("삭제 되었습니다.");
                        $scope.snapList();
                    } else {
                        alert(data.message);
                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });
        }
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
                    $scope.createSnap(data.ord_id, data.snap_id);
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
            },2000,true);
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
        $scope.snap_list_info=function(id){
            $http({
                method: 'GET',
                url: '/api/manager/vm/snapshot/list/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        if(data.list.snap_info.ssh_id=="") {
                            data.list.snap_info.ssh_id="-";
                        }
                        $scope.snapshot=data.list.snap_info;
                        $scope.snapshot.user_name = data.list.user_info.user_name;
                        $scope.parent_history = Array.prototype.slice.call(data.list.parent_history.split(",")).reverse();

                    } else {

                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.refresh = function(){
            $scope.snap_list = Array.prototype.slice.call($scope.snap_list).reverse();
        }


    });
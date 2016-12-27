angular
    .module('gncloud')
    .controller('guestSnapListCtrl', function ($scope, $http, dateModifyService) {

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
                $("#tab").show();
                $("#sab").show();
                $("#snap").hide();
                $("#image").show();
                $("#container").hide();
            }
            if(data == 'snap'){
                $("#snap").show();
                $("#image").hide();
                $("#container").hide();
            }
            if(data == 'image') {
                $("#snap").hide();
                $("#image").show();
                $("#container").hide();
            }
            if(data == 'container'){
                $("#tab").hide();
                $("#sab").hide();
                $("#snap").hide();
                $("#image").hide();
                $("#container").show();
            }
        }
        $http({
            method: 'GET',
            url: '/api/manager/vm/images/base',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {
                    $scope.base_list = data.list;
                }
                else {
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });


        $scope.snapList = function() {
            $http({
                method: 'GET',
                url: '/api/manager/vm/images/snap',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.snap_list = data.list;
                        for(var i = 0 ; i < data.list.length ; i++){
                            $scope.snap_list[i].create_time_diff = dateModifyService.modifyDate(data.list[i].create_time);
                        }


                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.snapList();


        $http({
            method: 'GET',
            url: '/api/manager/vm/container/services',
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

        $scope.actions = [
            {name: '시작', type: 'resume'},
            {name: '정지', type: 'suspend'},
            {name: '재시작', type: 'reboot'},
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

        }
        $http({
            method: 'GET',
            url: '/api/manager/vm/machines',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {
                    $scope.list = data.list;
                }
                else {
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.data = {};
        $scope.update_image = function (data) {
            if (data != null) {
                $scope.data.ord_id = data.id;
                $scope.data.type = data.type;
            }
        };
        $scope.submit = function () {
            var url = "/api/" + $scope.data.type + "/vm/machine/snapshots";
            $http({
                method: 'POST',
                url: url,
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8',
                }
            })
                .success(function (data) {
                    if (data.status == true) {
                        alert("스냅샷이 생성되었습니다");
                        $scope.snapList();
                    } else {
                        alert(data.message);
                    }
                });
        };



    });
angular
    .module('gncloud')
    .controller('guestServiceCreateCtrl', function ($scope, $http, $timeout, $rootScope,notification) {

        $http({
            method: 'GET',
            url: '/api/manager/vm/createsize',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {
                    $scope.size = data.list;
                }
                else {
                    if(data.message != null) {
                        alert(data.message)
                    }
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

        $http({
            method: 'GET',
            url: '/api/manager/vm/clustercheck',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {
                    $scope.hyper = data.list.hyper;
                    $scope.kvm = data.list.kvm;
                    $scope.docker = data.list.docker;
                }
                else {
                    if(data.message != null) {
                        alert(data.message)
                    }
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

        $scope.selectType = function(type){
                $http({
                    method: 'GET',
                    url: '/api/manager/vm/container/services/base',
                    headers: {'Content-Type': 'application/json; charset=utf-8'}
                })
                    .success(function (data, status, headers, config) {
                        if (data) {
                            $scope.type = type;
                            $scope.image_list = data.list;
                        }
                        else {
                            if(data.message != null) {
                                alert(data.message)
                            }
                        }
                    })
                    .error(function (data, status, headers, config) {
                        console.log(status);
                    });
        }

        $scope.save = function () {
            $http({
                method: 'POST',
                url: '/api/kvm/account/keys',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8',
                }
            })
                .success(function (data) {
                    if (data.status == true) {
                        alert("SSH key 추가되었습니다");
                        $scope.getkeys();
                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }
                });
        };

        $scope.data = {};
        $scope.update_image = function (data) {
            if (data != null){
                $scope.data.id = data.id;
                $scope.data.sub_type = data.sub_type;
                $scope.data.backup = data.backup;
            }
        };
        $scope.func = function(data){
            $scope.data.size_id = data.id;
        }
        $scope.submit = function() {
            $scope.data.tag = $("#tag").val();
            $scope.data.type = $scope.type;
            $http({
                method  : 'POST',
                url: '/api/manager/vm/machine',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                }
            })
                .success(function(data) {
                    if (data.status == true) {
                        if(data.value == 'name'){
                            $scope.data_value = data.value;
                            $("#vm_name").focus();
                        }else if(data.value == 'password'){
                            $scope.data_value = data.value;
                            $("#pasword").focus();
                        }else if(data.value == 'size_id'){
                            $scope.data_value = data.value;
                            $("#cpu").focus();
                        }else if(data.value == 'image_id'){
                            $scope.data_value = data.value;
                            $("#image_id").focus();
                        }else if(data.value == 'type'){
                            $scope.data_value = data.value;
                            $("#type").focus();
                        }else{
                            $scope.createInstance(data.value);
                            $scope.checkdisabled();
                        }
                    } else {
                        if(data.value != null) {
                            notification.sendMessage("warning",data.value);
                        }
                    }
                });
        };

        $scope.createInstance = function(id){
            $timeout(function () {
                window.location.href = '#/guestSerivceList';
            }, 1000 , true );

            $http({
                method  : 'POST',
                url: '/api/'+$scope.type+'/vm/machine',
                data: '{"id":"'+id+'"}',
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                }
            })
                .success(function(data) {
                    if (data.status == true) {
                        notification.sendMessage("success",$scope.data.vm_name+" 인스턴스 생성이 완료되었습니다.");
                    }else {
                        notification.sendMessage("error",$scope.data.vm_name+" 인스턴스 생성중 에러가 발생했습니다.");
                    }
                });
        };
        $scope.isAlive = false;
        $scope.checkdisabled=function () {
            $scope.isAlive = true;
        }

    })
    .directive("checkboxGroup", function() {
        return {
            restrict: "A",
            link: function(scope, elem, attrs) {
                // Determine initial checked boxes
                if (scope.sshkeys.indexOf(scope.item.id) !== -1) {
                    elem[0].checked = true;
                }

                // Update array on click
                elem.bind('click', function() {
                    var index = scope.sshkeys.indexOf(scope.item.id);
                    // Add if checked
                    if (elem[0].checked) {
                        if (index === -1) scope.sshkeys.push(scope.item.id);
                    }
                    // Remove if unchecked
                    else {
                        if (index !== -1) scope.sshkeys.splice(index, 1);
                    }
                    // Sort and update DOM display
                    scope.$apply(scope.sshkeys.sort(function(a, b) {
                        return a - b
                    }));
                });
            }
        }

    });
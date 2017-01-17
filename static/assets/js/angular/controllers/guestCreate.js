angular
    .module('gncloud')
    .controller('guestCreateCtrl', function ($scope, $http, $timeout, $rootScope) {

        $("#windows").hide();
        $("#ssh").hide();
        $("#snap").hide();
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
        $scope.selectType = function(type){
            if(type == 'docker'){
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
                $http({
                    method: 'GET',
                    url: '/api/manager/vm/container/services/snap',
                    headers: {'Content-Type': 'application/json; charset=utf-8'}
                })
                    .success(function (data, status, headers, config) {
                        if (data) {
                            $scope.type = type;
                            $scope.snap_list = data.list;
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
            }else if(type == 'hyperv' || type=='kvm'){
                $http({
                    method: 'GET',
                    url: '/api/manager/vm/images/base/' + type,
                    headers: {'Content-Type': 'application/json; charset=utf-8'}
                })
                    .success(function (data, status, headers, config) {
                        if (data) {
                            $scope.type = type;
                            $scope.image_list = data.list;
                            if(type=='hyperv'){
                                $("#windows").show();
                                $("#ssh").hide();
                            }else if(type =='kvm'){
                                $("#windows").hide();
                                $("#ssh").show();
                            }
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
                    url: '/api/manager/vm/images/snap/' + type,
                    headers: {'Content-Type': 'application/json; charset=utf-8'}
                })
                    .success(function (data, status, headers, config) {
                        if (data.status == true) {
                            $scope.snap_list = data.list;
                            $("#snap").hide();
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

        }

        $scope.getkeys = function () {
            $http({
                method: 'GET',
                url: '/api/kvm/account/keys',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.sshkey_list = data.list;
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

        $scope.getkeys();
        $scope.selectKey = function (data) {
            if (data != null){
                $scope.data.sshkeys = data;
            }
        };

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
        $scope.imageshow = function(ty){
            if(ty == 'image' ){
                $("#image").show();
                $("#snap").hide();
            }
            else if(ty =='snap'){
                $("#image").hide();
                $("#snap").show();

            }
        }
        $scope.data = {};
        $scope.update_image = function (data) {
            if (data != null){
                $scope.data.id = data.id;
                $scope.data.sub_type = data.sub_type;
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
                        }
                    } else {
                        if(data.value != null) {
                            alert(data.value)
                        }
                    }
                });
        };

        $scope.createInstance = function(id){
            $timeout(function () {
                window.location.href = '#/guestList';
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

                    }
                     else {
                    }
                });
        };



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
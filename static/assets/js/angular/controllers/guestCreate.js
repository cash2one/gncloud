angular
    .module('gncloud')
    .controller('guestCreateCtrl', function ($scope, $http) {
        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $scope.hyper = function(ty){
            $http({
                method: 'GET',
                url: '/api/manager/vm/images/base/' + ty,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.image_list = data.list;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });

            $http({
                method: 'GET',
                url: '/api/manager/vm/images/snap/' + ty,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.snap_list = data.list;
                        $("#snap").hide();
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.sshkeys = [];
        $http({
            method: 'GET',
            url: '/api/kvm/account/keys',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data) {
                    $scope.sshkey_list = data.list;
                }
                else {
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

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
                        alert(data.message)
                    }
                });
        };
        $scope.imageshow = function(){
            $("#image").show();
            $("#snap").hide();
        }
        $scope.snapshow = function(){
            $("#image").hide();
            $("#snap").show();
        }
        $scope.data = {};
        $scope.update_image = function (data) {
            if (data != null){
                $scope.data.id = data.id;
            }
        };
        $scope.func = function(cpu, memory, hdd){
            $scope.data.cpu = cpu
            $scope.data.memory = memory
            $scope.data.hdd = hdd
            $scope.data.name = hdd

        }

        $scope.submit = function() {
            console.log($scope.data.id);
            $scope.data.sshkeys = $scope.sshkeys;
            $scope.data.tag = $("#tag").val();
            $http({
                method  : 'POST',
                url: '/api/kvm/vm/machine',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                }
            })
                .success(function(data) {
                    if (data.status == true) {
                        alert("VM이 생성되었습니다");
                    } else {
                        alert(data.message)
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
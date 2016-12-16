angular
    .module('gncloud')
    .controller('guestDetailCtrl', function ($scope, $http, $routeParams, $sce) {

        $scope.cpu_url = $sce.trustAsResourceUrl("/cpu.html?id="+$routeParams.id);
        $scope.mem_url = $sce.trustAsResourceUrl("/memory.html?id="+$routeParams.id);
        $scope.modify_data = {};

        $http({
            method: 'GET',
            url: '/api/manager/vm/machines/'+$routeParams.id,
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.vm_data = data.info.vm_info;
                    $scope.tag_list = data.info.vm_info.tag.split(",");
                    $scope.disk_data = data.info.disk_info;
                }
                else {
                    alert(data.message)
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

        $scope.change_name = function() {
            if($("#vm_name").val() == "") {
                alert("이름을 입력해주세요");
                return false;
            }
            $http({
                method: 'PUT',
                url: '/api/manager/vm/machines/' + $scope.vm_data.id +'/name',
                data: '{"value":"'+$("#vm_name").val()+'"}',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        alert("이름이 수정되었습니다");
                        $scope.vm_data.name = $("#vm_name").val();
                    }
                    else {
                        alert(data.message)
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.change_tag = function() {
            if($("#vm_tag").val() == "") {
                alert("태그를 입력해주세요");
                return false;
            }
            $http({
                method: 'PUT',
                url: '/api/manager/vm/machines/' + $scope.vm_data.id +'/tag',
                data: '{"value":"'+$("#vm_tag").val()+'"}',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        alert("태그가 수정되었습니다");
                        $scope.tag_list = $("#vm_tag").val().split(",");
                    }
                    else {
                        alert(data.message)
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.delete = function() {
            $http({
                method: 'DELETE',
                url: '/api/'+$scope.vm_data.type+'/vm/machines/' + $scope.vm_data.id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                       alert("인스턴스가 삭제되었습니다");
                       window.location.href = '#/guestList';
                    }
                    else {
                        alert(data.message)
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

    });
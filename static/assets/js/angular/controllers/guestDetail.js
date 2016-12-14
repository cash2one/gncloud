angular
    .module('gncloud')
    .controller('guestDetailCtrl', function ($scope, $http, $routeParams) {

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

    });
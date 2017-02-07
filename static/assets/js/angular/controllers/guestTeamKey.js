angular
    .module('gncloud')
    .controller('guestTeamKeyCtrl', function ($scope, $http, dateModifyService, $rootScope) {

        $scope.sshkey=function(){
            $http({
                method: 'GET',
                url: '/api/kvm/account/keys',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.data_list = data.list; //ssh키에 대한 정보
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.sshkey();
        $scope.sshkey_save=function(){
            $http({
                method: 'POST',
                url: '/api/kvm/account/keys',
                data:'{"name":"'+$("#sshkey_name").val()+'"}',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.sshkey();
                        $(':input').val('');
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.download = function (id) { //ssh키의 다운로드
            $http({
                method: 'GET',
                url: "/api/kvm/account/keys/download/"+id,
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8',
                }
            })
                .success(function (data, status, headers, config) {
                    var header = headers(); // We set Content-disposition with filename in Controller.
                    var fileName = header['content-disposition'].split("=")[1].replace(/\"/gi,'');
                    var blob = new Blob([data],
                        {type : 'application/octet-stream;charset=UTF-8'});
                    var objectUrl = (window.URL || window.webkitURL).createObjectURL(blob);
                    var link = angular.element('<a/>');
                    link.attr({
                        href : objectUrl,
                        download : "sshkey"
                    })[0].click();
                });
        };
        $scope.sshkey_delete = function (id,index) { //ssh키의 다운로드
            $http({
                method: 'DELETE',
                url: "/api/kvm//account/keys/"+id,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8',
                }
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        alert(name + "상태가 변경되었습니다");
                        $scope.data_list.splice(index, 1);
                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }
                });
        };
    });
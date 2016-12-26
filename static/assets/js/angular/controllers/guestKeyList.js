angular
    .module('gncloud')
    .controller('guestKeyListCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $scope.getkeys = function() {
            $http({
                method: 'GET',
                url: '/api/kvm/account/keys',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.data_list = data.list;
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


        $scope.update = function (id, index) {
            $http({
                method: 'DELETE',
                url: '/api/kvm/account/keys/' + id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    $scope.data_list.splice(index, 1);
                    alert("삭제되었습니다");
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
                        alert(data.message)
                    }
                });
        };

        $scope.download = function (id) {
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

        $scope.getkeys();

    });

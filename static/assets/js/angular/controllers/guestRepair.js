angular
    .module('gncloud')
    .controller('guestRepairCtrl', function ($scope, $http) {
        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $http({
            method: 'GET',
            url: '/Manager/vm/guestMeList',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.Me_list = data.list;

                } else {
                    alert(data.message);
                }

            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });
        $scope.submit = function() {
            $http({
                method  : 'PUT',
                url: '/api/manager/vm/account/users/list',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                }
            })
                .success(function(data) {
                    if (data.status == 2) {
                        alert("success");

                    }
                    else if(data.status == 1){
                        alert("비밀번호가 틀렸습니다");
                    }
                    else {
                        alert(data.message)
                    }
                });
        };


    });
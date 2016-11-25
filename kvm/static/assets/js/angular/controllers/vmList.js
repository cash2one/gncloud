angular
    .module('gncloud')
    .controller('vmListCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $scope.guest_list = {};

        $http({
            method: 'get', //방식
            url: '/gncloud/guest_list', /* 통신할 URL */
            headers: {'Content-Type': 'application/json; charset=utf-8'} //헤더
        })
            .success(function(data, status, headers, config) {
                if( data ) {
                    $scope.guest_list = data.list;
                }
                else {
                }
            })
            .error(function(data, status, headers, config) {
                console.log(status);
            });

        $scope.actions = [
            {name:'select'},
            {name:'reboot'},
            {name:'suspend'},
            {name:'resume'},
            {name:'delete'},
        ];

        $scope.myActions = $scope.actions[0];

        $scope.update = function(name, action, index) {
            $http({
                method: 'get',
                url:'/gncloud/change_status/'+name+'/'+action.name ,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    alert(name+" guest의 상태가 변경되었습니다");
                    $scope.guest_list.splice(index, 1);
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });

        }
    });
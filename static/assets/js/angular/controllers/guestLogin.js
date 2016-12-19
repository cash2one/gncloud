angular
    .module('gncloud')
    .controller('guestLoginCtrl', function ($scope, $http, $location) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');


        $scope.data = {};
        $scope.submit = function() {
            $http({
                method  : 'POST',
                url: '/api/manager/vm/account',
                data: $scope.data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data) {
                        if (data.test == 'yes') {
                            alert(data.message);
                            window.location.reload();
                        }else if(data.test =='no'){
                            alert(data.message);
                            window.location.reload();
                            $location.path('/guestSelectTeam');
                        }
                        else if(data.status ==false) {
                            alert(data.message);
                            window.location.reload();
                        }
                        else if(data.test =='noyes') {
                            alert(data.message);
                            window.location.reload();
                            $location.path('/guestReadyTeam');
                        }
                    })
                .error(function (data) {
                    alert(data.message);
                });


        };



    });
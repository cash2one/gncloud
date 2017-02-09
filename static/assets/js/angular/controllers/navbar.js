angular
    .module('gncloud')
    .controller('navbarCtrl', function ($scope, $http, $rootScope,$location) {
        $rootScope.$on('init', function () {
            $scope.user_info = $rootScope.user_info;
        });

        $scope.selected = 0;

        if($location.path() == "/dashboard"){
            $scope.selected = 1;
        }else if($location.path() == "/guestList" || $location.path() == "/guestDetail"){
            $scope.selected = 2;
        }else if($location.path() == "/guestServiceList" || $location.path() == "/guestSerivceDetail"){
            $scope.selected = 3;
        }else if($location.path() == "/guestSnapList"){
            $scope.selected = 4;
        }

        $scope.select= function(number) {
            $scope.selected = number;
        }
    });
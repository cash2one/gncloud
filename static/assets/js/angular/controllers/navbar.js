angular
    .module('gncloud')
    .controller('navbarCtrl', function ($scope, $http, $rootScope) {
        console.log("hello");
        $rootScope.$on('init', function () {
            $scope.user_info = $rootScope.user_info;
        });
        $scope.selected = 1;

        $scope.select= function(number) {
            $scope.selected = number;
        }
    });
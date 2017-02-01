angular
    .module('gncloud')
    .controller('navleftCtrl', function ($scope, $http, $rootScope) {
        $scope.selecte= function(number) {

            $scope.selected = number;
        }
    });
angular
    .module('gncloud')
    .controller('navbarCtrl', function ($scope, $http, $rootScope) {
        $rootScope.$on('init', function () {
            $scope.user_info = $rootScope.user_info;
        });
    });
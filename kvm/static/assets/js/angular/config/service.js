/**
 * Created by jhjeon on 2016-09-29.
 */

var serviceConfig = function ($routeProvider, $locationProvider) {

    $routeProvider
        .when('/main', {templateUrl: '/main.html', controller: 'mainCtrl'})
        .when('/vmList', {templateUrl: '/vmList.html', controller: 'vmListCtrl'})
        .when('/vmCreate', {templateUrl: '/vmCreate.html', controller: 'vmCreateCtrl'})
}

// 서비스 페이지 설정
angular
    .module('gncloud')
    .config(serviceConfig);

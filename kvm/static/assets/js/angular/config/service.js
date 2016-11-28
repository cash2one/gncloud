/**
 * Created by jhjeon on 2016-09-29.
 */

var serviceConfig = function ($routeProvider, $locationProvider) {

    $routeProvider
        .when('/main', {templateUrl: '/main.html', controller: 'mainCtrl'})
        .when('/guestList', {templateUrl: '/guestList.html', controller: 'guestListCtrl'})
        .when('/guestCreate', {templateUrl: '/guestCreate.html', controller: 'guestCreateCtrl'})
        .when('/guestSnapList', {templateUrl: '/guestSnapList.html', controller: 'guestSnapListCtrl'})
}

// 서비스 페이지 설정
angular
    .module('gncloud')
    .config(serviceConfig);

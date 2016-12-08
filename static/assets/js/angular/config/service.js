var serviceConfig = function ($routeProvider, $locationProvider) {

    /**
     * Created by jhjeon on 2016-09-29.
     */
    $routeProvider
        .when('/main', {templateUrl: '/main.html', controller: 'mainCtrl'})
        .when('/guestList', {templateUrl: '/guestList.html', controller: 'guestListCtrl'})
        .when('/guestCreate', {templateUrl: '/guestCreate.html', controller: 'guestCreateCtrl'})
        .when('/guestSnapList', {templateUrl: '/guestSnapList.html', controller: 'guestSnapListCtrl'})
        .when('/monitor', {templateUrl: '/guestRunList.html', controller: 'guestRunListCtrl'})
        .when('/guestLogin', {templateUrl: '/guestLogin.html', controller: 'guestLoginCtrl'})
        .when('/guestLogout', {templateUrl: '/index.html', controller: 'guestLogoutCtrl'})
        .when('/guestKeyList', {templateUrl: '/guestKeyList.html', controller: 'guestKeyListCtrl'})
        .when('/guestSnapCreate', {templateUrl: '/guestSnapCreate.html', controller: 'guestSnapCreateCtrl'})
}

// 서비스 페이지 설정
angular
    .module('gncloud')
    .config(serviceConfig);

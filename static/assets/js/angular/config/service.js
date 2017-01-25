var serviceConfig = function ($routeProvider, $httpProvider) {
    $routeProvider
        .when('/guestList', {templateUrl: '/main/guestList.html', controller: 'guestListCtrl'})
        .when('/guestCreate', {templateUrl: '/main/guestCreate.html', controller: 'guestCreateCtrl'})
        .when('/guestSnapList', {templateUrl: '/main/guestSnapList.html', controller: 'guestSnapListCtrl'})
        .when('/monitor', {templateUrl: '/main/guestRunList.html', controller: 'guestRunListCtrl'})
        .when('/account', {templateUrl: '/main/guestLogin.html', controller: 'guestLoginCtrl'})
        .when('/guestLogout', {templateUrl: '/main/index.html', controller: 'guestLogoutCtrl'})
        .when('/guestKeyList', {templateUrl: '/main/guestKeyList.html', controller: 'guestKeyListCtrl'})
        .when('/guestSnapCreate', {templateUrl: '/main/guestSnapCreate.html', controller: 'guestSnapCreateCtrl'})
        .when('/account/users/list', {templateUrl: '/main/guestMeList.html', controller: 'guestMeListCtrl'})
        .when('/account/users', {templateUrl: '/main/guestSignUp.html', controller: 'guestSignUpCtrl'})
        .when('/guestRepair', {templateUrl: '/main/guestRepair.html', controller: 'guestRepairCtrl'})
        .when('/dashboard', {templateUrl: '/main/dashboard.html', controller: 'dashboardCtrl'})
        .when('/guestDetail', {templateUrl: '/main/guestDetail.html', controller: 'guestDetailCtrl'})
        .when('/guestSelectTeam', {templateUrl: '/main/guestSelectTeam.html', controller: 'guestSelectTeamCtrl'})
        .when('/guestReadyTeam', {templateUrl: '/main/guestReadyTeam.html', controller: 'guestReadyTeamCtrl'})
        .when('/guestCreateTeam', {templateUrl: '/main/guestCreateTeam.html', controller: 'guestCreateTeamCtrl'})
        .when('/guestSystemList', {templateUrl: '/main/guestSystemList.html', controller: 'guestSystemListCtrl'})
        .when('/guestTeamDetail', {templateUrl: '/main/guestTeamDetail.html', controller: 'guestTeamDetailCtrl'})
        .when('/guestTeamList', {templateUrl: '/main/guestTeamList.html', controller: 'guestTeamListCtrl'})
        .when('/guestCluster', {templateUrl: '/main/guestCluster.html', controller: 'guestClusterCtrl'})
        .when('/guestImage', {templateUrl: '/main/guestImage.html', controller: 'guestImageCtrl'})
        .when('/guestPrice', {templateUrl: '/main/guestPrice.html', controller: 'guestPriceCtrl'})
        .when('/guestLoginHist', {templateUrl: '/main/guestLoginHist.html', controller: 'guestLoginHistCtrl'})
        .when('/guestSetting', {templateUrl: '/main/guestSetting.html', controller: 'guestSettingCtrl'})
        .when('/guestNotice', {templateUrl: '/main/guestNotice.html', controller: 'guestNoticeCtrl'})
        .when('/guestQna', {templateUrl: '/main/guestQna.html', controller: 'guestQnaCtrl'})
    $httpProvider.interceptors.push('serviceLogger');
}

// 서비스 페이지 설정
angular
    .module('gncloud')
    .config(serviceConfig);

var serviceAddModules = [
    'ngRoute'
    ,'ngFileUpload'
    ,'uiSwitch'
    ,'angularNotify'
];

(function () {

    var app = angular.module('gncloud', serviceAddModules);

    app.directive('navbar', function (){
        return{
            restrict: 'E',
            templateUrl:'/main/navbar.html',
            controller: function ($scope, $location) {

            }
        }
    });

    app.directive('navleft', function (){
        return{
            restrict: 'E',
            templateUrl:'/main/navleft.html',
            controller: function ($scope, $location) {
                if($location.path() == "/guestSystemList") $scope.menu = 1;
                if($location.path() == "/guestTeamList") $scope.menu = 2;
                if($location.path() == "/guestCluster") $scope.menu = 3;
                if($location.path() == "/guestImage") $scope.menu = 4;
                if($location.path() == "/guestPrice") $scope.menu = 5;
                if($location.path() == "/guestLoginHist") $scope.menu = 6;
                if($location.path() == "/guestUseHist") $scope.menu = 7;
                if($location.path() == "/guestBackupHist") $scope.menu = 8;
                if($location.path() == "/guestProblemHist") $scope.menu = 9;
                if($location.path() == "/guestInvoice") $scope.menu = 10;
                if($location.path() == "/guestSetting") $scope.menu = 11;
            }
        };
    });
    app.directive('navme', function (){
        return{
            restrict: 'E',
            templateUrl:'/main/navme.html',
            controller: function ($scope, $location) {
                if($location.path() == "/account/users/list") $scope.me_menu = 1;
                if($location.path() == "/guestTeamKey") $scope.me_menu = 2;
                if($location.path() == "/guestTeamProfile") $scope.me_menu = 3;
                if($location.path() == "/guestTeamReso") $scope.me_menu = 4;
                if($location.path() == "/guestTeamWon") $scope.me_menu = 5;
                if($location.path() == "/guestTeamBackup") $scope.me_menu = 6;
                if($location.path() == "/guestInvoice") $scope.me_menu = 7;
            }
        };
    });

    app.run(function($rootScope,$http){
        $http({
            method: 'GET',
            url: '/api/manager/vm/logincheck',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                $rootScope.user_info = data.info;
                $rootScope.$emit('init');
            })
            .error(function (data, status, headers, config) {
                console.log("checking success!!");
            });


    });

    app.factory('serviceLogger', function ($location) {
        return {
            responseError: function(response) {
                if(response.status == 401){
                    window.location ="/"
                }
                return response;
            },
        };
    });

    app.service('dateModifyService', function()
    {
        this.modifyDate = function(date)
        {
            var data_year = date.substring(0,4);
            var data_month = date.substring(5,7);
            var data_day = date.substring(8,10);
            var data_time = date.substring(11,13);
            var data_mins= date.substring(14,16);
            var date = new Date();
            var year  = date.getFullYear();
            var month = date.getMonth() + 1; // 0부터 시작하므로 1더함 더함
            var day   = date.getDate();
            var time   = date.getHours();
            var min = date.getMinutes();
            var dateDiff = "";
            if(data_year != year && month == data_month){
                dateDiff = (year-data_year)+"년 전";
            }else if(data_month != month){
                if(month-data_month>0){
                    dateDiff = (month-data_month)+"개월 전";
                }else{
                    dateDiff = (12-data_month)+month+"개월 전";
                    console.log(dateDiff);
                }

            }else if(data_day != day){
                dateDiff = (day-data_day)+"일 전";
            }else if(data_time != time){
                dateDiff = (time-data_time)+"시간 전";
            }else if(data_mins != min){
                dateDiff = (min-data_mins) +"분 전";
            }else{
                dateDiff = "1분 전";
            }
            return dateDiff
        };
    });

    app.service('notification', function($rootScope){
        this.sendMessage = function(data_type, data_title, data_contetnt) {
            var notify = {
                type: data_type,
                title: data_title,
                content: data_contetnt
            };
            $rootScope.$emit('notify', notify);
        }
    });

})();







var serviceAddModules = [
    'ngRoute'
];

(function () {
    var app = angular.module('gncloud', serviceAddModules);

    app.factory('serviceLogger', function ($location) {
        return {
            responseError: function(response) {
                if(response.status == 401){
                   alert("로그인이 필요합니다");
                   $location.url("/account");
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
            var date = new Date();
            var year  = date.getFullYear();
            var month = date.getMonth() + 1; // 0부터 시작하므로 1더함 더함
            var day   = date.getDate();
            var time   = date.getHours();
            var dateDiff = "";
            if(data_year != year){
                dateDiff = (year-data_year)+"년 전";
            }else if(data_month != month){
                dateDiff = (month-data_month)+"개월 전";
            }else if(data_day != day){
                dateDiff = (day-data_day)+"일 전";
            }else if(data_time != time){
                dateDiff = (time-data_time)+"시간 전";
            }
            return dateDiff
        };
    });
})();








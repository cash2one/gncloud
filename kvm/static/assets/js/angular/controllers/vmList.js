angular
    .module('gncloud')
    .controller('vmListCtrl', function ($scope, $http) {

        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        // 이메일 객체를 생성
        $scope.emails = {};

        // 서버에서 데이터를 받아온 것처럼 꾸며보자.
        // 그냥 객체의 배열이다.
        $scope.emails.messages = [{
            "from": "Steve Jobs",
            "subject": "I think I'm holding my phone wrong :/",
            "sent": "2013-10-01T08:05:59Z"
        }, {
            "from": "Ellie Goulding",
            "subject": "I've got Starry Eyes, lulz",
            "sent": "2013-09-21T19:45:00Z"
        }, {
            "from": "Michael Stipe",
            "subject": "Everybody hurts, sometimes.",
            "sent": "2013-09-12T11:38:30Z"
        }, {
            "from": "Jeremy Clarkson",
            "subject": "Think I've found the best car... In the world",
            "sent": "2013-09-03T13:15:11Z"
        }];
    });
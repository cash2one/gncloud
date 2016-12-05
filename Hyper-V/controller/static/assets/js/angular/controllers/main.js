angular
    .module('gncloud')
    .controller('mainCtrl', function ($scope, $http) {
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

    });
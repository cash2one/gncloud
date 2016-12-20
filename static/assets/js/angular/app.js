var serviceAddModules = [
    'ngRoute'
];

(function () {
    var app = angular.module('gncloud', serviceAddModules);
    app.factory('serviceLogger', function ($location) {
        return {
            request: function (config) {
                //$location.url("/account");
                return config;
            }
        };
    });
})();








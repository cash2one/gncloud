'use strict';


var app = angular.module('fileUpload', ['ngFileUpload']);
var version = '11.1.3';

app.controller('MyCtrl', ['$scope', '$http', 'Upload', function ($scope, $http, $timeout, $compile, Upload) {

    $scope.uploadPic = function (file) {
        $scope.formUpload = true;
        if (file != null) {
            $scope.upload(file);
        }
    };

    $scope.upload = function (file, resumable) {
        uploadUsing$http(file);
    };

    function uploadUsing$http(file) {
        file.upload = Upload.http({
            url: 'https://angular-file-upload-cors-srv.appspot.com/upload' + $scope.getReqParams(),
            method: 'POST',
            headers: {
                'Content-Type': file.type
            },
            data: file
        });

        file.upload.then(function (response) {
            file.result = response.data;
        }, function (response) {
            if (response.status > 0)
                $scope.errorMsg = response.status + ': ' + response.data;
        });
    }

}]);
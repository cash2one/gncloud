angular
    .module('gncloud')
    .controller('guestImageCtrl', function ($scope, $http, dateModifyService,$routeParams,Upload) {
        $("#container").hide();
        $scope.image=function(){
            $http({
                method: 'GET',
                url: '/api/manager/vm/images/base',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        for (var i = 0; i < data.list.guest_list.length; i++) {
                            data.list.guest_list[i].create_time_diff = dateModifyService.modifyDate(data.list.guest_list[i].create_time);
                        }

                        $scope.images_list = data.list.guest_list; //이미지 관리 리스트
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.image();
        $scope.contain=function(){
            $http({
                method: 'GET',
                url: '/api/manager/vm/container/services',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        for (var i = 0; i < data.list.length; i++) {
                            data.list[i].create_time_diff = dateModifyService.modifyDate(data.list[i].create_time);//날짜변경
                        }
                        $scope.contain_list = data.list;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }



        $scope.initForm = function (part) {
            if(part =="instance") $scope.instanceImage = {};
            if(part =="docker") $scope.dockerImage = {};
        };


        //이미지 저장
        $scope.uploadPic = function (file) {
            $scope.formUpload = true;
            if (file != null) {
                uploadUsingUpload(file);
            }else{
                saveInstanceImage()
            }
        };

        function uploadUsingUpload(file) {
            $scope.instanceImage.file = file;
            file.upload = Upload.upload({
                url: "/api/manager/vm/image/file",
                headers: {
                    'optional-header': 'header-value'
                },
                data: $scope.instanceImage
            });

            file.upload.then(function (response) {
                $scope.image();
                $scope.instanceImage = {};
            }, function (response) {

            }, function (evt) {

            });

        }

        function saveInstanceImage(){
            $http({
                method: "POST",
                url: '/api/manager/vm/image',
                data: $scope.instanceImage,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.image();
                        $scope.instanceImage = {};
                    }else{
                        if(data.message != null){
                            alert(data.message);
                        }
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }


        $scope.deleteInstanceImage = function(id){
            $http({
                method: 'DELETE',
                url: '/api/manager/vm/image/'+id,
                data: $scope.instanceImage,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.image();
                    }else{
                        if(data.message != null){
                            alert(data.message);
                        }
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.getInstanceImage = function(id){
            $('#icon_image').attr('src','');

            $http({
                method: 'GET',
                url: '/api/manager/vm/image/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.instanceImage = data.info;
                    }else{
                        if(data.message != null){
                            alert(data.message);
                        }
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }



        //docker 저장 로직
        $scope.uploadDocker = function (file) {
            $scope.formUpload = true;
            if (file != null) {
                uploadUsingUploadDocker(file);
            }else{
                saveInstanceImageDocker()
            }
        };

        function uploadUsingUploadDocker(file) {
            $scope.dockerImage.file = file;
            file.upload = Upload.upload({
                url: "/api/manager/vm/dockerimage/file",
                headers: {
                    'optional-header': 'header-value'
                },
                data: $scope.dockerImage
            });

            file.upload.then(function (response) {
                $scope.contain();
                $scope.instanceImage = {};
            }, function (response) {

            }, function (evt) {

            });

        }

        function saveInstanceImageDocker(){
            $http({
                method: "POST",
                url: '/api/manager/vm/dockerimage',
                data: $scope.dockerImage,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.contain();
                        $scope.dockerImage = {};
                    }else{
                        if(data.message != null){
                            alert(data.message);
                        }
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.getInstanceImageDocker = function(id){
            $('#icon_image').attr('src','');

            $http({
                method: 'GET',
                url: '/api/manager/vm/dockerimage/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.dockerImage = data.info;

                        for(var i=0; i < data.info.gnDockerImageDetail.length ; i++){
                            if(data.info.gnDockerImageDetail[i].arg_type == "mount"){
                                if($scope.dockerImage.vol != null) {
                                    $scope.dockerImage.vol += data.info.gnDockerImageDetail[i].argument + "\n";
                                }else{
                                    $scope.dockerImage.vol = data.info.gnDockerImageDetail[i].argument + "\n";
                                }
                            }

                            if(data.info.gnDockerImageDetail[i].arg_type == "port"){
                                if($scope.dockerImage.port != null) {
                                    $scope.dockerImage.port += data.info.gnDockerImageDetail[i].argument.replace("-p ","")+",";
                                }else{
                                    $scope.dockerImage.port = data.info.gnDockerImageDetail[i].argument.replace("-p ","")+",";
                                }
                            }

                            if(data.info.gnDockerImageDetail[i].arg_type == "env"){
                                if($scope.dockerImage.env != null) {
                                    $scope.dockerImage.env += data.info.gnDockerImageDetail[i].argument + "\n";
                                }else{
                                    $scope.dockerImage.env = data.info.gnDockerImageDetail[i].argument + "\n";
                                }
                            }
                        }

                        $scope.dockerImage.vol = $scope.dockerImage.vol.slice(0,-1)
                        $scope.dockerImage.port = $scope.dockerImage.port.slice(0,-1)
                        $scope.dockerImage.env = $scope.dockerImage.env.slice(0,-1)

                    }else{
                        if(data.message != null){
                            alert(data.message);
                        }
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.deleteInstanceImageDoker = function(id){
            $http({
                method: 'DELETE',
                url: '/api/manager/vm/dockerimage/'+id,
                data: $scope.dockerImage,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.contain();
                    }else{
                        if(data.message != null){
                            alert(data.message);
                        }
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.refresh = function(type){
            if(type == 'table'){
                $scope.table = Array.prototype.slice.call($scope.table).reverse();
            }else if(type =='contain'){
                $scope.contain_list = Array.prototype.slice.call($scope.contain_list).reverse();
            }else if(type == 'image'){
                $scope.paths = Array.prototype.slice.call($scope.paths).reverse();
            }

        }
        $scope.imageset = function(ty){
            if(ty == 'container'){
                $("#machine").hide();
                $("#container").fadeIn();
                $scope.contain();
            }
            else if(ty == 'machine'){
                $("#container").hide();
                $("#machine").fadeIn();
                $scope.image();
            }
        }

    }).directive('tooltip', function(){
        return {
            restrict: 'A',
            link: function(scope, element, attrs){
                $(element).hover(function(){
                    $(element).tooltip('show');
                }, function(){
                    $(element).tooltip('hide');
                });
            }
        };
    });

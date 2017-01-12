angular
    .module('gncloud')
    .controller('guestSystemListCtrl', function ($scope, $http, dateModifyService,$routeParams,Upload) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $("#container").hide();
        $("#team-sett").hide();
        $("#cluster-sett").hide();
        $("#image-sett").hide();
        $scope.table = {};
        $scope.teamtable=function(){
            $http({
                method: 'GET',
                url: '/api/manager/vm/account/teamtable',
                headers: {'Content-Type': 'application/json; charset=utf-8'} //시스템 관리자의 팀관리
            })
                .success(function (data, status, headers, config) {
                    if (data) {

                        var newArr = new Array();
                        for (var i = 0; i < data.list.length; i++) {
                            data.list[i].team_info.create_time_diff = dateModifyService.modifyDate(data.list[i].team_info.create_date); // 날짜 설정

                            var owner_id = "";
                            var owner_name = "";
                            var users = "";
                            var usersfirst ="";
                            var usersfirstid ="";
                            for (var j = 0; j < data.list[i].user_list.length; j++) {
                                if (data.list[i].user_list[j][0].team_owner == 'owner') { //팀장찾는 곳
                                    owner_id = "("+data.list[i].user_list[j][1].user_id+")";
                                    owner_name = data.list[i].user_list[j][1].user_name;

                                }else if(j==1){
                                    usersfirst = data.list[i].user_list[j][1].user_name;
                                    usersfirstid="("+data.list[i].user_list[j][1].user_id+")";
                                }else{
                                    users +=data.list[i].user_list[j][1].user_name+"("+data.list[i].user_list[j][1].user_id+")";
                                }

                            }

                            data.list[i].team_info.userslen = data.list[i].user_list.length > 0 ? (data.list[i].user_list.length - 1):0;
                            data.list[i].team_info.usersfirstid = usersfirstid;
                            data.list[i].team_info.usersfirst = usersfirst;
                            data.list[i].team_info.users = users;
                            data.list[i].team_info.owner_id = owner_id;
                            data.list[i].team_info.owner_name = owner_name;
                            data.list[i].team_info.cpu_use_per = data.list[i].quto_info.cpu_per[0];
                            data.list[i].team_info.cpu_use_cnt = data.list[i].quto_info.cpu_cnt[0];
                            data.list[i].team_info.cpu_tot_cnt = data.list[i].quto_info.cpu_cnt[1];
                            data.list[i].team_info.mem_use_per = data.list[i].quto_info.mem_per[0];
                            data.list[i].team_info.mem_use_cnt = data.list[i].quto_info.mem_cnt[0];
                            data.list[i].team_info.mem_tot_cnt = data.list[i].quto_info.mem_cnt[1];
                            data.list[i].team_info.disk_use_per = data.list[i].quto_info.disk_per[0];
                            data.list[i].team_info.disk_use_cnt = data.list[i].quto_info.disk_cnt[0];
                            data.list[i].team_info.disk_tot_cnt = data.list[i].quto_info.disk_cnt[1];
                            newArr.push(data.list[i].team_info);
                        }

                        $scope.table = newArr;


                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.diskusage=function(code){
            $http({
                method: 'GET',
                url: '/api/manager/vm/account/teamtable/'+code,
                headers: {'Content-Type': 'application/json; charset=utf-8'} //시스템 관리자의 팀관리
            })
                .success(function (data, status, headers, config) {
                    if (data) {

                        data.list[0].team_info.create_time_diff = dateModifyService.modifyDate(data.list[0].team_info.create_date); // 날짜 설정
                        var owner_id = "";
                        var owner_name = "";
                        var users = "";
                        var usersfirst = "";
                        var usersfirstid = "";
                        for (var j = 0; j < data.list[0].user_list.length; j++) {
                            if (data.list[0].user_list[j][0].team_owner == 'owner') { //팀장찾는 곳
                                owner_id = "(" + data.list[0].user_list[j][1].user_id + ")";
                                owner_name = data.list[0].user_list[j][1].user_name;

                            }else {
                                users += data.list[0].user_list[j][1].user_name + "(" + data.list[0].user_list[j][1].user_id + ")";
                            }
                            data.list[0].team_info.userslen = data.list[0].user_list.length > 0 ? (data.list[0].user_list.length - 1) : 0;
                            data.list[0].team_info.users = users;
                            data.list[0].team_info.owner_id = owner_id;
                            data.list[0].team_info.owner_name = owner_name;
                            data.list[0].team_info.cpu_use_per = data.list[0].quto_info.cpu_per[0];
                            data.list[0].team_info.cpu_use_cnt = data.list[0].quto_info.cpu_cnt[0];
                            data.list[0].team_info.cpu_tot_cnt = data.list[0].quto_info.cpu_cnt[1];
                            data.list[0].team_info.mem_use_per = data.list[0].quto_info.mem_per[0];
                            data.list[0].team_info.mem_use_cnt = data.list[0].quto_info.mem_cnt[0];
                            data.list[0].team_info.mem_tot_cnt = data.list[0].quto_info.mem_cnt[1];
                            data.list[0].team_info.disk_use_per = data.list[0].quto_info.disk_per[0];
                            data.list[0].team_info.disk_use_cnt = data.list[0].quto_info.disk_cnt[0];
                            data.list[0].team_info.disk_tot_cnt = data.list[0].quto_info.disk_cnt[1];
                        }


                        $scope.select = data.list[0].team_info;
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
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

        $scope.getCluster=function(){
            $http({
                method: 'GET',
                url: '/api/manager/vm/host',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.cluster_list = data.info;
                        for (var i = 0; i < $scope.cluster_list.length; i++) {
                            $scope.cluster_list[i].create_time_diff = dateModifyService.modifyDate(data.info[i].create_time);
                        }
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
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
        $scope.click=function(ty){
            if(ty == 'profile-system') {
                $("#profile-system").fadeIn();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
            }
            else if(ty == 'team-sett'){
                $("#profile-system").hide();
                $("#team-sett").fadeIn();
                $("#cluster-sett").hide();
                $("#image-sett").hide();
                $scope.teamtable();
            }
            else if(ty =='cluster-sett'){
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").fadeIn();
                $("#image-sett").hide();
                $scope.getCluster();
            }
            else if(ty =='image-sett'){
                $("#profile-system").hide();
                $("#team-sett").hide();
                $("#cluster-sett").hide();
                $("#image-sett").fadeIn();
                $scope.image();
            }
        }

        $scope.click($routeParams.id);
        $scope.refresh = function(type){
            if(type == 'table'){
                $scope.table = Array.prototype.slice.call($scope.table).reverse();
            }else if(type =='contain'){
                $scope.contain_list = Array.prototype.slice.call($scope.contain_list).reverse();
            }else if(type == 'image'){
                $scope.paths = Array.prototype.slice.call($scope.paths).reverse();
            }

        }


        $scope.initForm = function (part) {
            if(part =="instance") $scope.instanceImage = {};
            if(part =="docker") $scope.dockerImage = {};
        };
        //인스턴스 저장 로직
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

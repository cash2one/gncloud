angular
    .module('gncloud')
    .controller('guestQnaCtrl', function ($scope, $http, $rootScope, notification) {
        $scope.user_info = $rootScope.user_info;
        $scope.showData=1;
        $rootScope.$on('init', function () {
            $scope.user_info = $rootScope.user_info;
        });
        $scope.data={};
        $scope.qna_list = function (page) {
            $scope.data.page=page;
            $http({
                method: 'GET',
                url: '/api/manager/vm/qna',
                params:$scope.data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.list = data.list.list;
                        $scope.team = data.list.team_info;
                        $scope.total_page=data.list.total_page;
                        $scope.page_hist =data.list.page+1;
                        $scope.page_total =data.list.total+1;
                        $scope.prev_page = page - 1;
                        $scope.next_page = page + 1;
                        $scope.this_page = data.list.page*10;
                    }else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        };
        $scope.qna_list(1);
        $scope.qna_info=function (id,page) {
            $http({
                method: 'GET',
                url: '/api/manager/vm/qna/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.notice = data.list.qna_info;
                        $scope.reply = data.list.qna_ask;
                        $scope.qna_list(page);
                        $scope.checkid = id;
                    }else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })

        }
        $scope.qna_create=function () {
            $http({
                method: 'POST',
                url: '/api/manager/vm/qna',
                data:$scope.data
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.qna_list($scope.data.page);
                        notification.sendMessage("success","등록되었습니다.");
                        $scope.data.title="";$scope.data.text="";
                    }else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })

        }
        $scope.qna_reply_create=function (id) {
            $http({
                method: 'POST',
                url: '/api/manager/vm/qna/'+id,
                data:$scope.data
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.qna_list($scope.data.page);
                        $scope.qna_info(id,$scope.data.page);
                        $scope.data.reply_text="";
                    }else {
                        $scope.check_list = data.showData;
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })

        }
        $scope.changeqna=function (id, text) {
            $scope.data.text=text;
            $http({
                method:'PUT',
                url:'/api/manager/vm/qna/'+id,
                data:$scope.data
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.qna_list($scope.data.page);
                        $scope.data.text="";
                    }else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        }
        $scope.changereply=function (id, text) {
            $scope.data.text=text;
            $http({
                method:'PUT',
                url:'/api/manager/vm/qna/ask/'+id,
                data:$scope.data
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.qna_list($scope.data.page);
                        $scope.data.text="";
                    }else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        }
        $scope.deleteqna=function (id) {
            var returnvalue = confirm("글을 삭제하시겠습니까?");
            if(returnvalue==true){
                $http({
                    method:'DELETE',
                    url: '/api/manager/vm/qna/'+id
                })
                    .success(function (data, status, headers, config) {
                        if (data.status == true) {
                            $scope.qna_list($scope.data.page);
                            notification.sendMessage("success", "삭제되었습니다.");


                        }else {
                            if (data.message != null) {
                                alert(data.message);
                            }
                        }

                    })
            }

        }
        $scope.delete_reply=function (id) {
            var returnvalue = confirm("댓글을 삭제하시겠습니까?");
            if(returnvalue ==true){
                $http({
                    method:'DELETE',
                    url: '/api/manager/vm/qna/ask/'+id
                })
                    .success(function (data, status, headers, config) {
                        if (data.status == true) {
                            $scope.qna_info($scope.checkid,$scope.data.page);


                        }else {
                            if (data.message != null) {
                                alert(data.message);
                            }
                        }

                    })
            }

        }
        $scope.close=function () {
            $("#title").val('');
            $("#text").val('');
            $("#replytext").val('');
        }
    });

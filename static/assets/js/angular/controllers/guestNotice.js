angular
    .module('gncloud')
    .controller('guestNoticeCtrl', function ($scope, $http, $rootScope) {
        $scope.user_info = $rootScope.user_info;
        $scope.showData=2;
        $rootScope.$on('init', function () {
            $scope.user_info = $rootScope.user_info;
        });
        $scope.data={};
        $scope.noticeList = function (page) {
            $scope.data.page=page;
            $http({
                method: 'GET',
                url: '/api/manager/vm/notice',
                params:$scope.data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.list = data.list.list;
                        $scope.total_page=data.list.total_page;
                        $scope.page_hist =data.list.page+1;
                        $scope.page_total =data.list.total+1;
                        $scope.prev_page = page - 1;
                        $scope.next_page = page + 1;
                        $scope.this_page = data.list.page *10;

                    }else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        };
        $scope.noticeList(1);
        $scope.notice_lnfo=function (id,page) {
            $http({
                method: 'GET',
                url: '/api/manager/vm/notice/'+id,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.notice = data.list;
                        $scope.noticeList(page);
                    }else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })

        }
        $scope.notice_create=function () {
            $http({
                method: 'POST',
                url: '/api/manager/vm/notice',
                data:$scope.data
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.noticeList($scope.data.page);
                        $scope.data.title="";$scope.data.text="";
                    }else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })

        }
        $scope.changetext=function (id, text) {
            $scope.data.text1=text;
            $scope.data.id=id;
            $http({
                method:'PUT',
                url:'/api/manager/vm/notice',
                data:$scope.data
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.noticeList($scope.data.page);
                        alert("수정 되었습니다.");
                    }else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        }
        $scope.deletenoti=function (id) {
            $http({
                method:'DELETE',
                url: '/api/manager/vm/notice/'+id
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.noticeList($scope.data.page);
                        alert("삭제 되었습니다.");


                    }else {
                        if (data.message != null) {
                            alert(data.message);
                        }
                    }

                })
        }
        $scope.close=function () {
            $("#title").val('');
            $("#text").val('');
        }
    });
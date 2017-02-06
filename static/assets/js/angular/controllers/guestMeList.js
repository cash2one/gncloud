angular
    .module('gncloud')
    .controller('guestMeListCtrl', function ($scope, $http, dateModifyService, $rootScope) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $scope.close=function () {
            $(':input').val('');
        }
        $scope.profile=function(){
            $http({
                method: 'GET',
                url: '/api/manager/vm/account/users/list',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        $scope.te_list = data.list; // 유저 부분 리스트

                    } else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }

                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.profile();



        $scope.submit = function() {
            $http({
                method  : 'PUT',
                url: '/api/manager/vm/account/users/list',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8' // 개인설정 비밀번호 변경등
                }
            })
                .success(function(data) {
                    if (data.status == 2) {
                        alert("변경되었습니다.");
                        $scope.profile();
                        $(':input').val('');
                    }
                    else if(data.status == 1){
                        alert("비밀번호가 틀렸습니다");
                    }
                    else {
                        if(data.message != null) {
                            alert(data.message)
                        }
                    }
                });
        };



            $scope.user_info = $rootScope.user_info;

            $rootScope.$on('init', function () {
                $scope.user_info = $rootScope.user_info;
            });
            $scope.refresh = function () {
                $scope.won_list = Array.prototype.slice.call($scope.won_list).reverse();
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
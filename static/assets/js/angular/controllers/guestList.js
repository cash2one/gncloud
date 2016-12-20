angular
    .module('gncloud')
    .controller('guestListCtrl', function ($scope, $http, dateModifyService) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $('[data-toggle="tooltip"]').tooltip();

        $scope.guest_list = {};

        $http({
            method: 'GET',
            url: '/api/manager/vm/machines',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    $scope.guest_list = data.list;

                    for(var i = 0 ; i < data.list.length ; i++){
                        var tagArr = data.list[i].tag.split(",");
                        if(tagArr.length - 1 > 0 ) {
                            $scope.guest_list[i].tagFirst = tagArr[0];
                            $scope.guest_list[i].tagcount = "+" + (tagArr.length - 1);
                        }else{
                            $scope.guest_list[i].tagFirst = data.list[i].tag;
                        }
                        $scope.guest_list[i].create_time_diff = dateModifyService.modifyDate(data.list[i].create_time);
                    }

                } else {
                    alert(data.message);
                }

            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

        $scope.actions = [
            {name: '시작', type: 'resume'},
            {name: '정지', type: 'suspend'},
            {name: '재시작', type: 'reboot'}
        ];

        $scope.update = function (id, action, index) {
            $http({
                method: "PUT",
                url: "/api/kvm/vm/machines/" + id,
                data: action,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        alert(name + " guest의 상태가 변경되었습니다");
                    } else {
                        alert(data.message);
                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });

        }

        $scope.refresh = function(){
            $scope.guest_list = Array.prototype.slice.call($scope.guest_list).reverse();
        }
    });
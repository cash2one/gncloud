angular
    .module('gncloud')
    .controller('guestListCtrl', function ($scope, $http) {

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
                        //태그 카운팅
                        var count = data.list[i].tag.split(",");
                        if(count.length - 1 > 0 ) {
                            $scope.guest_list[i].tagFirst = count[0];
                            $scope.guest_list[i].tagcount = "+" + (count.length - 1);
                        }

                        //날짜 카운팅
                        $scope.guest_list[i].create_time_diff = data.list[i].create_time;
                        var data_year = data.list[i].create_time.substring(0,4);
                        var data_month = data.list[i].create_time.substring(5,7);
                        var data_day = data.list[i].create_time.substring(8,10);
                        var data_time = data.list[i].create_time.substring(11,13);
                        var date = new Date();
                        var year  = date.getFullYear();
                        var month = date.getMonth() + 1; // 0부터 시작하므로 1더함 더함
                        var day   = date.getDate();
                        var time   = date.getHours();
                        var dateDiff = "";
                        if(data_year != year){
                            dateDiff = (year-data_year)+"년 전";
                        }else if(data_month != month){
                            dateDiff = (month-data_Month)+"개월 전";
                        }else if(data_day != day){
                            dateDiff = (day-data_day)+"일 전";
                        }else if(data_time != time){
                            dateDiff = (time-data_time)+"시간 전";
                        }
                        $scope.guest_list[i].create_time_diff = dateDiff;
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
            var url = '/api/kvm/vm/machines/' + id;
            var method = "PUT";
            if (action.type == "delete") {
                url = '/api/kvm/vm/machines/' + id;
                method = 'DELETE';
            }

            $http({
                method: method,
                url: url,
                data: action,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function(data, status, headers, config) {
                    if (data.status == true) {
                        alert(name + " guest의 상태가 변경되었습니다");
                        window.location.reload();
                        $scope.guest_list.splice(index, 1);
                    } else {
                        alert(data.message);
                    }
                })
                .error(function(data, status, headers, config) {
                    console.log(status);
                });

        }

        $scope.refresh = function(){

        }
    });
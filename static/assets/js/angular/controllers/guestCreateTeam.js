angular
    .module('gncloud')
    .controller('guestCreateTeamCtrl', function ($scope, $http,$rootScope, $event) {
        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');
        $("#i").hide();
        $("#t").hide();
        $scope.submit = function() {
            $http({
                method  : 'POST',
                url: '/api/manager/vm/account/createteam',
                data: $scope.data,
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                }
            })
                .success(function(data) {
                    if (data.test == 'success') {
                        alert("팀생성이 완료되었습니다.");
                        $rootScope.user_info.team_code = $scope.data.team_code;
                        $rootScope.$emit('init');
                        window.location="/main/#/dashboard"
                    } else if(data.test == 'id'){
                        $("#i").hide();
                        $("#t").show();
                    }else if(data.test == 'team'){
                        $("#i").show();
                        $("#t").hide();
                    }
                });
        };

        $scope.keyup = function(){
            if($event.keyCode == '13'){
                submit();
            }
        }
    });
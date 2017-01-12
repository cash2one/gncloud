angular
    .module('gncloud')
    .controller('guestCreateTeamCtrl', function ($scope, $http,$rootScope) {
        //탭이동
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
    });
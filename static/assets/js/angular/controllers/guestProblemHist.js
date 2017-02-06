angular
    .module('gncloud')
    .controller('guestProblemHistCtrl', function ($scope, $http) {
        var d = new Date();

        $scope.data={"year":d.getFullYear(),"month":(d.getMonth() + 1), "solve":true, "notsolve":true};
        $scope.month_list = [
            {value: 1},
            {value: 2},
            {value: 3},
            {value: 4},
            {value: 5},
            {value: 6},
            {value: 7},
            {value: 8},
            {value: 9},
            {value: 10},
            {value: 11},
            {value: 12}
        ];
        $scope.year_list = [
            {name: d.getFullYear() - 1 , value: d.getFullYear() - 1},
            {name: d.getFullYear(), value: d.getFullYear()}
        ];


        $scope.page=function(page) {
            $scope.data.page=page;
            $http({
                method: 'GET',
                url: '/api/manager/vm/errorhist',
                params:$scope.data//,
                //headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.error_hist = data.list.list;
                        $scope.total_count = data.list.total_count;
                        $scope.solve_count = data.list.solve_count;
                        $scope.not_solve_count = data.list.not_solve_count;
                        $scope.page_hist =data.list.page+1;
                        $scope.page_total =data.list.total+1;
                        $scope.prev_page = page - 1;
                        $scope.next_page = page + 1;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }
        $scope.page(1);

        $scope.select_error_info=function(id) {
            $http({
                method: 'GET',
                url: '/api/manager/vm/errorhist/'+id,
                params:$scope.select_data,
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.error_info = data.info;
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.checkAll = function () {
            if ($scope.selectedAll) {
                $scope.selectedAll = true;
            } else {
                $scope.selectedAll = false;
            }
            angular.forEach($scope.error_hist, function (item) {
                item.Selected = $scope.selectedAll;
            });
        };

        $scope.save_one=function(id) {
            $http({
                method: 'PUT',
                url: '/api/manager/vm/errorhist',
                data:'{"id":"'+$scope.error_info.id+'","solve_content":"'+$scope.error_info.solve_content+'"}',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.page($scope.data.page);
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.save_all=function() {
            var checkArr = new Array();
            for(var i = 0 ;i < $scope.error_hist.length ; i++){
                if($scope.error_hist[i].Selected == true && $scope.error_hist[i].solver_id == null){
                    checkArr.push($scope.error_hist[i].id);
                }
            }

            $http({
                method: 'PUT',
                url: '/api/manager/vm/errorhist_all',
                data:'{"id_selected":['+checkArr+'],"solve_content":"'+$scope.error_info.solve_content+'"}',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data) {
                        $scope.page($scope.data.page);
                    }
                    else {
                    }
                })
                .error(function (data, status, headers, config) {
                    console.log(status);
                });
        }

        $scope.check_checklist = function(){
            $scope.error_info = {};
            var count = 0;
            for(var i = 0 ;i < $scope.error_hist.length ; i++){
                if($scope.error_hist[i].Selected == true && $scope.error_hist[i].solver_id == null){
                    count++;
                }
            }
            if(count == 0 ){
                alert("처리할 장애목록을 체크해주세요.");
            }else{
                $("#modal-error-arr").modal('show');
            }
        }
    });
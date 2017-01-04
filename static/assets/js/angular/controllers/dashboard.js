angular
    .module('gncloud')
    .controller('dashboardCtrl', function ($scope, $http, $rootScope) {
        $http({
            method: 'GET',
            url: '/api/manager/useinfo',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    new Chart(document.getElementById("cpu_chart").getContext("2d"), $scope.getConfig(data.list.cpu_per, "cpu"));
                    new Chart(document.getElementById("mem_chart").getContext("2d"), $scope.getConfig(data.list.mem_per, "mem"));
                    new Chart(document.getElementById("disk_chart").getContext("2d"), $scope.getConfig(data.list.disk_per, "disk"));
                    new Chart(document.getElementById("status_chart").getContext("2d"), $scope.getConfig(data.list.vm_count, "status"));
                    new Chart(document.getElementById("type_chart").getContext("2d"), $scope.getConfig(data.list.vm_type, "type"));
                    $scope.team_name = data.list.team_name;
                    $scope.cpu_use_per = data.list.cpu_per[0];
                    $scope.cpu_use_cnt = data.list.cpu_cnt[0];
                    $scope.cpu_tot_cnt = data.list.cpu_cnt[1];
                    $scope.mem_use_per = data.list.mem_per[0];
                    $scope.mem_use_cnt = data.list.mem_cnt[0];
                    $scope.mem_tot_cnt = data.list.mem_cnt[1];
                    $scope.disk_use_per = data.list.disk_per[0];
                    $scope.disk_use_cnt = data.list.disk_cnt[0];
                    $scope.disk_tot_cnt = data.list.disk_cnt[1];
                    $scope.docker_cnt = data.list.docker_info;
                    $scope.hyperv_cnt = data.list.vm_type[1];
                    $scope.kvm_cnt = data.list.vm_type[0];
                    $scope.kvm_per = data.list.vm_kvm_per;
                    $scope.hyperv_per = data.list.vm_hyperv_per;
                    $scope.run_cnt = data.list.vm_count[0];
                    $scope.stop_cnt = data.list.vm_count[1];
                    $scope.tot_cnt = data.list.vm_count[0] + data.list.vm_count[1];
                    $scope.team_user_count = data.list.team_user_count;
                    $scope.user_list=data.list.user_list;
                    for (var i = 0; i < data.list.user_list.length; i++) {
                        $scope.user_list[i].user_id = data.list.user_list[i][0];
                        $scope.user_list[i].user_name = data.list.user_list[i][1];
                        $scope.user_list[i].cnt = data.list.user_list[i][2];
                    }
                    $scope.image_type_list=data.list.image_type_list;
                    for (var i = 0; i < data.list.image_type_list.length; i++) {
                        $scope.image_type_list[i].name = data.list.image_type_list[i][0];
                        $scope.image_type_list[i].cnt = data.list.image_type_list[i][1];
                    }

                }
                else {
                    if(data.message != null) {
                        alert(data.message)
                    }
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

        $scope.getConfig = function (data, type) {
            var config = null;
            var rgb1 = null;
            var rgb2 = "rgb(204, 204, 204)";
            if(type == 'cpu'){
                rgb1 = "rgb(255, 167, 22)"
            }else if(type == 'mem'){
                rgb1 = "rgb(83, 200, 173)"
            }else if(type == 'disk'){
                rgb1 = "rgb(87, 161, 246)"
            }


            if (type == 'cpu' || type == 'mem' || type == 'disk' ) {
                config = {
                    type: 'doughnut',
                    data: {
                        datasets: [{
                            data: data,
                            backgroundColor: [
                                rgb1,
                                rgb2
                            ],
                        }],
                        labels: [
                            "사용중",
                            "미사용"
                        ]
                    },
                    options: {
                        responsive: true,
                        legend: true
                    }
                }
            }else if (type == 'status') {
                config = {
                    type: 'doughnut',
                    data: {
                        datasets: [{
                            data: data,
                            backgroundColor: [
                                "rgb(252, 204, 112)",
                                "rgb(226, 117, 96)"
                            ],
                        }],
                        labels: [
                            "실행",
                            "정지"
                        ]
                    },
                    options: {
                        responsive: true,
                        legend: true
                    }
                }
            }else if (type == 'type') {
                config = {
                    type: 'doughnut',
                    data: {
                        datasets: [{
                            data: data,
                            backgroundColor: [
                                "rgb(83, 200, 173)",
                                "rgb(59, 92, 145)"
                            ],
                        }],
                        labels: [
                            "kvm",
                            "hiperv"
                        ]
                    },
                    options: {
                        responsive: true,
                        legend: true
                    }
                }
            }
            return config;
        }


    });
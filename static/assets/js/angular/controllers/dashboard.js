angular
    .module('gncloud')
    .controller('dashboardCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        $http({
            method: 'GET',
            url: '/api/manager/useinfo',
            headers: {'Content-Type': 'application/json; charset=utf-8'}
        })
            .success(function (data, status, headers, config) {
                if (data.status == true) {
                    new Chart(document.getElementById("cpu_chart").getContext("2d"), $scope.getConfig(data.list.cpu_per, "quota"));
                    new Chart(document.getElementById("mem_chart").getContext("2d"), $scope.getConfig(data.list.mem_per, "quota"));
                    new Chart(document.getElementById("disk_chart").getContext("2d"), $scope.getConfig(data.list.disk_per, "quota"));
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
                    $scope.run_cnt = data.list.vm_count[0];
                    $scope.stop_cnt = data.list.vm_count[1];
                    $scope.tot_cnt = data.list.vm_count[0] + data.list.vm_count[1];
                    $scope.team_user_count = data.list.team_user_count;
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
            if (type == 'quota') {
                config = {
                    type: 'doughnut',
                    data: {
                        datasets: [{
                            data: data,
                            backgroundColor: [
                                "rgb(233, 30, 99)",
                                "rgb(204, 204, 204)"
                            ],
                        }],
                        labels: [
                            "사용중",
                            "미사"
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
                                "rgb(233, 30, 99)",
                                "rgb(255, 193, 7)"
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
                                "rgb(233, 30, 99)",
                                "rgb(255, 193, 7)"
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
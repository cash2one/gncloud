angular
    .module('gncloud')
    .controller('guestTeamResoCtrl', function ($scope, $http, dateModifyService, $rootScope) {
        $scope.reso = function () {
            //**********리소스*************//
            $http({
                method: 'GET',
                url: '/api/manager/useinfo',
                headers: {'Content-Type': 'application/json; charset=utf-8'}
            })
                .success(function (data, status, headers, config) {
                    if (data.status == true) {
                        new Chart(document.getElementById("cpu_chart").getContext("2d"), $scope.getConfig(data.list.cpu_per, "cpu"));
                        new Chart(document.getElementById("memory_chart").getContext("2d"), $scope.getConfig(data.list.mem_per, "mem"));
                        new Chart(document.getElementById("disk_chart").getContext("2d"), $scope.getConfig(data.list.disk_per, "disk"));

                        $("#cpu_per").html(data.list.cpu_per[0]);
                        $("#cpu_use_cnt").html(data.list.cpu_cnt[0]);
                        $("#cpu_total_cnt").html(data.list.cpu_cnt[1]);
                        $("#mem_per").html(data.list.mem_per[0]);
                        $("#mem_use_cnt").html(data.list.mem_cnt[0]);
                        $("#mem_total_cnt").html(data.list.mem_cnt[1]);
                        $("#disk_per").html(data.list.disk_per[0]);
                        $("#disk_use_cnt").html(data.list.disk_cnt[0]);
                        $("#disk_total_cnt").html(data.list.disk_cnt[1]);
                    }
                    else {
                        if (data.message != null) {
                            notification.sendMessage("error",data.message);
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
                if (type == 'cpu') {
                    rgb1 = "rgb(255, 167, 22)"
                } else if (type == 'mem') {
                    rgb1 = "rgb(83, 200, 173)"
                } else if (type == 'disk') {
                    rgb1 = "rgb(87, 161, 246)"
                }


                if (type == 'cpu' || type == 'mem' || type == 'disk') {
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
                }
                return config;
            }
        }
        $scope.reso();

    });

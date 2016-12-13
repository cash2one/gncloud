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
                    new Chart(document.getElementById("memory_chart").getContext("2d"), $scope.getConfig(data.list.memory_per, "quota"));
                    new Chart(document.getElementById("disk_chart").getContext("2d"), $scope.getConfig(data.list.disk_per, "quota"));
                    new Chart(document.getElementById("status_chart").getContext("2d"), $scope.getConfig(data.list.vm_count, "status"));
                    new Chart(document.getElementById("type_chart").getContext("2d"), $scope.getConfig(data.list.vm_type, "type"));
                }
                else {
                    alert(data.message)
                }
            })
            .error(function (data, status, headers, config) {
                console.log(status);
            });

        $scope.getConfig = function (data, type) {
            var config = null;
            if (type == 'quota') {
                config = {
                    type: 'pie',
                    data: {
                        datasets: [{
                            data: data,
                            backgroundColor: [
                                "rgb(233, 30, 99)",
                                "rgb(255, 193, 7)"
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
                    type: 'pie',
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
                    type: 'pie',
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
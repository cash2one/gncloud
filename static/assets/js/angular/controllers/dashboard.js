angular
    .module('gncloud')
    .controller('dashboardCtrl', function ($scope, $http) {

        //탭이동
        $('.nav-sidebar li').removeClass('active');
        var url = window.location;
        $('ul.nav-sidebar a').filter(function () {
            return this.href.indexOf(url.hash) != -1;
        }).parent().addClass('active');

        config = {
            type: 'pie',
            data: {
                datasets: [{
                    data: [225, 50, 100, 40],
                    backgroundColor: [
                        "rgb(233, 30, 99)",
                        "rgb(255, 193, 7)",
                        "rgb(0, 188, 212)",
                        "rgb(139, 195, 74)"
                    ],
                }],
                labels: [
                    "Pink",
                    "Amber",
                    "Cyan",
                    "Light Green"
                ]
            },
            options: {
                responsive: true,
                legend: true
            }
        }

        new Chart(document.getElementById("cpu_chart").getContext("2d"), config);
        new Chart(document.getElementById("memory_chart").getContext("2d"), config);
        new Chart(document.getElementById("disk_chart").getContext("2d"), config);
        new Chart(document.getElementById("kvm_chart").getContext("2d"), config);
        new Chart(document.getElementById("hiperv_chart").getContext("2d"), config);
    });
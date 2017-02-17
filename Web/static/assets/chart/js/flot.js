var data = [], totalPoints = 110;
var updateInterval = 320;
var realtime = 'on';

$(function () {
    //Real time ==========================================================================================
    var plot = $.plot('#real_time_chart', [getRandomData()], {
        series: {
            shadowSize: 0,
            color: 'rgb(0, 188, 212)'
        },
        grid: {
            borderColor: '#f3f3f3',
            borderWidth: 1,
            tickColor: '#f3f3f3'
        },
        lines: {
            fill: true
        },
        yaxis: {
            min: 0,
            max: 100
        },
        xaxis: {
            min: 0,
            max: 10
        }
    });

    function updateRealTime() {
        plot.setData([getRandomData()]);
        plot.draw();

        var timeout;
        if (realtime === 'on') {
            timeout = setTimeout(updateRealTime, 1000);
        } else {
            clearTimeout(timeout);
        }
    }

    updateRealTime();

    $('#realtime').on('change', function () {
        realtime = this.checked ? 'on' : 'off';
        updateRealTime();
    });
    //====================================================================================================

});

var res = [];
var cnt = 0;
for (var i = 0; i < 11 ; i++) {
        res.push([i,i*10]);
}
function getRandomData() {
    var arr=[]
    for(var i = 1; i < 11 ; i++){
        arr.push([i-1,res[i][1]]);
    }
    arr.push([11,Math.random()*100]);
    res=arr;
    return arr;
}




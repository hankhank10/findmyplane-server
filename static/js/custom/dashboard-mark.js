refreshData();


function refreshData() {

    $.getJSON("https://findmyplane.live/stats", function(data) {
        //window.alert(data.now.current_planes)
        $('#current_planes').text(data.now.current_planes)
    })

    $.getJSON("https://findmyplane.live/stats/history/new_plane/day/0/1", function(data) {
        $('#planes_today').text(data[0].value)
        $('#planes_yesterday').text(data[1].value)
    })

    $.getJSON("https://findmyplane.live/stats/history/location_update/24H/0/1", function(data) {

        $('#updates_last_24_hours').text(Math.round(data[0]/1000)+"k")
        $('#updates_24_hours_before_that').text(Math.round(data[0]/1000)+"k")

    })

    $.getJSON("https://findmyplane.live/stats/history/location_update/hour/25/72", function(data) {
        
        let counter = 0;
        for (i = 0; i < data.length; i++) {
            counter = counter + data[i].value
        }
        $('#updates_24_hours_before_that').text(Math.round(counter/1000)+"k")
    })

    $.getJSON("https://findmyplane.live/stats/history/location_update/day/0/1", function(data) {
        $('#updates_today').text(Math.round(data[0].value/1000)+"k")
        $('#updates_yesterday').text(Math.round(data[1].value/1000)+"k")
    })


    var d = new Date();
    var percentage_through_hour = d.getMinutes() / 60
    //alert(percentage_through_hour);

    $.getJSON("https://findmyplane.live/stats/history/location_update/hour/0/1", function(data) {
        
        updates_this_hour = data[0].value
        $('#updates_this_hour').text(Math.round(updates_this_hour/1000)+"k")

        updates_this_hour_run_rate = updates_this_hour / percentage_through_hour
        $('#updates_this_hour_run_rate').text(Math.round(updates_this_hour_run_rate/1000)+"k")

        $('#updates_last_hour').text(Math.round(data[1].value/1000)+"k")
    })

}

var intervalId = window.setInterval(function(){
    refreshData();
}, 30000);

$(function () {
    
    // draw empty chart
    var ctx = document.getElementById("myAreaChart").getContext("2d");
    var myChart1 = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: "Location updates",
                    lineTension: 0.3,
                    backgroundColor: "rgba(78, 115, 223, 0.05)",
                    borderColor: "rgba(78, 115, 223, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgba(78, 115, 223, 1)",
                    pointBorderColor: "rgba(78, 115, 223, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                    pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            legend: {
                display: false,
            },
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true
                    }
                }]
            }
        }
    });

    // draw empty chart
    var ctx = document.getElementById("myAreaChart2").getContext("2d");
    var myChart2 = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: "Location updates",
                    lineTension: 0.3,
                    backgroundColor: "rgba(78, 115, 223, 0.05)",
                    borderColor: "rgba(78, 115, 223, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgba(78, 115, 223, 1)",
                    pointBorderColor: "rgba(78, 115, 223, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                    pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            legend: {
                display: false,
            },
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true
                    }
                }]
            }
        }
    });

    ajax_chart(myChart1, "https://findmyplane.live/stats/history/location_update/day/0/10", "date");
    ajax_chart(myChart2, "https://findmyplane.live/stats/history/location_update/hour/0/48", "hour");


    // function to update our chart
    function ajax_chart(chart, url, time_period) {
        var data = data || {};

        $.getJSON(url, data).done(function(response) {
            
            let labels = [];
            let datapoints = [];

            $.each(response , function( line ) {

                if (time_period === "date") {
                    labels.unshift(response[line].sensible_date)
                }
                if (time_period === "hour") {
                    labels.unshift(response[line].sensible_hour)
                }
                datapoints.unshift(response[line].value/1000)
            });
            console.log(labels)
            
            chart.data.labels = labels;
            chart.data.datasets[0].data = datapoints; // or you can iterate for multiple datasets
            chart.update(); // finally update our chart
        });
    }
});




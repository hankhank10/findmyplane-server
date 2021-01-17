let polylinePoints;


$(function() {
    $('#browseButton').change(function() {
        var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/api/upload_pln',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                console.log (data.status)
                if (data.status === "success") {
                    drawFlightPlan(data.waypoints);
                }
                if (data.status != "success") {
                    temporaryAlert("Uh oh...", "File could not be parsed. Ensure you are uploading a .PLN file.", "error")
                }
            },
            error: function() {
                temporaryAlert("Uh oh...", "File could not be parsed. Ensure you are uploading a .PLN file.", "error")
            },
        });
    });
});


function drawFlightPlan(data) {
    
    flightplanLayerGroup.clearLayers();
    var polylinePoints = [];

    data.forEach(function(waypoint) {
        console.log(waypoint.latitude);
        polylinePoints.push([waypoint.latitude, waypoint.longitude]);
    });
    
    var polylineOptions = {
        color: 'blue',
        weight: 6,
        opacity: 0.9
    };

    var polyline = new L.Polyline(polylinePoints, polylineOptions);

    flightplanLayerGroup.addLayer(polyline);

    temporaryAlert("", "New flight plan uploaded", "success")

    $('#labelFlightPlan').addClass('btn-success').addClass('btn');
    $('#spanFlightPlanLabel').html ("<i class='fas fa-route'></i> <i class='fas fa-check'>")

}
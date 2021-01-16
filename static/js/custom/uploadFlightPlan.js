let polylinePoints;


$(function() {
    $('#upload-file-btn').click(function() {
        var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/api/upload_pln',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                drawFlightPlan(data);
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
        color: 'red',
        weight: 6,
        opacity: 0.9
    };

    var polyline = new L.Polyline(polylinePoints, polylineOptions);

    flightplanLayerGroup.addLayer(polyline);

}
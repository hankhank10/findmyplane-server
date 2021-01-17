let altitude;
let compass;

let latitude;
let longitude;

let latitude_minus_1;
let longitude_minus_1;

let latitude_minus_2;
let longitude_minus_2;

let lastConnectionTime;
let lastPlaneTimestamp;

let disconnectedFromServer = false;
let pointsDrawn = 0;

window.setInterval(function(){
    //console.log(showMyPlane);
    if (showMyPlane === true) {
        getSimulatorData();
        updateMap();
        drawLine();
    };
    loadTraffic('flybywire');
}, 2000);


function setConnectionStatus(statusToReport) {

    if (statusToReport == "connected") {
        $('#btnServerStatus').removeClass('btn-danger').removeClass('btn-warning').addClass('btn-success');
        $('#btnServerStatus').html('<i class="fas fa-server"></i> <i class="fas fa-check"></i>');
        lastConnectionTime = Date.now()/1000;
        $('#lastDataTime').html("")
        disconnectedFromServer = false;
    }

    if (statusToReport == "error") {
        $('#btnServerStatus').removeClass('btn-success').removeClass('btn-warning').addClass('btn-danger');
        $('#btnServerStatus').html('<i class="fas fa-server"></i> Disconnected <span id="lastDataTimeLabel"></span> &nbsp <i class="fas fa-sync fa-spin">');
        $('#lastDataTimeLabel').livestamp(lastConnectionTime);
        disconnectedFromServer = true;
    }
}

function setPlaneStatus(statusToReport) {

    if (statusToReport == "recent") {
        $('#btnPlaneStatus').removeClass('btn-danger').removeClass('btn-warning').addClass('btn-success');
        $('#btnPlaneStatus').html('<i class="fas fa-plane"></i> <i class="fas fa-check"></i>');        
    }

    if (statusToReport == "old") {
        $('#btnPlaneStatus').removeClass('btn-success').removeClass('btn-warning').addClass('btn-danger');
        $('#btnPlaneStatus').html('<i class="fas fa-plane"></i> Last data <span id="lastPlaneTimestampLabel"></span> &nbsp <i class="fas fa-sync fa-spin">');
        $('#lastPlaneTimestampLabel').livestamp(lastPlaneTimestamp);
    }

}

function getSimulatorData() {

    $.getJSON($SCRIPT_ROOT + '/api/plane/' + ident_public_key, {}, function(data) {

        //Navigation
        altitude = data.my_plane.current_altitude;
        compass = data.my_plane.current_compass;
        latitude = data.my_plane.current_latitude;
        longitude = data.my_plane.current_longitude;
        lastPlaneTimestamp = data.my_plane.last_update;
        secondsSinceLastPlaneTimestamp = data.my_plane.seconds_since_last_update;

    })
    .done(function() { setConnectionStatus('connected')})
    .fail(function() { 
        setConnectionStatus('error');
    });

    if (secondsSinceLastPlaneTimestamp < 15 && disconnectedFromServer != true) {
        setPlaneStatus('recent');
    } else {
        setPlaneStatus('old')
    }

}

function toggleFollowPlane() {
    followPlane = !followPlane;
    if (followPlane === true) {
        $("#followMode").text("Moving map enabled")
        $("#followModeButton").removeClass("btn-outline-danger").addClass("btn-primary")
    }
    if (followPlane === false) {
        $("#followMode").text("Moving map disabled")
        $("#followModeButton").removeClass("btn-primary").addClass("btn-outline-danger")
    }
}

function toggleShowTrack() {
    showTrack = !showTrack;
    if (showTrack === true) {
        $("#showTrackMode").text("Track history enabled")
        $("#showTrackButton").removeClass("btn-outline-danger").addClass("btn-primary")
    }
    if (showTrack === false) {
        $("#showTrackMode").text("Track history disabled")
        $("#showTrackButton").removeClass("btn-primary").addClass("btn-outline-danger")
    }
}

function updateMap() {
    var pos = L.latLng(latitude, longitude);

    marker.slideTo(	pos, {
        duration: 1500,
    });
    marker.setRotationAngle(compass);

    if (followPlane === true) {
        map.panTo(pos);
    }
}

function clearPathHistory() {
    lineLayerGroup.clearLayers();
}

function drawLine() {

    if (pointsDrawn == 0) {
        latitude_minus_1 = latitude;
        longitude_minus_1 = longitude;
        pointsDrawn = pointsDrawn + 1;
        return
    }

    if (pointsDrawn == 1) {
        latitude_minus_2 = latitude_minus_1;
        longitude_minus_2 = longitude_minus_1;
        pointsDrawn = pointsDrawn + 1;
        return
    }

    pointsDrawn = pointsDrawn + 1;

    if (showTrack === true) {
        var polylinePoints = [
            [latitude_minus_2, longitude_minus_2],
            [latitude_minus_1, longitude_minus_1]
        ];   
        
        console.log(latitude_minus_2, longitude_minus_2, ">", latitude_minus_1, longitude_minus_1)
        var polylineOptions = {
            color: 'red',
            weight: 6,
            opacity: 0.9
        };

        var polyline = new L.Polyline(polylinePoints, polylineOptions);

        lineLayerGroup.addLayer(polyline);
    }

    latitude_minus_2 = latitude_minus_1;
    latitude_minus_1 = latitude;
    longitude_minus_2 = longitude_minus_1;
    longitude_minus_1 = longitude;

}


function loadTraffic(apiToCheck) {
    var bounds = map.getBounds();
    west = bounds.getWest();
    south = bounds.getSouth();
    east = bounds.getEast();
    north = bounds.getNorth();

    if (north > 90) {north = 90}
    if (east > 180) {east = 180}
    if (south < -90) {south = -90}
    if (west < -180) {west = -180}

    //console.log ("west=", west)
    //console.log ("south=", south)
    //console.log ("east =", east)
    //console.log ("north =", north)
    //apiURL = "https://api.flybywiresim.com/txcxn?west=-180&south=-90&east=180&north=90&skip=0&take=100"


    $.ajax({
        type: 'GET',
        url: 'https://api.flybywiresim.com/txcxn',
        data: {
            west: west,
            south: south,
            east: east,
            north: north,
            skip: 0,
            take: 100,
        },
        contentType: 'application/json; charset=utf-8',
        cache: false,
        success: function(data) {
            
            flybywireTrafficLayerGroup.clearLayers();

            trafficStatusMessage = "<i class='fas fa-traffic-light'></i> " + data.count
            if (data.total > data.count) {
                trafficStatusMessage = trafficStatusMessage + " of " + data.total
            }
            trafficStatusMessage = trafficStatusMessage + " local planes shown"

            $('#btnGlobalTraffic').html(trafficStatusMessage)
            $('#btnGlobalTraffic').removeClass("btn-warning").addClass("btn-success")

            data.results.forEach(function(otherPlane) {

                var otherPlaneMarker = L.marker([otherPlane.location.y, otherPlane.location.x], otherPlaneMarkerOptions);
                otherPlaneMarker.setRotationAngle(otherPlane.heading);

                tooltipText = "<b>" + otherPlane.aircraftType + "</b>"

                if (otherPlane.flight != "") {
                    tooltipText = tooltipText + " with flight number <b>" + otherPlane.flight + "</b>"
                }

                if (otherPlane.trueAltitude != "") {
                    tooltipText = tooltipText + " at <b>" + otherPlane.trueAltitude + "ft </b>"
                }

                if (otherPlane.origin != "") {
                    tooltipText = tooltipText + " from <b>" + otherPlane.origin + "</b>"
                }

                if (otherPlane.destination != "") {
                    tooltipText = tooltipText + " to <b>" + otherPlane.destination + "</b>"
                }

                tooltipText = tooltipText + "<br><i>(source: Fly-By-Wire)</i>"

                otherPlaneMarker.bindTooltip(tooltipText).openTooltip();
                otherPlaneMarker.addTo(flybywireTrafficLayerGroup)

            });

        },
    });
};



function temporaryAlert(title, message, icon) {
    let timerInterval

    Swal.fire({
        title: title,
        html: message,
        icon: icon,
        timer: 2000,
        timerProgressBar: true,
        onBeforeOpen: () => {
            Swal.showLoading()
            timerInterval = setInterval(() => {
                const content = Swal.getContent()
                if (content) {
                    const b = content.querySelector('b')
                    if (b) {
                        b.textContent = Swal.getTimerLeft()
                    }
                }
            }, 100)
        },
        onClose: () => {
            clearInterval(timerInterval)
        }
    }).then((result) => {
        /* Read more about handling dismissals below */
        if (result.dismiss === Swal.DismissReason.timer) {
            console.log('I was closed by the timer')
        }
    })
}
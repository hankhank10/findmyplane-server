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

let showFBWTraffic = true;
let showFMPTraffic = true;

let bounds;
let west;
let south;
let east;
let north;

window.setInterval(function(){
    //console.log(showMyPlane);
    getMapBounds()

    if (showMyPlane === true || showFMPTraffic === true) {
        getSimulatorData();
    }

    if (showMyPlane === true) {
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

    if (showMyPlane === true) {
        endpointToCall = '/api/plane/' + ident_public_key
    }
    if (showMyPlane === false) {
        endpointToCall = '/api/planes/'
    }

    $.ajax({
        type: 'GET',
        url: $SCRIPT_ROOT + endpointToCall,
        data: {
            west: west,
            south: south,
            east: east,
            north: north,
        },
        contentType: 'application/json; charset=utf-8',
        cache: false,
        success: function(data) {
            //Navigation
            if (showMyPlane === true) {
                altitude = data.my_plane.current_altitude;
                compass = data.my_plane.current_compass;
                latitude = data.my_plane.current_latitude;
                longitude = data.my_plane.current_longitude;
                lastPlaneTimestamp = data.my_plane.last_update;
                secondsSinceLastPlaneTimestamp = data.my_plane.seconds_since_last_update;
            }

            if (showFMPTraffic) {
                findmyplaneTrafficLayerGroup.clearLayers();

                howManyFMPPlanesDisplayed = 0

                data.other_planes.forEach(function(otherPlane) {

                    //console.log(otherPlane)
                    //console.log(otherPlane.current_latitude)
                    var otherPlaneMarker = L.marker([otherPlane.current_latitude, otherPlane.current_longitude], FMPPlaneMarkerOptions);
                    otherPlaneMarker.setRotationAngle(otherPlane.current_compass);

                    otherPlaneMarker.bindTooltip(generatePlaneToolTip(otherPlane.title, otherPlane.atc_id, otherPlane.ident_public_key, otherPlane.current_altitude, "", "", "findmyplane")).openTooltip();
                    otherPlaneMarker.addTo(findmyplaneTrafficLayerGroup)

                    howManyFMPPlanesDisplayed = howManyFMPPlanesDisplayed + 1
                });

                fmpTrafficStatusMessage = "<i class='fas fa-traffic-light'></i> "+ howManyFMPPlanesDisplayed + " Find My Plane planes in range"
                $('#btnFMPTraffic').html(fmpTrafficStatusMessage)
                $('#btnFMPTraffic').removeClass("btn-warning").addClass("btn-success")
            }

            setConnectionStatus('connected');
        },
        error: function(){
            setConnectionStatus('error');
        }
    });

    if (showMyPlane === true) {
        if (secondsSinceLastPlaneTimestamp < 15 && disconnectedFromServer != true) {
            setPlaneStatus('recent');
        } else {
            setPlaneStatus('old')
        }
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
        
        //console.log(latitude_minus_2, longitude_minus_2, ">", latitude_minus_1, longitude_minus_1)
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

function getMapBounds() {
    var bounds = map.getBounds();
    west = bounds.getWest();
    south = bounds.getSouth();
    east = bounds.getEast();
    north = bounds.getNorth();

    if (north > 90) {north = 90}
    if (east > 180) {east = 180}
    if (south < -90) {south = -90}
    if (west < -180) {west = -180}
}

function loadTraffic(apiToCheck) {

    if (showFBWTraffic === true) {
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

                fbwTrafficStatusMessage = "<i class='fas fa-traffic-light'></i> " + data.count
                if (data.total > data.count) {
                    fbwTrafficStatusMessage = fbwTrafficStatusMessage + " of " + data.total
                }
                fbwTrafficStatusMessage = fbwTrafficStatusMessage + " FBW planes in range"

                $('#btnFBWTraffic').html(fbwTrafficStatusMessage)
                $('#btnFBWTraffic').removeClass("btn-warning").addClass("btn-success")

                data.results.forEach(function(otherPlane) {

                    var otherPlaneMarker = L.marker([otherPlane.location.y, otherPlane.location.x], otherPlaneMarkerOptions);
                    otherPlaneMarker.setRotationAngle(otherPlane.heading);

                    otherPlaneMarker.bindTooltip(generatePlaneToolTip(otherPlane.aircraftType, otherPlane.flight, "", otherPlane.trueAltitude, otherPlane.origin, otherPlane.destination, "flybywire")).openTooltip();
                    otherPlaneMarker.addTo(flybywireTrafficLayerGroup)

                });

            },
        });
    }

};


function generatePlaneToolTip(aircraftType, flightNumber, ident, altitude, origin, destination, source) {

    tooltipText = "<b>" + aircraftType + "</b>"
    if (flightNumber != "") {
        tooltipText = tooltipText + " with flight number <b>" + flightNumber + "</b>";
        if (ident != "") { tooltipText = tooltipText + " and"}
    }
    if (ident != "") {tooltipText = tooltipText + " ident <b>" + ident + "</b>"}
    if (altitude != "") {tooltipText = tooltipText + " at <b>" + altitude + "ft </b>"}
    if (origin != "") {tooltipText = tooltipText + " from <b>" + origin + "</b>"}
    if (destination != "") {tooltipText = tooltipText + " to <b>" + destination + "</b>"}
    if (source === "flybywire") {tooltipText = tooltipText + "<br><i>(source: Fly-By-Wire)</i>"}
    if (source === "findmyplane") {tooltipText = tooltipText + "<br><i>(source: Find My Plane)</i>"}

    return tooltipText
}


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
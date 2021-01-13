let altitude;
let compass;
let latitude;
let longitude;

let lastConnectionTime;
let lastPlaneTimestamp;

let disconnectedFromServer = false;


window.setInterval(function(){
    getSimulatorData();
    updateMap()
}, 2000);


function setConnectionStatus(statusToReport) {

    if (statusToReport == "connected") {
        $('#btnServerStatus').removeClass('btn-danger').removeClass('btn-warning').addClass('btn-success');
        $('#btnServerStatus').html('<i class="fas fa-server"></i> Connected');
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
        $('#btnPlaneStatus').html('<i class="fas fa-plane"></i> Live');        
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
        altitude = data.current_altitude;
        compass = data.current_compass;
        latitude = data.current_latitude;
        longitude = data.current_longitude;
        lastPlaneTimestamp = data.last_update;
        secondsSinceLastPlaneTimestamp = data.seconds_since_last_update;

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

    return false;
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
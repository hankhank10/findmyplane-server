let altitude;
let compass;
let latitude;
let longitude;

let lastConnectionTime;


window.setInterval(function(){
    getSimulatorData();
    updateMap()
}, 2000);


function setConnectionStatus(statusToReport) {

    if (statusToReport == "connected") {
        $('#btnServerStatus').removeClass('btn-warning').addClass('btn-success');
        $('#btnServerStatus').html("Connected to <b>"+ident_public_key+"</b>");
        lastConnectionTime = Date.now()/1000;
        $('#lastDataTime').html("")
    }

    if (statusToReport == "error") {
        $('#btnServerStatus').removeClass('btn-success').addClass('btn-warning');
        $('#btnServerStatus').html('No data from <b>'+ident_public_key+'</b> since <span id="lastDataTime"></span>');
        $('#lastDataTime').livestamp(lastConnectionTime);
    }
}

function getSimulatorData() {

    $.getJSON($SCRIPT_ROOT + '/api/plane/' + ident_public_key, {}, function(data) {

        //Navigation
        altitude = data.current_altitude;
        compass = data.current_compass;
        latitude = data.current_latitude;
        longitude = data.current_longitude;

    })
    .done(function() { setConnectionStatus('connected')})
    .fail(function() { setConnectionStatus('error') });

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
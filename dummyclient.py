import requests
import time
import random

def print_settings():
    print ("# SETTINGS:")
    print ("Server address is", website_address)
    print ("Delay after failed new plane request is", str(delay_after_failed_new_plane_request), "seconds")
    print ("Delay between updates is", str(delay_between_updates), "seconds")
    print ()


def update_location():

    global current_latitude
    global current_longitude

    error_this_time = False
    global datapoints_sent
    global server_errors_logged
    global sim_errors_logged

    global current_altitude
    global vertical_movement

    current_latitude = current_latitude
    if current_longitude > 17:
        current_longitude = starting_longitude
    else:
        current_longitude = current_longitude + 0.03
    
    if current_altitude == 10000:
        vertical_movement = "up"
    if current_altitude == 37000:
        vertical_movement = "down"

    if vertical_movement == "up":
        current_altitude = current_altitude + 250
    if vertical_movement == "down":
        current_altitude = current_altitude - 250
    
    current_compass = 90

    if not error_this_time:
        data_to_send = {
            'ident_public_key': ident_public_key,
            'ident_private_key': ident_private_key,
            'current_latitude': current_latitude,
            'current_longitude': current_longitude,
            'current_compass': current_compass,
            'current_altitude': current_altitude,
            'seatbelt_sign': True,
            'no_smoking_sign': True,
            'door_status': 1,
            'gear_handle_position': 1,
            'client_version': 2000
        }

        if verbose: print ("Sending ", data_to_send)
        
        try:
            url_to_post_to = website_address+"/api/update_plane_location"
            #print(url_to_post_to)
            r = requests.post(url_to_post_to, json=data_to_send)
            if r.status_code != 200:
                server_errors_logged += 1

        except:
            if verbose: print ("Error sending data")
            server_errors_logged += 1

        datapoints_sent += 1

    if not verbose: print (str(datapoints_sent) + " datapoints sent of which " + str(server_errors_logged) + " generated server errors and " + str(sim_errors_logged) + " sim errors", end='\r')

    return "ok"


# Settings
website_address = "http://localhost"
website_port = 8765
website_address = website_address + ":" + str(website_port)

delay_after_failed_new_plane_request = 3
delay_between_updates = 2
verbose = False
version = "Dummy Alpha 0.3"

datapoints_sent = 0
server_errors_logged = 0
sim_errors_logged = 0

print ("Fake client")
print ()
print_settings()

# Request new plane instance from the server

print("# CONNECTING TO SERVER IN TEST MODE")
ident_public_key = "DUMMY"
ident_private_key = "dummydata"

print ("Server set as", website_address)
print ("Ident public key =", str(ident_public_key))
print ("Press CTRL-C to exit")
print ()

starting_latitude = 48.8566
starting_longitude = 2.3522
current_latitude = starting_latitude
current_longitude = starting_longitude

current_altitude = 22000
vertical_movement = "up"

# Report the info to the server
run_forever = True
try:
    while run_forever:
        update_location()
        time.sleep(delay_between_updates)
except KeyboardInterrupt:
    quit()


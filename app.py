import os
from re import A
from flask import Flask, flash, request, redirect, url_for, render_template, flash, jsonify, Response, send_file, got_request_exception
import secrets
import random
import string

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from flask_migrate import Migrate

from datetime import datetime

from sqlalchemy.sql.expression import false

import nearby_city_api
import stats_handler2
import tweeter

import xmltodict
import json
import secrets
import os
from pathlib import Path

import requests
import logging

from flask_cors import CORS

import secretstuff

# Error messages
error_message_400 = {'status': 'error', 
                     'message': 'The necessary variables were not provided. Please check the API documentation.'}


#import sentry_sdk
#from sentry_sdk.integrations.flask import FlaskIntegration

# Sentry
#sentry_sdk.init(
#    dsn="https://00a5f5470b9c45d8ba9c438c4e5eae62@o410120.ingest.sentry.io/5598707",
#    integrations=[FlaskIntegration()],
#    traces_sample_rate=1.0
#)

import rollbar
import rollbar.contrib.flask



# Define flask variables
app = Flask(__name__)
app.secret_key = secretstuff.secret_key
app.config['UPLOAD_FOLDER'] = 'uploads'
CORS(app)

# DB initialisation
app.config['SQLALCHEMY_DATABASE_URI'] = secretstuff.planes_mysql_address
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)


# Rollbar
rollbar.init(
        '11bec99d70ec4f028dada8d1f7996076',
        'flask',
        root=os.path.dirname(os.path.realpath(__file__)),
        allow_logging_basic_config=False)

rollbar.report_message('app.py started', 'info')
got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


# DB models

class Plane(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ident_public_key = db.Column(db.String(6))
    ident_private_key = db.Column(db.String(30))
    current_latitude = db.Column(db.Float, default=0)
    current_longitude = db.Column(db.Float, default=0)
    previous_latitude = db.Column(db.Float, default=0)
    previous_longitude = db.Column(db.Float, default=0)
    current_compass = db.Column(db.Integer, default=0)
    current_altitude = db.Column(db.Integer, default=0)
    current_speed = db.Column(db.Integer, default=0)
    last_update = db.Column(db.DateTime, default=datetime.utcnow())
    time_created = db.Column(db.DateTime, default=datetime.utcnow())
    ever_received_data = db.Column(db.Boolean, default=false)
    title = db.Column(db.String(200), default="Unknown aircraft")
    atc_id = db.Column(db.String(30), default="Unknown callsign")
    description_of_location = db.Column(db.String(200))
    full_plane_description = db.Column(db.String(300))
    client = db.Column(db.String(20), default="Find My Plane")

    on_ground = db.Column(db.Boolean, default=False)
    seatbelt_sign = db.Column(db.Boolean, default=False)
    no_smoking_sign = db.Column(db.Boolean, default=False)
    door_status = db.Column(db.Integer, default=0)
    parking_brake = db.Column(db.Boolean, default=False)

    @hybrid_property
    def current_compass_less_90(self):
        if self.current_compass is None:
            return 0

        try:
            compass = self.current_compass - 90
        except:
            return 0
        
        if compass < 0:
            compass = compass + 360
        return compass

    @hybrid_property
    def seconds_since_last_update(self):
        time_difference_seconds = datetime.utcnow() - self.last_update
        return time_difference_seconds.seconds
    
    @hybrid_property
    def is_current(self):
        if self.seconds_since_last_update < (5 * 60):
            return True
        else:
            return False


class Waypoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ident_public_key = db.Column(db.String(6), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    compass = db.Column(db.Integer)
    altitude = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    on_ground = db.Column(db.Boolean)


# API Endpoints

@app.route('/api')
def api_docs():
    stats_handler2.log_event('page_load', 'api')
    return redirect ("https://app.swaggerhub.com/apis-docs/hankhank/FindMyPlane/")


@app.route('/api/create_dummy_plane')
def api_dummy_plane():

    new_plane = Plane (
        ident_public_key = "DUMMY",
        ident_private_key = "dummydata",
        current_latitude = 0,
        current_longitude = 0,
        previous_latitude = 0,
        previous_longitude = 0,
        current_compass = 0,
        current_altitude = 0,
        last_update = datetime.utcnow(),
        time_created = datetime.utcnow(),
        title = "Boeing 747",
        atc_id = "DUM 1",
        current_speed = 0,
        client= "Find My Plane",
        on_ground = False,
        ever_received_data = False
    )
    
    db.session.add(new_plane)
    db.session.commit()

    return "ok"


@app.route('/api/create_new_plane', methods=['POST'])
def api_new_plane():

    data_received = request.json

    # Generate upper case random public key
    letters = string.ascii_uppercase

    public_key = ''.join(random.choice(letters) for i in range(5))
    private_key = secrets.token_urlsafe(20)

    # Set the default variables
    plane_title = "Unknown aircraft"
    atc_id = "Unknown callsign"
    client = "Find My Plane"

    # But replace them if they have been passed
    if not data_received is None:
        if 'title' in data_received: plane_title = data_received['title']
        if 'atc_id' in data_received: atc_id = data_received['atc_id']
        if 'client' in data_received: client = data_received['client']

    new_plane = Plane (
        ident_public_key = public_key,
        ident_private_key = private_key,
        current_latitude = 0,
        current_longitude = 0,
        previous_latitude = 0,
        previous_longitude = 0,
        current_compass = 0,
        current_altitude = 0,
        last_update = datetime.utcnow(),
        time_created = datetime.utcnow(),
        title = plane_title,
        atc_id = atc_id,
        client = client,
        ever_received_data = False
    )
    
    db.session.add(new_plane)
    db.session.commit()

    output_dictionary = {
        "status": "success",
        "ident_public_key": public_key,
        "ident_private_key": private_key
    }

    stats_handler2.log_event('new_plane', public_key)

    # Tweet
    #try:
    #    tweet_message = "New flight: " + plane_title + " with callsign " + atc_id + ". Follow along live at https://findmyplane.live/view/" + public_key
    #    tweeter.post_tweet(tweet_message)
    #except:
    #    pass

    return jsonify(output_dictionary)


@app.route('/api/update_plane_location', methods=['POST'])
def api_update_location():

    data_received = request.json

    # Check that information has been passed
    if data_received is None: return jsonify(error_message_400), 400
    if not 'ident_public_key' in data_received: return jsonify(error_message_400), 400
    if not 'ident_private_key' in data_received: return jsonify(error_message_400), 400

    #print (data_received['ident_public_key'] + "> " + data_received['ident_private_key'])

    # Find the plane requested
    #print (data_received['ident_public_key'])
    plane_to_update = Plane.query.filter_by(
        ident_public_key = data_received['ident_public_key'].upper(), 
        ident_private_key = data_received['ident_private_key']
        ).first_or_404()

    # Check if it is the first time data has been sent, because in that scenario we need to update the plane descriptions at the end of creating the record
    first_time = False
    if plane_to_update.ever_received_data == False:
        plane_to_update.ever_received_data = True
        first_time = True

    # Get the compass, but if it's none then default to 0
    current_compass = 0
    if 'current_compass' in data_received:
        if data_received['current_compass'] is not None:
            current_compass = data_received['current_compass']

    current_compass = round(current_compass, 0)
    current_compass = '{:.0f}'.format(current_compass)

    # Do the update for mandatory data
    plane_to_update.last_update = datetime.utcnow()

    # Set the optional variables
    if 'current_latitude' in data_received: 
        if first_time:
            plane_to_update.previous_latitude = data_received['current_latitude']
        else:
            plane_to_update.previous_latitude = plane_to_update.current_latitude
        
        plane_to_update.current_latitude = data_received['current_latitude']
    
    if 'current_longitude' in data_received: 
        if first_time:
            plane_to_update.previous_longitude = data_received['current_longitude']
        else:
            plane_to_update.previous_longitude = plane_to_update.current_longitude

        plane_to_update.current_longitude = data_received['current_longitude']    

    if 'current_compass' in data_received:
        if data_received['current_compass'] is not None:
            current_compass = data_received['current_compass']
            current_compass = round(current_compass,0)
            current_compass = '{:.0f}'.format(current_compass)
            plane_to_update.current_compass = current_compass
    
    if 'current_altitude' in data_received: plane_to_update.current_altitude = data_received['current_altitude']
    if 'current_speed' in data_received: plane_to_update.current_speed = data_received['current_speed']

    if 'on_ground' in data_received: plane_to_update.on_ground = data_received['on_ground']
    if 'seatbelt_sign' in data_received: plane_to_update.seatbelt_sign = data_received['seatbelt_sign']
    if 'no_smoking_sign' in data_received: plane_to_update.no_smoking_sign = data_received['no_smoking_sign']
    if 'door_status' in data_received: plane_to_update.door_status = data_received['door_status']
    if 'parking_brake' in data_received: plane_to_update.parking_brake = data_received['parking_brake']

    if 'title' in data_received: plane_to_update.title = data_received['title']
    if 'atc_id' in data_received: plane_to_update.atc_id = data_received['atc_id']
    if 'client' in data_received: plane_to_update.client = data_received['client']
    if 'speed' in data_received: plane_to_update.speed = data_received['speed']


    # Create waypoint record
    if data_received['ident_public_key'] != "DUMMY":
        new_waypoint = Waypoint (
            ident_public_key = data_received['ident_public_key'].upper(),
            latitude = data_received['current_latitude'],
            longitude = data_received['current_longitude'],
            compass = data_received['current_compass'],
            altitude = data_received['current_altitude'],
            timestamp = datetime.utcnow(),
            on_ground = plane_to_update.on_ground
        )
    
        db.session.add(new_waypoint)
        
    db.session.commit()

    if first_time:
        backend_update_plane_descriptions()

    if data_received['ident_public_key'] != "DUMMY":
        stats_handler2.log_event('location_update', data_received['ident_public_key'])
        pass

    return jsonify({'status': 'success'})


@app.route ('/api/plane/<ident_public_key>', endpoint='my_plane')
@app.route ('/api/planes/', endpoint='all_planes')
def api_view_plane_data(ident_public_key="none"):

    output_dictionary = {'status': 'success'}

    if request.endpoint == 'my_plane':
        plane = Plane.query.filter_by(ident_public_key = ident_public_key).first_or_404()

        if plane.current_altitude == None:
            altitude = 0
        else:
            altitude = plane.current_altitude
            altitude = round(altitude,-3)
            altitude = '{:.0f}'.format(altitude)

        if plane.current_latitude == None or plane.current_longitude == None:
            return jsonify({
                'status': 'error',
                'error_reason': 'current lat or lon is None',
                'debug_data': {
                    'ident_public_key': plane.ident_public_key,
                    'current_latitude': plane.current_latitude,
                    'current_longitude': plane.current_longitude,
                    'previous_latitude': plane.previous_latitude,
                    'previous_longitude': plane.previous_longitude
                }
            }) 

        if plane.previous_latitude == None: plane.previous_latitude = 0
        if plane.previous_longitude == None: plane.previous_longitude = 0
        db.session.commit()

        latitude_difference = abs(plane.current_latitude) - abs(plane.previous_latitude)
        longitude_difference = abs(plane.current_longitude) - abs(plane.previous_longitude)
        if latitude_difference > 1 or longitude_difference > 1:
            return jsonify({
                'status': 'error',
                'error_reason': 'too big a jump in lat or lon detected',
                'debug_data': {
                    'ident_public_key': plane.ident_public_key,
                    'current_latitude': plane.current_latitude,
                    'current_longitude': plane.current_longitude,
                    'previous_latitude': plane.previous_latitude,
                    'previous_longitude': plane.previous_longitude,
                    'latitude_difference': latitude_difference,
                    'longitude_difference': longitude_difference,
                }
            })
            
        my_plane_dictionary = {
            'ident_public_key': plane.ident_public_key,
            'current_latitude': plane.current_latitude,
            'current_longitude': plane.current_longitude,
            'current_compass': plane.current_compass,
            'current_altitude': altitude,
            'current_speed': plane.current_speed,
            'last_update': plane.last_update,
            'time_created': plane.time_created,
            'ever_received_data': plane.ever_received_data,
            'seconds_since_last_update': plane.seconds_since_last_update,
            'minutes_since_last_update': plane.seconds_since_last_update / 60,
            'latitude_difference': latitude_difference,
            'longitude_difference': longitude_difference,
            'on_ground': plane.on_ground,
            'client': plane.client,
            'title': plane.title,
            'atc_id': plane.atc_id
        }
        output_dictionary['my_plane'] = my_plane_dictionary

    # Do the other planes
    output_dictionary['other_planes'] = []

    north = request.args.get('north')
    south = request.args.get('south')
    east = request.args.get('east')
    west = request.args.get('west')

    if north == None: north = 90
    if south == None: south = -90
    if east == None: east = 180
    if west == None: west = -180

    north = float(north)
    south = float(south)
    east = float(east)
    west = float(west)

    if north > 90: north = 90
    if south < -90: south = -90
    if east > 180: east = 180
    if west < -180: west = -180

    traffic_planes = Plane.query.filter(Plane.ident_public_key != ident_public_key, Plane.current_latitude > south, Plane.current_latitude < north, Plane.current_longitude > west, Plane.current_longitude < east).all()

    for traffic_plane in traffic_planes:
        if traffic_plane.is_current and traffic_plane.ever_received_data:

            if traffic_plane.current_altitude == None:
                altitude = 0
            else:
                altitude = traffic_plane.current_altitude
                altitude = round(altitude,-3)
                altitude = '{:.0f}'.format(altitude)

            other_plane_dictionary = {
                'ident_public_key': traffic_plane.ident_public_key,
                'current_latitude': traffic_plane.current_latitude,
                'current_longitude': traffic_plane.current_longitude,
                'current_altitude': altitude,
                'current_compass': traffic_plane.current_compass,
                'title': traffic_plane.title,
                'atc_id': traffic_plane.atc_id,
                'client': traffic_plane.client,
                'current_speed': traffic_plane.current_speed,
                'on_ground': traffic_plane.on_ground
            }
            output_dictionary['other_planes'].append(other_plane_dictionary)
    
    #if request.endpoint == "my_plane":
    #    ga.send_event('usage', 'api query one plane', ident_public_key)
    #if request.endpoint == "all_planes":
    #    ga.send_event('usage', 'api query all planes', ident_public_key)

    return jsonify(output_dictionary)


# Backend endpoints

@app.route('/backend/random_tweet')
def random_tweet():
    if int(number_of_current_planes()) < 5:
        return "Nobody here mate"

    random_planes = some_random_current_planes(how_many=20)
    random_plane = random.choice(random_planes)

    if random_plane.full_plane_description == None:
        stats_handler2.log_event('tweet_nothing_to_say')
        return "Nothing to say mate"

    if random_plane.ident_public_key == "DUMMY":
        stats_handler2.log_event('tweet_plane_is_dummy')
        return "That plane is a dummy"        
    
    if "null island" in random_plane.full_plane_description:
        stats_handler2.log_event('tweet_plane_is_nowhere')
        return "That plane is nowhere"

    try:
        message_to_tweet = "Live flight: " + random_plane.full_plane_description + ". Follow along at https://findmyplane.live/view/" + random_plane.ident_public_key
        tweeter.post_tweet (message_to_tweet)
    except:
        stats_handler2.log_event('tweet_error')
        return "Something went wrong" + message_to_tweet

    stats_handler2.log_event('tweet_sent')
    return "All good"



@app.route('/backend/update_plane_descriptions')
def backend_update_plane_descriptions():

    planes = Plane.query.all()  #this should eventually be changed to only show current planes
    number_of_planes_updated = 0

    for plane in planes:
        if plane.ever_received_data and not plane.is_current:
            if plane.ident_public_key != "DUMMY":
                #print ("Deleting ", plane.ident_public_key)
                #db.session.delete(plane)
                pass

        
        if plane.is_current and plane.ever_received_data:
            if plane.current_latitude or plane.current_longitude != None:

                if plane.title != None: 
                    plane.title = plane.title.replace("Asobo", "")
                    plane.title = plane.title.replace("DCDesigns_", "")
                    plane.title = plane.title.replace("Aircraft Mega Pack", "")
                    
                    plane.title = plane.title.replace("F15E", "F-15E")
                    
                    plane.title = plane.title.replace("_", " ")



                plane_location = nearby_city_api.find_closest_city(plane.current_latitude, plane.current_longitude)
                if plane_location['status'] == "success":
                    
                    if plane.current_latitude < 0.02 and plane.current_longitude < 0.02:
                        plane.full_plane_description = plane.title + " at null island somewhere off Ghana"
                    else:
                        description_of_location = plane_location['text_expression']
                        plane.description_of_location = description_of_location

                        if plane.current_altitude != None:
                            # Format altitude
                            altitude = plane.current_altitude
                            altitude = round(altitude,-3)
                            altitude = '{:.0f}'.format(altitude)
                            # Set description
                            try:
                                plane.full_plane_description = plane.title + " at " + altitude + "ft, " + description_of_location
                            except:
                                plane.full_plane_description = "A plane somewhere"
                        else:
                            plane.full_plane_description = plane.title + " at unknown altitude " + description_of_location

                    number_of_planes_updated += 1

    db.session.commit()
    return str(number_of_planes_updated) + " plane descriptions updated"


@app.route('/number_of_planes')
def number_of_current_planes():
    plane_list = Plane.query.filter(Plane.ever_received_data == True).all()

    plane_count = 0
    for plane in plane_list:
        if plane.is_current:
            plane_count = plane_count + 1

    return str(plane_count)


def some_random_current_planes(how_many=5):
    planes_list = Plane.query.filter(Plane.ever_received_data == True).order_by(Plane.last_update.desc()).limit(how_many*2).all()

    plane_count = 0
    filtered_planes_list = []

    for plane in planes_list:
        if plane.is_current:
            if plane_count <= how_many - 1:
                filtered_planes_list.append(plane)
                plane_count = plane_count + 1

    return filtered_planes_list


# Public facing events ...

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['ident'] == "":
            flash('No ident provided')
            return redirect (url_for('index'))
        else:
            return redirect (url_for('show_map', ident_public_key=request.form['ident'].upper()))

    if request.method == 'GET':
        stats_handler2.log_event('page_load', 'index')
        return render_template('index.html',
                               number_of_current_planes=number_of_current_planes(),
                               some_random_current_planes=some_random_current_planes(10)
                               )


@app.route('/someplanes')
def some_planes():
    return str(some_random_current_planes(10)[0].current_compass_less_90)


@app.route('/view/<ident_public_key>')
def show_map(ident_public_key):

    if len(ident_public_key) == 5: 
        source = "findmyplane"
    else:
        source = "flybywire"

    if source == "findmyplane":

        ident_public_key = ident_public_key.upper()

        plane = Plane.query.filter_by(ident_public_key = ident_public_key).first()

        if bool(plane) == False:
            flash("No record of ident "+ ident_public_key + " with Find My Plane")
            return redirect(url_for('index'))

    if source == "flybywire":
        try:
            r = requests.get('https://api.flybywiresim.com/txcxn/_find', {'flight': ident_public_key})
            json_output = r.json()
        except:
            json_output = []
            logging.error("Fly By Wire API returned an error when trying to search for flight  " + ident_public_key)

        if json_output == [] or json_output['fullMatch'] == None:
            flash ("Can't find plane "+ ident_public_key + " with Fly By Wire")
            return redirect(url_for('index'))

    stats_handler2.log_event('map_load')

    return render_template('map.html',
                           ident_public_key=ident_public_key,
                           source=source,
                           just_map = False)


@app.route('/view_world')
def show_world_map():

    stats_handler2.log_event('world_map_load')

    return render_template('map.html',
                           ident_public_key="WORLD",
                           just_map = False)


@app.route('/view_world/justmap')
def show_world_map_just_map():

    stats_handler2.log_event('world_map_load')

    return render_template('map.html',
                           ident_public_key="WORLD",
                           just_map = True)


@app.route('/stats')
def stats_endpoint():

    stats_dictionary = {
        'history': stats_handler2.return_all_events(),
        'now': {
            'current_planes': int(number_of_current_planes())
        }
    }

    return jsonify(stats_dictionary)


@app.route('/stats/fire_hose')
def fire_hose():
    fire_hose_status = stats_handler2.fire_hose()
    return fire_hose_status


@app.route('/stats/history/<event_type>/<period_type>/<most_recent_period>/<oldest_period>')
def stats_history(event_type, period_type, most_recent_period, oldest_period):

    output = stats_handler2.create_event_history(event_type, period_type, int(most_recent_period), int(oldest_period))
    return jsonify(output)


@app.route('/activity')
def statschart():
    return render_template('dashboard.html')


@app.route('/latestclient')
def latest_client_check():
    return "Alpha 0.2"


@app.route('/download')
@app.route('/download/findmyplane-setup.exe')
@app.route('/download/findmyplane-setup.zip')
def download_setup_link():
    stats_handler2.log_event('download', 'setup')
    return redirect('https://github.com/hankhank10/findmyplane-client/releases/download/v0.8.4/findmyplane-setup.zip')


@app.route('/download/findmyplane-client.exe')
@app.route('/download/findmyplane-client.zip')
def download_exe_link():
    stats_handler2.log_event('download', 'client')
    return redirect("https://github.com/hankhank10/findmyplane-client/releases/download/v0.8.4/findmyplane-client.zip")


@app.route('/debug/error')
def debug_error():
    a = 1 / 0
    return a


# All of these are parsing PLN endpoints
def open_file(filename):
    with open (filename, 'r') as xmlfile:
        xml_string = xmlfile.read()

    xml_string = xml_string.replace('°','')

    pln_dictionary = xmltodict.parse(xml_string)
    return pln_dictionary


def fix_waypoints(pln_dictionary):

    for waypoint in pln_dictionary['SimBase.Document']['FlightPlan.FlightPlan']['ATCWaypoint']:

        # Split into constituent parts
        waypoint['Latitude'] = waypoint['WorldPosition'].split(",")[0]
        waypoint['Longitude'] = waypoint['WorldPosition'].split(",")[1]
        waypoint['Altitude'] = waypoint['WorldPosition'].split(",")[2]
        
        # Tidy altitude
        waypoint['Altitude'] = float(waypoint['Altitude'])

        # Work out latitude
        latitude_direction = waypoint['Latitude'][0]
        rest_of_latitude = waypoint['Latitude'][1:]
        
        latitude_degrees = rest_of_latitude.split(" ")[0]
        latitude_minutes = rest_of_latitude.split(" ")[1]
        latitude_seconds = rest_of_latitude.split(" ")[2]

        latitude_minutes = latitude_minutes.split("'")[0]
        latitude_seconds = latitude_seconds.split('"')[0]

        latitude_degrees = int(latitude_degrees)
        latitude_minutes = int(latitude_minutes)
        latitude_seconds = float(latitude_seconds)

        latitude_decimal = latitude_degrees + (latitude_minutes/60) + (latitude_seconds/3600)
        #print (str(latitude_degrees), str(latitude_minutes), str(latitude_seconds), ">", str(latitude_decimal))

        if latitude_direction == "S":
            latitude_decimal = -latitude_decimal
        waypoint['DecimalLatitude'] = latitude_decimal

        # Work out longitude
        longitude_direction = waypoint['Longitude'][0]
        rest_of_longitude = waypoint['Longitude'][1:]
        
        longitude_degrees = rest_of_longitude.split(" ")[0]
        longitude_minutes = rest_of_longitude.split(" ")[1]
        longitude_seconds = rest_of_longitude.split(" ")[2]

        longitude_minutes = longitude_minutes.split("'")[0]
        longitude_seconds = longitude_seconds.split('"')[0]

        longitude_degrees = int(longitude_degrees)
        longitude_minutes = int(longitude_minutes)
        longitude_seconds = float(longitude_seconds)

        longitude_decimal = longitude_degrees + (longitude_minutes/60) + (longitude_seconds/3600)
        print (str(longitude_degrees), str(longitude_minutes), str(longitude_seconds), ">", str(longitude_decimal))

        if longitude_direction == "W":
            longitude_decimal = -longitude_decimal
        waypoint['DecimalLongitude'] = longitude_decimal

    return pln_dictionary


def simplify_route(source_dictionary):

    output_dictionary = []

    a = 0
    for waypoint in source_dictionary['SimBase.Document']['FlightPlan.FlightPlan']['ATCWaypoint']:
        this_waypoint = {
            'id': a,
            'latitude': waypoint['DecimalLatitude'],
            'longitude': waypoint['DecimalLongitude']
        }
        output_dictionary.append(this_waypoint)
        a = a + 1
    
    output_dictionary = {
        'status': 'success',
        'waypoints': output_dictionary
    }

    return output_dictionary


def create_db():
    db.create_all()


def save_file(filename, pln_dictionary):
    with open (filename, 'w') as jsonfile:
        json.dump(pln_dictionary['SimBase.Document']['FlightPlan.FlightPlan'], jsonfile, indent=4)


@app.route('/api/upload_pln', methods=['GET', 'POST'])
def receive_upload(simple=True):
    
    if request.method == "GET":
        return render_template('upload.html')

    if request.method == "POST":

        if 'file' not in request.files:
            return "No file uploaded"

        temporary_filename = secrets.token_urlsafe(25)

        file = request.files['file']
        extension = Path(file.filename).suffix

        if extension != ".pln":
            return jsonify({'status': 'error'})

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], temporary_filename))

        new_route = open_file('uploads/' + temporary_filename)
        fixed_route = fix_waypoints(new_route)

        if simple:
            simple_route = simplify_route(fixed_route)
            return jsonify(simple_route)
        else:
            return jsonify(fixed_route)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8765, debug=True)

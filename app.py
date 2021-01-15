import os
from flask import Flask, flash, request, redirect, url_for, render_template, flash, jsonify, Response
import secrets
import random
import string

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from flask_migrate import Migrate

from datetime import datetime

import nearby_city_api
import stats_handler


# Define flask variables
app = Flask(__name__)
app.secret_key = 'sdfdsagfdggdfsgdfg988'
#website_url = "http://localhost:5008/"

# DB initialisation
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///findmyplanedb.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)


# DB models

class Plane(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ident_public_key = db.Column(db.String(6))
    ident_private_key = db.Column(db.String)
    current_latitude = db.Column(db.Float)
    current_longitude = db.Column(db.Float)
    current_compass = db.Column(db.Integer)
    current_altitude = db.Column(db.Integer)
    last_update = db.Column(db.DateTime, default=0)
    ever_received_data = db.Column(db.Boolean)
    title = db.Column(db.String)
    atc_id = db.Column(db.String)
    description_of_location = db.Column(db.String)
    full_plane_description = db.Column(db.String)

    @hybrid_property
    def current_compass_less_90(self):
        compass = self.current_compass - 90
        if compass < 0:
            compass = compass + 360
        return compass

    @hybrid_property
    def seconds_since_last_update(self):
        #print (str(self.id), self.last_update)
            
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
    ident_public_key = db.Column(db.String(6), db.ForeignKey('plane.ident_public_key'), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    compass = db.Column(db.Integer)
    altitude = db.Column(db.Integer)


# API Endpoints
@app.route('/api/create_dummy_plane')
def api_dummy_plane():

    new_plane = Plane (
        ident_public_key = "DUMMY",
        ident_private_key = "dummydata",
        current_latitude = 0,
        current_longitude = 0,
        current_compass = 0,
        current_altitude = 0,
        last_update = datetime.utcnow(),
        title = "Boeing 747",
        atc_id = "AFC 156",
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

    new_plane = Plane (
        ident_public_key = public_key,
        ident_private_key = private_key,
        current_latitude = 0,
        current_longitude = 0,
        current_compass = 0,
        current_altitude = 0,
        last_update = datetime.utcnow(),
        title = data_received['title'],
        atc_id = data_received['atc_id'],
        ever_received_data = False
    )
    
    db.session.add(new_plane)
    db.session.commit()

    output_dictionary = {
        "ident_public_key": public_key,
        "ident_private_key": private_key
    }

    stats_handler.increment_stat('planes_created')

    return jsonify(output_dictionary)


@app.route('/api/update_plane_location', methods=['POST'])
def api_update_location():

    data_received = request.json

    # Update plane information
    plane_to_update = Plane.query.filter_by(ident_public_key = data_received['ident_public_key'].upper(), ident_private_key = data_received['ident_private_key']).first_or_404()

    plane_to_update.last_update = datetime.utcnow()
    plane_to_update.current_latitude = data_received['current_latitude']
    plane_to_update.current_longitude = data_received['current_longitude']
    plane_to_update.current_compass = data_received['current_compass']
    plane_to_update.current_altitude = data_received['current_altitude']

    # Check if it is the first time data has been sent
    first_time = False
    if plane_to_update.ever_received_data == False:
        plane_to_update.ever_received_data = True
        first_time = True

    #db.session.commit()

    # Create waypoint record
    new_waypoint = Waypoint (
        ident_public_key = data_received['ident_public_key'].upper(),
        latitude = data_received['current_latitude'],
        longitude = data_received['current_longitude'],
        compass = data_received['current_compass'],
        altitude = data_received['current_altitude']
    )
    
    db.session.add(new_waypoint)
    db.session.commit()

    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    compass = db.Column(db.Integer)
    altitude = db.Column(db.Integer)

    if first_time:
        backend_update_plane_descriptions()

    if data_received['ident_public_key'] != "DUMMY": stats_handler.increment_stat('location_updates')

    return "ok"


@app.route ('/api/plane/<ident_public_key>')
def api_view_plane_data(ident_public_key):
    plane = Plane.query.filter_by(ident_public_key = ident_public_key).first_or_404()

    output_dictionary = {
        'ident_public_key': plane.ident_public_key,
        'current_latitude': plane.current_latitude,
        'current_longitude': plane.current_longitude,
        'current_compass': plane.current_compass,
        'current_altitude': plane.current_altitude,
        'last_update': plane.last_update,
        'ever_received_data': plane.ever_received_data,
        'seconds_since_last_update': plane.seconds_since_last_update,
        'minutes_since_last_update': plane.seconds_since_last_update / 60
    }

    return jsonify(output_dictionary)


# Backend endpoints

@app.route('/backend/update_plane_descriptions')
def backend_update_plane_descriptions():

    planes = Plane.query.all()  #this should eventually be changed to only show current planes
    number_of_planes_updated = 0

    for plane in planes:
        if plane.is_current and plane.ever_received_data:
            plane_location = nearby_city_api.find_closest_city(plane.current_latitude, plane.current_longitude)
            if plane_location['status'] == "success":
                description_of_location = plane_location['text_expression']
                plane.description_of_location = description_of_location

                # Format altitude
                altitude = plane.current_altitude
                altitude = round(altitude,-3)
                altitude = '{:.0f}'.format(altitude)

                if plane.current_altitude != None:
                    plane.full_plane_description = plane.title + " at " + altitude + "ft, " + description_of_location
                else:
                    plane.full_plane_description = plane.title + " at unknown altitude " + description_of_location

                number_of_planes_updated += 1
                #print (plane.ident_public_key, plane.full_plane_description)
            else:
                #print ("City API status", plane_location['status'])
                pass

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


def some_random_current_planes(how_many = 5):
    planes_list = Plane.query.filter(Plane.ever_received_data == True).order_by(Plane.last_update.desc()).limit(how_many*2).all()

    plane_count = 0
    filtered_planes_list = []

    for plane in planes_list:
        if plane.is_current:
            if plane_count <= how_many -1:
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
        stats_handler.increment_stat('homepage_loads')
        return render_template('index.html', number_of_current_planes=number_of_current_planes(), some_random_current_planes = some_random_current_planes(10))


@app.route('/view/<ident_public_key>')
def show_map(ident_public_key):

    ident_public_key = ident_public_key.upper()

    plane = Plane.query.filter_by(ident_public_key = ident_public_key).first()

    if bool(plane) == False:
        flash ("No record of ident "+ ident_public_key)
        return redirect(url_for('index'))

    stats_handler.increment_stat('map_loads')

    return render_template('map.html', ident_public_key = ident_public_key)


@app.route('/latestclient')
def latest_client_check():
    return "Alpha 0.2"


@app.route('/download/findmyplane-client.zip')
def download_link():
    stats_handler.increment_stat('downloads')

    return redirect('https://github.com/hankhank10/findmyplane-client/releases/download/a0.2/findmyplane-client.zip')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8765, debug=True)

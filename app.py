import os
from flask import Flask, flash, request, redirect, url_for, render_template, flash, jsonify, Response
import secrets
import random
import string

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#import secretstuff

from datetime import datetime


# Define flask variables
app = Flask(__name__)
#app.secret_key = secretstuff.secret_key
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
    ident_public_key = db.Column(db.String)
    ident_private_key = db.Column(db.String)
    current_latitude = db.Column(db.Float)
    current_longitude = db.Column(db.Float)
    current_compass = db.Column(db.Integer)
    current_altitude = db.Column(db.Integer)
    last_update = db.Column(db.DateTime)
    ever_received_data = db.Column(db.Boolean)

    def seconds_since_last_update(self):
        time_difference_seconds = datetime.utcnow() - self.last_update
        return time_difference_seconds.seconds
    
    def is_current(self):
        if minutes_since_last_update < (5 * 60):
            return True
        else:
            return False

# API Endpoints

@app.route('/api/create_new_plane')
def api_new_plane():

    # Generate upper case random public key
    letters = string.ascii_uppercase
    public_key = ''.join(random.choice(letters) for i in range(5))

    # Generate random private key
    private_key = secrets.token_urlsafe(20)

    new_plane = Plane (
        ident_public_key = public_key,
        ident_private_key = private_key,
        current_latitude = 0,
        current_longitude = 0,
        current_compass = 0,
        current_altitude = 0,
        last_update = datetime.utcnow(),
        ever_received_data = False
    )
    
    db.session.add(new_plane)
    db.session.commit()

    output_dictionary = {
        "ident_public_key": public_key,
        "ident_private_key": private_key
    }

    return jsonify(output_dictionary)


@app.route('/api/update_plane_location', methods=['POST'])
def api_update_location():

    data_received = request.json

    plane_to_update = Plane.query.filter_by(ident_public_key = data_received['ident_public_key'], ident_private_key = data_received['ident_private_key']).first_or_404()

    plane_to_update.last_update = datetime.utcnow()
    plane_to_update.ever_received_data = True
    plane_to_update.current_latitude = data_received['current_latitude']
    plane_to_update.current_longitude = data_received['current_longitude']
    plane_to_update.current_compass = data_received['current_compass']
    plane_to_update.current_altitude = data_received['current_altitude']

    db.session.commit()

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
        'seconds_since_last_update': plane.seconds_since_last_update(),
        'minutes_since_last_update': plane.seconds_since_last_update() / 60
    }

    return jsonify(output_dictionary)


# The main event...

@app.route('/')
def index():
    return "Index"


@app.route('/view/<ident_public_key>')
def show_map(ident_public_key):

    plane = Plane.query.filter_by(ident_public_key = ident_public_key).first_or_404()

    return render_template('map.html', ident_public_key = ident_public_key)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8765, debug=True)

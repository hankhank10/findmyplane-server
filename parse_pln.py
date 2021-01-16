import xmltodict
import json
import secrets
import os
from pathlib import Path

from flask import Flask, jsonify, request, render_template
from __main__ import app


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
        print (str(latitude_degrees), str(latitude_minutes), str(latitude_seconds), ">", str(latitude_decimal))

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
    
    return output_dictionary


def save_file(filename, pln_dictionary):
    with open (filename, 'w') as jsonfile:
        json.dump(pln_dictionary['SimBase.Document']['FlightPlan.FlightPlan'], jsonfile, indent=4)


@app.route('/api/upload_pln', methods=['GET', 'POST'])
def receive_upload(simple = True):
    
    if request.method == "GET":
        return render_template('upload.html')


    if request.method == "POST":
        
        if 'file' not in request.files:
            return "No file uploaded"
        
        temporary_filename = secrets.token_urlsafe(25)

        file = request.files['file']
        extension = Path(file.filename).suffix

        if extension != ".pln":
            return "Please upload a .PLN file"

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], temporary_filename))

        new_route = open_file('uploads/' + temporary_filename)
        fixed_route = fix_waypoints(new_route)

        if simple == False:
            return (jsonify(fixed_route))
        
        else:
            simple_route = simplify_route(fixed_route)
            return jsonify(simple_route)

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=11046, debug=True)
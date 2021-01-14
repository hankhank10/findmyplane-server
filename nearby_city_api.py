import requests

def find_closest_city (latitude, longitude):

    latitude_string = "{0:+.05f}".format(latitude)
    longitude_string = "{0:+.05f}".format(longitude)

    lat_lon_string = latitude_string+longitude_string

    url_to_get = "http://geodb-free-service.wirefreethought.com/v1/geo/locations/"+lat_lon_string+"/nearbyCities"
    data_to_pass = {
        'radius': 15000,
        'limit': 1,
        'minPopulation': 1000000
    }

    try:
        r = requests.get(url_to_get, params = data_to_pass)
    except:
        return {'status': 'error'}
    
    if r.status_code != 200:
        return {'status': 'error'}

    if r.json()['data'] == []:
        return {'status': 'error'}

    text_expression = str(round(r.json()['data'][0]['distance'])) + " miles from " + str(r.json()['data'][0]['name'] + ", "+ r.json()['data'][0]['country'])
    dictionary_to_return = {
        'status': "success",
        'name': r.json()['data'][0]['name'],
        'country': r.json()['data'][0]['country'],
        'region': r.json()['data'][0]['region'],
        'distance': r.json()['data'][0]['distance'],
        'text_expression': text_expression
    }

    return dictionary_to_return

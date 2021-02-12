import requests

def find_closest_city (latitude, longitude):

    if latitude == None or longitude == None:
        return {'status': 'error'}
        
    latitude_string = "{0:+.05f}".format(latitude)
    longitude_string = "{0:+.05f}".format(longitude)

    lat_lon_string = latitude_string+longitude_string

    url_to_get = "http://geodb-free-service.wirefreethought.com/v1/geo/locations/"+lat_lon_string+"/nearbyCities"
    data_to_pass = {
        'radius': 15000,
        'limit': 1,
        'minPopulation': 500000,
        'types': 'CITY'
    }

    try:
        r = requests.get(url_to_get, params = data_to_pass)
    except:
        return {'status': 'error'}
    
    if r.status_code != 200:
        return {'status': 'error'}

    if r.json()['data'] == []:
        return {'status': 'error'}

    distance = r.json()['data'][0]['distance']
    distance = round(distance,-2)
    distance = '{:.0f}'.format(distance)

    if distance == "0":
        distance = "over "
    else:
        distance = str(distance) + " miles from "

    text_expression = distance + str(r.json()['data'][0]['name'] + ", "+ r.json()['data'][0]['country'])
    

    #'{:.2f}'.format(round(2606.89579999999, 2))

    if 'region' in r.json()['data'][0]:
        region = r.json()['data'][0]['region']
    else:
        region = None

    dictionary_to_return = {
        'status': "success",
        'name': r.json()['data'][0]['name'],
        'country': r.json()['data'][0]['country'],
        'region': region,
        'distance': r.json()['data'][0]['distance'],
        'text_expression': text_expression
    }

    return dictionary_to_return

import json
from datetime import datetime

# Stat names
homepage_loads = 0
downloads = 0
map_loads = 0
planes_created = 0
location_updates = 0

# JSON filename
filename = "stats.json"


def increment_stat(stat_name):

    if stat_name == "homepage_loads":
        global homepage_loads
        homepage_loads = homepage_loads + 1

    if stat_name == "downloads":
        global downloads
        downloads = downloads + 1

    if stat_name == "map_loads":
        global map_loads
        map_loads = map_loads + 1

    if stat_name == "planes_created":
        global planes_created
        planes_created = planes_created + 1

    if stat_name == "location_updates":
        global location_updates
        location_updates = location_updates + 1

    write_stats_to_json()


def write_stats_to_json():
    
    stats_dictionary = {
        'homepage_loads': homepage_loads,
        'downloads': downloads,
        'map_loads': map_loads,
        'planes_created': planes_created,
        'location_updates': location_updates,
        'last_update': str(datetime.utcnow())
    }

    with open(filename, 'w') as json_file:
        json.dump(stats_dictionary, json_file)


def load_stats_from_json():

    global homepage_loads
    global downloads
    global map_loads
    global planes_created
    global location_updates

    with open(filename, 'r') as json_file:
        stats_dictionary = json.load(json_file)

    homepage_loads = stats_dictionary['homepage_loads']
    downloads = stats_dictionary['downloads']
    map_loads = stats_dictionary['map_loads']
    planes_created = stats_dictionary['planes_created']
    location_updates = stats_dictionary['location_updates']


def return_stats():

    stats_dictionary = {
        'homepage_loads': homepage_loads,
        'downloads': downloads,
        'map_loads': map_loads,
        'planes_created': planes_created,
        'location_updates': location_updates
    }
    return stats_dictionary


load_stats_from_json()

from active_alchemy import ActiveAlchemy
from datetime import datetime
import requests
import json

# Database settings
db = ActiveAlchemy('sqlite:///stats.sqlite')

# Firehose settings
listener_url = "http://listener-nl.logz.io:8070"
token = "zTZFlzdhrkIASAgsZQGFPAolBANBpWwx"
message_type = "MY-TYPE"
combined_url = listener_url + "?token=" + token
combined_url = combined_url + "&type=" + message_type


class RecordableEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String)
    event_detail = db.Column(db.String)
    time_it_happened = db.Column(db.DateTime)
    flushed = db.Column(db.Integer)


def log_event(event_type, event_detail=None):
    new_event = RecordableEvent (
        event_type = event_type,
        event_detail = event_detail,
        time_it_happened = datetime.utcnow(),
        flushed = 0
    )

    db.session.add(new_event)
    db.session.commit()

    return "success"


def count_events(event_type):
    event_count = RecordableEvent.query().filter_by(event_type=event_type).count()
    return event_count


def return_all_events():
    dictionary_to_return = {
        'page_load': count_events('page_load'),
        'map_load': count_events('map_load'),
        'new_plane': count_events('new_plane'),
        'location_update': count_events('location_update'),
        'world_map_load': count_events('world_map_load'),
        'test_event': count_events('test_event'),
        'tweet_sent': count_events('tweet_sent'),
        'tweet_error': count_events('tweet_error'),
        'tweet_nothing_to_say': count_events('tweet_nothing_to_say'),
        'tweet_plane_is_dummy': count_events('tweet_plane_is_dummy'),
        'tweet_plane_is_nowhere': count_events('tweet_plane_is_nowhere')
    }
    return dictionary_to_return


def create_database():
    db.create_all()


def fire_hose():
    new_events = RecordableEvent.query().filter_by(flushed=0).all()

    payload = ""

    for each_event in new_events:
        event_dictionary = {
            'event_id': each_event.id,
            'event_type': each_event.event_type,
            'event_detail': each_event.event_detail,
            'time_it_happened': each_event.time_it_happened.strftime("%m/%d/%Y, %H:%M:%S"),
        }
        event_json = json.dumps(event_dictionary)
        payload = payload + event_json + "\n"
        each_event.flushed = 1

    print (payload)
    if payload == "":
        return "empty"

    r = requests.post(url=combined_url, data=payload)

    if r.status_code == 200:
        db.session.commit()

    print (r.status_code)


#db.create_all()

#for a in range(1,1000):
#    log_event("test_event" + str(a))

#print(str(count_events("test_event")))
#print (fire_hose())

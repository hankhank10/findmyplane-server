from active_alchemy import ActiveAlchemy
from datetime import datetime, timedelta
import requests
import json


# Database settings
db = ActiveAlchemy('mysql+pymysql://mark:kansas01@51.195.171.71/stats')

# Firehose settings
listener_url = "http://listener-nl.logz.io:8070"
token = "zTZFlzdhrkIASAgsZQGFPAolBANBpWwx"
message_type = "MY-TYPE"
combined_url = listener_url + "?token=" + token
combined_url = combined_url + "&type=" + message_type


class RecordableEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(30))
    event_detail = db.Column(db.String(50))
    time_it_happened = db.Column(db.DateTime)
    flushed = db.Column(db.Integer)


def time_range(period_type, how_many_back):

    right_now = datetime.utcnow()

    if period_type.upper() == "DAY":
        reference_point = right_now - timedelta(days=how_many_back)
        start_of_period = reference_point.replace(microsecond=0, second=0, minute=0, hour=0)
        end_of_period = start_of_period + timedelta(days=1)

    if period_type.upper() == "HOUR":
        reference_point = right_now - timedelta(hours=how_many_back)
        start_of_period = reference_point.replace(microsecond=0, second=0, minute=0)
        end_of_period = start_of_period + timedelta(hours=1)

    if period_type.upper() == "MINUTE":
        reference_point = right_now - timedelta(minutes=how_many_back)
        start_of_period = reference_point.replace(microsecond=0, second=0)
        end_of_period = start_of_period + timedelta(minutes=1)

    if how_many_back == 0:
        end_of_period = right_now

    return start_of_period, end_of_period


def log_event(event_type, event_detail=None):
    new_event = RecordableEvent (
        event_type = event_type,
        event_detail = event_detail,
        time_it_happened = datetime.utcnow(),
        flushed = 0
    )

    db.session.add(new_event)
    try:
        db.session.commit()
    except:
        db.session.rollback()

    return "success"


def count_events(event_type = None):
    if event_type is None:
        event_count = RecordableEvent.query().count()
    else:
        event_count = RecordableEvent.query().filter_by(event_type=event_type).count()

    return event_count


def count_events_by_time(event_type, period_type, how_many_back):

    if period_type == "24H":
        start_period = datetime.utcnow() - timedelta(days=how_many_back + 1)
        end_period = datetime.utcnow() - timedelta(days=how_many_back)
    else:
        start_period, end_period = time_range(period_type, how_many_back)
    
    event_count = RecordableEvent.query().filter(
        RecordableEvent.event_type == event_type,
        RecordableEvent.time_it_happened > start_period,
        RecordableEvent.time_it_happened < end_period).count()

    return event_count


def create_event_history(event_type, period_type, most_recent_period, oldest_period):

    event_history = []
    a = 0

    for period in range (most_recent_period, oldest_period+1):

        a = a + 1
        if period_type == "24H":
            period_start = datetime.utcnow() - (timedelta(hours= 24 * a))
            period_end = period_start + (timedelta(hours= 24))
        else:
            # Get the name for the period by getting the start date
            period_start, period_end = time_range(period_type, period)
        
        period_name = period_start

        # Query the DB
        period_value = count_events_by_time(event_type, period_type, period)

        # Return dictionary
        event_dictionary = {
            'date': period_name.timestamp(),
            'sensible_date': period_name.strftime("%d %b"),
            'sensible_hour': period_name.strftime("%H:00 %a"),
            'value': period_value
        }
        event_history.append(event_dictionary)

    return event_history


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
    number_of_events_sent = 0

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
        number_of_events_sent = number_of_events_sent + 1

    #print (payload)
    if payload == "":
        return "empty"

    r = requests.post(url=combined_url, data=payload)
        
    if r.status_code == 200:
        db.session.commit()
        return str(number_of_events_sent) + " events flushed"
    else:
        return "error" + str(r.status_code)



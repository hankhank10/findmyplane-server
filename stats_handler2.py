from active_alchemy import ActiveAlchemy
from datetime import datetime

db = ActiveAlchemy('sqlite:///stats.sqlite')


class RecordableEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String)
    event_detail = db.Column(db.String)
    time_it_happened = db.Column(db.DateTime)


def log_event(event_type, event_detail=None):
    new_event = RecordableEvent (
        event_type = event_type,
        event_detail = event_detail,
        time_it_happened = datetime.utcnow()
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

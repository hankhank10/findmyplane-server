import requests

try:
    listener_url = "http://listener-nl.logz.io:8070"
    token = "zTZFlzdhrkIASAgsZQGFPAolBANBpWwx"
    message_type = "MY-TYPE"
    combined_url = listener_url + "?token=" + token
    combined_url = combined_url + "&type=" + message_type
except:
    print ("Couldn't start firehose")


def send_hose(event_type, page_url = None, plane_id=None, other_variable=None):
    try:
        payload = {
            'event_type': event_type,
            'page_url': event_type,
            'plane_id': plane_id,
            'other_variable': other_variable
        }
        r = requests.post(url=combined_url, json=payload)
    except:
        return "error"

    if r.status_code == 200:
        return "ok"
    else:
        return "error"


send_hose("firehose_started")
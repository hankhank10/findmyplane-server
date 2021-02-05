from datetime import datetime, timedelta


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


start, end = time_range("minute", 24)
print (start.strftime("%m/%d/%Y, %H:%M:%S"))
print (end.strftime("%m/%d/%Y, %H:%M:%S"))


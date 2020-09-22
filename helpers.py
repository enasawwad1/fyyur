import datetime


def get_datetime_now():
    return datetime.datetime.now()


def convert_string_to_datetime(value, format='%Y-%m-%d %H:%S:%M'):
    return datetime.datetime.strptime(value, format)

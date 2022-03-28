import datetime

import dateutil.parser
import pytz
from tzlocal import get_localzone


def assert_datetime_string_format(str_date, date_format='%d/%m/%Y'):
    try:
        datetime.datetime.strptime(str_date, date_format)
    except ValueError:
        raise ValueError(f'Invalid date format ({str_date}), should be {date_format}')


def get_local_timezone():
    timezone_str = str(get_localzone())
    return timezone_str


def get_now():
    now = datetime.datetime.now()
    return set_timezone_on_datetime(now, get_local_timezone())


def get_utc_now():
    now = datetime.datetime.utcnow()
    return set_timezone_on_datetime(now, 'UTC')


def get_yesterday():
    now = datetime.datetime.now() - datetime.timedelta(days=1)
    return set_timezone_on_datetime(now, get_local_timezone())


def get_utc_yesterday():
    now = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    return set_timezone_on_datetime(now, 'UTC')


def get_today_interval():
    today_date = get_now()
    return get_day_interval_from_date(today_date)


def get_day_interval_from_date(date):
    start_date = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
    end_date = datetime.datetime(date.year, date.month, date.day, 23, 59, 59, 999999)
    return [start_date, end_date]


def assert_valid_timezone(timezone):
    if timezone not in pytz.all_timezones:
        raise ValueError(f'Invalid timezone ({timezone})')


def set_timezone_on_datetime(date, timezone):
    timezone = pytz.timezone(timezone)
    localized = timezone.localize(date)
    return localized


def convert_datetime_timezone(localized_date, dst_timezone='UTC'):
    timezone = pytz.timezone(dst_timezone)
    converted = localized_date.astimezone(timezone)
    return converted


def convert_datetime_timezone_to_local(localized_date):
    return convert_datetime_timezone(localized_date, get_local_timezone())


def set_and_convert_date_timezone(date, src_timezone, dst_timezone='UTC'):
    localized = set_timezone_on_datetime(date, src_timezone)
    converted = convert_datetime_timezone(localized, dst_timezone)
    return converted


def datetime_to_string(date, date_format='%d/%m/%Y %H:%M:%S'):
    return date.strftime(date_format)


def string_to_datetime(str_date, date_format='%d/%m/%Y'):
    return datetime.datetime.strptime(str_date, date_format)


def iso_string_to_datetime(str_date):
    return dateutil.parser.isoparse(str_date)


def is_work_day(date):
    return date.weekday() <= 4  # monday=0 | sunday = 6


def add_minutes_to_datetime(date, minutes):
    return date + datetime.timedelta(minutes=minutes)


def add_days_to_datetime(date, days):
    return date + datetime.timedelta(days=days)


def get_all_dates_between(start_date, end_date):
    current_date = datetime.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
    current_date = set_timezone_on_datetime(current_date, 'UTC')
    dates = []
    end_date -= datetime.timedelta(days=1)
    while current_date <= end_date:
        dates.append(current_date)
        current_date += datetime.timedelta(days=1)

    return dates

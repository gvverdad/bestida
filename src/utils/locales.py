# jinja2 fitlers
import logging
import datetime, pytz
import dateutil.parser
from babel.core import Locale
from babel.dates import format_date, format_time, format_datetime

log = logging.getLogger(__name__)


def locale_datetime_format(value, locale="en-au", timezone="Australia/Melbourne"):
    if not isinstance(value, datetime.datetime):
        date_tm = dateutil.parser.parse(value)
    else:
        date_tm = value
    # utc datetime naive to utc aware to timezone aware
    date_tm = pytz.utc.localize(date_tm).astimezone(pytz.timezone(timezone))

    return format_datetime(date_tm, locale=Locale.parse(locale, sep="-"))


def locale_date_format(value, locale="en-au"):
    if not isinstance(value, datetime.date):
        date = dateutil.parser.parse(value)
    else:
        date = value
    return format_date(date, locale=Locale.parse(locale, sep="-"))


def locale_time_format(value, locale="en-au"):
    if not isinstance(value, datetime.time):
        time = dateutil.parser.parse(value)
    else:
        time = value
    return format_time(time, locale=Locale.parse(locale, sep="-"))

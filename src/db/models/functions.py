import babel, iso4217, iso3166
from dateutil.zoneinfo import getzoneinfofile_stream, ZoneInfoFile

from sqlalchemy_continuum.utils import is_versioned

themes_list = None
timezones_list = None
locales_list = None
tables_list = None
app_tables_list = None
versioned_tables_list = None
currencies_list = None
countries_list = None
queues_list = None

def get_spool_keep_days():
    from ...config import config
    return config["spooler"]["keepdays"]


def get_default_country():
    from ...config import config
    return config["defaults"]["country"]


def get_default_currency():
    from ...config import config
    return config["defaults"]["currency"]


def get_default_locale():
    from ...config import config
    return config["defaults"]["locale"]


def get_default_timezone():
    from ...config import config
    return config["defaults"]["timezone"]

def get_default_user_expiry():
    from ...config import config
    return int(config["defaults"]["user_expiry"])  # days

def get_default_password_expiry():
    from ...config import config
    return int(config["defaults"]["password_expiry"])  # days


def get_theme_choices():
    from ...config import config

    global themes_list
    if themes_list is None:
        themes_list = []
        themes = dict(config.items("themes"))
        for k, v in themes.items():
            themes_list.append((k, v))
    return themes_list


def get_timezone_choices():
    global timezones_list
    if timezones_list is None:
        zones = ZoneInfoFile(getzoneinfofile_stream()).zones.keys()
        timezones_list = [(tz, tz) for tz in zones]
    return timezones_list


def get_locale_choices():
    global locales_list
    if locales_list is None:
        locales_list = [(lo.lower().replace("_", "-"),
                         babel.core.Locale.parse(lo).display_name)
                        for lo in babel.localedata.locale_identifiers()]
    return locales_list


def get_tables_choices():
    from ..models.model import Models
    from .. import sqa

    global tables_list
    if tables_list is None:
        tables_list = [(k, sqa.get_table_info(k)["label"])
                       for k, v in Models.items()]
    return tables_list


def get_app_tables_choices():
    from ..models.model import Models
    from .. import sqa

    global app_tables_list
    if app_tables_list is None:
        app_tables_list = [(k, sqa.get_table_info(k)["label"])
                           for k, v in Models.items()
                           if not k.endswith("_version") and not k.startswith("transaction")
                           ]
    return app_tables_list


def get_versioned_tables_choices():
    from ..models.model import Models
    from .. import sqa

    global versioned_tables_list
    if versioned_tables_list is None:
        versioned_tables_list = [(k, sqa.get_table_info(k)["label"])
                                 for k, v in Models.items()
                                 if is_versioned(sqa.get_model(k))]
    return versioned_tables_list


def get_currency_choices():
    global currencies_list
    if currencies_list is None:
        currencies_list = [(c.code, c.currency_name, c.exponent)
                           for c in iso4217.Currency]
    return currencies_list


def get_country_choices():
    global countries_list
    if countries_list is None:
        countries_list = [(c.alpha2, c.apolitical_name)
                          for c in iso3166.countries]
    return countries_list


def get_queue_choices():
    from ...config import config

    global queues_list
    if queues_list is None:
        queues_list = [(q.strip(), q.strip())
                       for q in config["jobqs"]["keys"].split(",")]
    return queues_list

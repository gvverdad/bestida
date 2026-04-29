import logging, time, datetime

log = logging.getLogger(__name__)


def get_timestamp(date_time=None):
    """
        http://stackoverflow.com/questions/29238540/converting-a-datetime-object-to-an-integer-python
    """
    if date_time is None:
        date_time = datetime.datetime.utcnow()
    return int(time.mktime(date_time.timetuple()))


# https://stackoverflow.com/questions/38865201/most-efficient-way-to-search-in-list-of-dicts?rq=1
def search_list_of_dict(lst, key, search_value):
    for d in lst:
        #if get_attr(d, key) == search_value:
        if d[key] == search_value:
            return d
    return None


def search_index_list_of_dict(lst, key, search_value):
    for i, d in enumerate(lst):
        if d[key] == search_value:
            return i
    return -1


# https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary
def sort_list_of_dict(lst, key, desc=False):
    if desc:
        return sorted(lst, key=lambda d: d[key], reverse=True)

    return sorted(lst, key=lambda d: d[key])


def quoter(value, value_type=None, quote_type='"', apply_to_bool=False,
           return_string=False, strip_value=True):
    """
        apply quotes to value
    """
    if value is None:
        return value

    NEEDS_QUOTE = [
        # sqlalchemy.types
        "char", "varchar", "nchar", "nvarchar",
        "text", "unicodetext", "string",
        # datatypes in string format
        "str", "unicode", "enum"
    ]

    if apply_to_bool:
        # sqlalchemy.types
        NEEDS_QUOTE.append("boolean")
        # datatypes in string format
        NEEDS_QUOTE.append("bool")

    if value_type is None:
        value_type = type(value).__name__
    if value_type in ["dict", "list", "tuple"]:
        return value

    if value_type.lower() in NEEDS_QUOTE:
        if hasattr(value, "replace"):  # string
            value = value.replace(quote_type, f"\{quote_type}")  # escape quotes in string
        if strip_value:
            value = value.strip()
        return f"{quote_type}{value}{quote_type}"
    if return_string:
        if strip_value:
            value = value.strip()
        return str(value)
    return value


def string_to_type(data_type, value, timezone=None):
    if data_type == "String":
        return value
    elif data_type == "Boolean":
        if value.strip() == "":
            return False
        return bool(value)
    elif data_type == "Integer":
        if value.strip() == "":
            value = 0
        return int(value)
    elif data_type == "Numeric":
        from decimal import Decimal
        if value.strip() == "":
            value = 0
        return Decimal(value)
    elif data_type == "Date":
        import dateutil.parser
        try:
            return dateutil.parser.parse(value.replace("Z", "")).date()
        except ValueError:
            raise ValueError("Invalid Date: {}".format(value))
    elif data_type == "Time":
        import dateutil.parser
        try:
            return dateutil.parser.parse(value.replace("Z", "")).time()
        except ValueError:
            raise ValueError("Invalid Time: {}".format(value))
    elif data_type == "DateTime":
        import dateutil.parser
        import pytz
        try:
            # parse value to datetime
            # convert naive datetime to timezone aware datetime
            # convert timezone aware to utc datetime
            # then remove tzinfo so value is now naive
            return pytz.timezone(timezone). \
                localize(dateutil.parser.parse(value.replace("Z", ""))). \
                astimezone(pytz.UTC).replace(tzinfo=None)
        except ValueError:
            raise ValueError("Invalid DateTime: {}".format(value))
    elif data_type == "Enum":
        return value
    elif data_type == "Select":
        """
        if implementing Select then
        use this function instead of schemas.datasource.convert_data2 
        
        table = field.selectTable or field.join_list[0][2]
        val = value
        if isinstance(value, dict):
            val = value["Id"]  # must be a record
        if isinstance(val, str) and value.strip() == "":
            value = None
        else:
            value = db_session.query(sqa.get_model(table)).get(int(val))
        """
        raise NotImplementedError
    else:
        return value


# http://code.activestate.com/recipes/577346-getattr-with-arbitrary-depth/
def get_attr(obj, attr, default=None, encode_datetime=True):
    import datetime
    """
    Get a named attribute from an object; getAttr(x, 'a.b.c.d') is
    equivalent to x.a.b.c.d. When a default argument is given, it is
    returned when any attribute in the chain doesn't exist; without
    it, an exception is raised when a missing attribute is encountered.
    """
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            return default

    if encode_datetime:
        if isinstance(obj, (datetime.date, datetime.time, datetime.datetime)):
            obj = obj.isoformat()  # to satisfy json.dumps

    return obj


def set_attr(obj, attrib, value):
    """
        setattr for nested attributes
        ie. User.Id.CreateDate
        will update CreateDate
    """
    if obj is None:
        return None
    a_list = attrib.split('.')
    for a in a_list[:-1]:
        obj = getattr(obj, a)
    setattr(obj, a_list[-1], value)


def get_dict(dic, keys, default=None):
    """
    get nested dict value
    :param dic:
    :param keys: ie. Personal.Firstname
    :param default:
    :return:
    """
    keys = keys.split(".")
    for k in keys:
        if k in dic:
            dic = dic.get(k)
        else:
            return default
    return dic


def set_dict(dic, keys, value, idx=None):
    keys = keys.split(".")
    for k in keys:
        if k in dic:
            dic = dic.get(k)
        else:
            raise KeyError("set_dict KeyError: {}".format(k))

    if idx is not None:
        dic[idx] = value
    else:
        dic = value


def utc_to_timezone(utc_dt, time_zone):
    from dateutil import tz

    utc_zone = tz.gettz('UTC')
    to_zone = tz.gettz(time_zone)

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    utc = utc_dt.replace(tzinfo=utc_zone)

    # Convert time zone
    return utc.astimezone(to_zone)


def copy_nested_fields(src, paths, sep='.'):
    """
    Example usage
    src = {
        "a": 1,
        "b": {"c": 2, "d": {"e": 3, "f": 4}},
        "x": {"y": {"z": 5}}
    }

    paths = ["a", "b.c", "b.d.e", "x.y.z"]
    dst = copy_nested_fields(src, paths)
    print(dst)
    # {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}, 'x': {'y': {'z': 5}}}
    """
    def get_value(d, keys):
        for k in keys:
            d = d[k]
        return d

    result = {}
    for path in paths:
        keys = path.split(sep)
        try:
            value = get_value(src, keys)
        except:
            continue

        # Build nested structure into result
        cur = result   # cur now shares the same reference (pointer) as result - shallow copy
        for k in keys[:-1]:
            cur = cur.setdefault(k, {})
        cur[keys[-1]] = value  # result is also populated here

    return result

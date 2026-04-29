from sqlalchemy import select, text

from ..db import engine
from .misc import get_attr


def search_list_of_records(records, key, search_value):
    for rec in records:
        if get_attr(rec, key) == search_value:
            return rec
    return None


def check_create_sequence(seq_name, start=None, increment=None, minvalue=None,
                          maxvalue=None, cycle=None):
    # Postgres
    stmt = select([1]).where(text(f"sequence_name='{seq_name}'")).\
        select_from(text("information_schema.sequences"))

    with engine.connect() as conn:
        result = conn.execute(stmt)
        sequence_exists = bool(result.scalar())
        if not sequence_exists:
            stmt = f"CREATE SEQUENCE {seq_name}"
            if start is not None:
                stmt += f" START {start}"
            if increment is not None:
                stmt += f" INCREMENT {increment}"
            if minvalue is not None:
                stmt += f" MINVALUE {minvalue}"
            if maxvalue is not None:
                stmt += f" MAXVALUE {maxvalue}"
            if cycle is not None:
                if cycle is True:
                    stmt += f" CYCLE"
                else:
                    stmt += f" NO CYCLE"
            conn.execute(stmt)

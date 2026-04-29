from sqlalchemy import event, and_, func
from sqlalchemy.exc import IntegrityError


def get_null_marker_for_column(col):
    """
    Pick a type-safe NULL marker value depending on column type.
    """
    try:
        pytype = col.type.python_type
    except NotImplementedError:
        # fallback if SQLAlchemy type doesn't expose python_type
        pytype = str

    if pytype == int:
        return -9999999
    elif pytype == float:
        return -9999999.0
    elif pytype == bool:
        return False
    elif pytype.__name__ in ('datetime', 'date', 'time'):
        # a date far in the past
        import datetime
        return datetime.datetime(1900, 1, 1)
    else:
        # default to string marker
        return '__NULL_MARKER__'


def enforce_nullable_unique(model, field_names):
    """
    In PostgreSQL, NULL is not equal to anything, even another NULL.
    So the unique index doesn’t treat two rows with NULLs as duplicates.

    Attach before_insert and before_update listeners enforcing unique combination (NULL == NULL).
    """
    def _check_unique(mapper, connection, target):
        table = target.__table__
        conditions = []

        for fname in field_names:
            col = getattr(table.c, fname)
            val = getattr(target, fname)

            marker = get_null_marker_for_column(col)

            # Use COALESCE so NULL == NULL
            conditions.append(
                func.coalesce(col, marker) == func.coalesce(val, marker)
            )

        # Exclude same row during update
        if getattr(target, 'Id', None) is not None:
            conditions.append(table.c.Id != target.Id)

        query = table.select().where(and_(*conditions))
        result = connection.execute(query).fetchone()

        if result:
            raise IntegrityError(
                f"Duplicate combination in {', '.join(field_names)} not allowed (NULLs treated as equal)",
                params=None,
                orig=None
            )

    # Attach events
    event.listen(model, 'before_insert', _check_unique)
    event.listen(model, 'before_update', _check_unique)

def register_nullable_unique_listeners(base):
    """
        Attach nullable unique enforcement for models that
        declare __nullable_unique_fields__
    """
    for cls in base.__subclasses__():
        table = getattr(cls, '__table__', None)
        if table is None:
            continue

        # Explicitly declared fields
        if hasattr(cls, '__nullable_unique_fields__'):
            enforce_nullable_unique(cls, cls.__nullable_unique_fields__)

        # Recurse for subclass hierarchies (joined-table inheritance)
        if cls.__subclasses__():
            register_nullable_unique_listeners(cls)

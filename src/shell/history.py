from src.db import db_session, sqa
from sqlalchemy.orm import aliased
from sqlalchemy.inspection import inspect
from sqlalchemy_continuum import version_class

from src.db.models.model import Model

# run "./shellserver src.shell.history development.ini" in /home/gvv/Projects/gvv

def get_dynamic_table_history(session, table_name):
    # Reflect the table class from the given table name
    #table_class = Model.metadata.tables.get(table_name)  # <class 'sqlalchemy.sql.schema.Table'>
    table_class = sqa.get_model(table_name)  # <class 'sqlalchemy.ext.declarative.api.DeclarativeMeta'>
    if table_class is None:
        raise ValueError(f"Table '{table_name}' not found in the model registry.")

    # Get the versioned class for the table
    version_table = version_class(table_class)
    #version_class = table_class.__versioned__ #['class']
    version_alias = aliased(version_table)

    # Start building the query
    query = session.query(version_alias)

    # Dynamically add relationships
    relationships = inspect(table_class).relationships
    for rel_name, rel in relationships.items():
        # Check if the related table is versioned
        related_class = rel.mapper.class_
        if not hasattr(related_class, '__versioned__'):
            continue  # Skip if the related table is not versioned


        # Get the versioned class for the related table
        #related_version_class = related_class.__versioned__['class']
        related_version_table = version_class(related_class)
        related_alias = aliased(related_version_table)

        # Join the related version table using the foreign key
        query = query.outerjoin(
            related_alias,
            getattr(version_alias, rel.local_columns.pop().key) == related_alias.Id
        )

        # Add all fields from the related table to the query
        for column in inspect(related_class).columns:
            print(f"{rel_name}_{column.key}")
            query = query.add_columns(getattr(related_alias, column.key).label(f"{rel_name}_{column.key}"))

    # Add all columns from the main versioned table to the query
    for column in inspect(table_class).columns:
        print(f"{table_class.__table__.name}.{column.key}")
        query = query.add_columns(getattr(version_alias, column.key).label(column.key))

    # Optional: Order by version number
    #query = query.order_by(version_alias.version.desc())

    return query

def run(app):
    session = db_session()

    results = get_dynamic_table_history(session, "Users")
    #for row in results:
    #    print(row)

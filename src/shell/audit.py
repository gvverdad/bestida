from src.db import db_session, sqa
from sqlalchemy.orm import aliased
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy_continuum import version_class

from src.schemas.datasource import get_table_list, ListParams
from src.schemas.model import grid_schema
from src.db.models.model import sorted_props

# run "./shellserver src.shell.audit development.ini" in /home/gvv/Projects/gvv

def get_audit_grid_data(session, params):
    try:
        version_table = version_class(sqa.get_model(params.DbTableName))
        # version_table: <class 'sqlalchemy.ext.declarative.api.DeclarativeMeta'>
        table_name = version_table.__table__.name
        sqa.get_model(table_name)
    except:
        raise ValueError(f"Table '{params.DbTableName}' not found in the model registry.")

    user = session.query(sqa.get_model("Users")).get(1)

    company_ids = list()
    # valid companies
    if not user.Role.Group.IsAdmin:
        if params.CompanyRowId is None:
            company_ids.append(user.Company_Id)
        else:
            company_ids.append(params.CompanyRowId)
        for coys in user.Role.Group.Companies:
            if coys.Id not in company_ids:
                company_ids.append(coys.Id)

    if params.Locale is None:
        params.Locale = user.Settings.Locale
    if params.Timezone is None:
        params.Timezone = user.Settings.Timezone

    #for crit in params.Criteria:
    #    if crit["name"] == "operation_type":
    #        if crit["value"].casefold() == "create":
    #            crit["value"] = 0
    #        elif crit["value"].casefold() == "update":
    #            crit["value"] = 1
    #        elif crit["value"].casefold() == "delete":
    #            crit["value"] = 2
    results = get_table_list(table_name, params, session, company_ids)

    for row in results.data:
        if row["operation_type"] == 0:
            row["operation_type"] = "Create"
        elif row["operation_type"] == 1:
            row["operation_type"] = "Update"
        elif row["operation_type"] == 2:
            row["operation_type"] = "Delete"

    return results


def inspect_model(model, version_model, level=0, max_depth=1, audit=False):
    indent = "  " * level
    #mapper = inspect(model)

    mapper, props = sorted_props(model)

    relationships = inspect(version_model).relationships
    for rel_name, rel in relationships.items():
        # Check if the related table is versioned
        related_class = rel.mapper.class_
        print(f"related:{related_class} name:{rel_name} versioned:{hasattr(related_class, '__versioned__')}")
        if not hasattr(related_class, '__versioned__'):
            continue  # Skip if the related table is

    for prop in props:
        if isinstance(prop, ColumnProperty):
            print(f"{indent}Column: {prop.key}, Type: {prop.columns[0].type}")
        elif isinstance(prop, RelationshipProperty):
            if prop.key == "versions" or prop.key == "version_parent" or prop.key == "transaction":
                continue
            print(f"{indent}Relationship: {prop.key}, Target: {prop.mapper.class_.__name__}")

            # Recurse one level deep
            if level < max_depth:
                inspect_model(prop.mapper.class_, level=level + 1, max_depth=max_depth)

def get_grid_schema(table_name):
    table_class = sqa.get_model(table_name)  # <class 'sqlalchemy.ext.declarative.api.DeclarativeMeta'>
    if table_class is None:
        raise ValueError(f"Table '{table_name}' not found in the model registry.")

    version_table = version_class(table_class)
    inspect_model(version_table, table_class)
    #inspect_model(table_class)
    print("get_grid_schema")

def get_audit_grid_schema(table_name):
    # Reflect the table class from the given table name
    #table_class = Model.metadata.tables.get(table_name)  # <class 'sqlalchemy.sql.schema.Table'>
    table_class = sqa.get_model(table_name)  # <class 'sqlalchemy.ext.declarative.api.DeclarativeMeta'>
    if table_class is None:
        raise ValueError(f"Table '{table_name}' not found in the model registry.")

    # Get the versioned class for the table
    version_table = version_class(table_class)
    #version_class = table_class.__versioned__ #['class']

    # Dynamically add relationships
    relationships = inspect(table_class).relationships
    for rel_name, rel in relationships.items():
        # Check if the related table is versioned
        related_class = rel.mapper.class_
        print(f"related:{related_class} name:{rel_name} versioned:{hasattr(related_class, '__versioned__')}")
        if not hasattr(related_class, '__versioned__'):
            continue  # Skip if the related table is not versioned

        # Get the versioned class for the related table
        #related_version_class = related_class.__versioned__['class']
        related_version_table = version_class(related_class)
        related_alias = aliased(related_version_table)

        # Add all fields from the related table to the query
        for column in inspect(related_class).columns:
            print(f"{rel_name}_{column.key}")

    # Add all columns from the main versioned table to the query
    for column in inspect(table_class).columns:
        print(f"{table_class.__table__.name}.{column.key}")



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
        print(f"related:{related_class} name:{rel_name} versioned:{hasattr(related_class, '__versioned__')}")
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

    for row in query:
        print(row)

def run(app):
    session = db_session()

    table_name = "Companies"

    #get_grid_data(session, table_name)
    #get_dynamic_table_history(session, table_name)
    #get_audit_grid_schema(table_name)
    get_grid_schema(table_name)


def get_grid_data(session, table_name):
    params = ListParams(Depth=1,
                        CompanyRowId=1,
                        Locale="en-au",
                        Timezone="Australia/Melbourne",
                        DbTableName=table_name,
                        Offset=0,
                        PageSize=9999,
                        ChoicesAsTuple=False,
                        ChoicesKey=True,
                        TextAsString=True,
                        Draw=1)

    results = get_audit_grid_data(session, params)
    for row in results.data:
        print(row)

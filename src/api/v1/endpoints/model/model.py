import logging, copy
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db  # an object to provide global access to a database session
from sqlalchemy_continuum import version_class

from .....db import sqa
from .....db.models.model import Models
from .....db.models.security.Users import User as DBUser
from .....security.policy import get_current_user
from .....schemas.model import (Table, TableSchema, Field, FormSchemaParams,
                                FieldSchema, FormSchema, FormField, GridSchema,
                                form_schema, form_field_schema, grid_schema)
from .....schemas.datasource import EnumResult
from .....db.models.functions import (get_tables_choices,
                                      get_app_tables_choices,
                                      get_versioned_tables_choices)
from .....utils.misc import search_list_of_dict
from .....cache import cache

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tables", response_model=List[Table], tags=["model"])
def get_tables(current_user_id: DBUser = Depends(get_current_user)):
    return [sqa.get_table_info(k) for k, v in Models.items()]


@router.get("/getTablesList", response_model=EnumResult, tags=["model"])
def get_table_choices(current_user_id: DBUser = Depends(get_current_user)):
    tables = get_tables_choices()

    results = dict()
    results["draw"] = 1
    results["recordsTotal"] = len(tables)
    results["data"] = tables

    return EnumResult.model_validate(results)


@router.get("/getAppTablesList", response_model=EnumResult, tags=["model"])
def get_app_table_choices(current_user_id: DBUser = Depends(get_current_user)):
    tables = get_app_tables_choices()

    results = dict()
    results["draw"] = 1
    results["recordsTotal"] = len(tables)
    results["data"] = tables

    return EnumResult.model_validate(results)


@router.get("/getVersionedTablesList", response_model=EnumResult, tags=["model"])
def get_versioned_table_choices(current_user_id: DBUser = Depends(get_current_user)):
    tables = get_versioned_tables_choices()

    results = dict()
    results["draw"] = 1
    results["recordsTotal"] = len(tables)
    results["data"] = tables

    return EnumResult.model_validate(results)


@router.get("/tableSchema/{table_name}", response_model=TableSchema, tags=["model"])
def get_table_schema(table_name: str,
                     current_user_id: DBUser = Depends(get_current_user)):
    from .....config import config

    cache_tables = False
    if "tables" in config["cache"]:
        cache_tables = config.getboolean("cache", "tables")

    if cache_tables:
        cache_name = f"table_schema_{table_name}"
        if cache_name in cache:
            return TableSchema.model_validate(cache[cache_name])

    try:
        schema = sqa.get_table_info(table_name)
        if cache_tables:
            cache[cache_name] = schema
        return TableSchema.model_validate(schema)
    except:
        raise HTTPException(status_code=500, detail="Invalid Table: {}".format(table_name))


@router.get("/tableFields/{table_name}", response_model=List[Field], tags=["model"])
def get_table_fields(table_name: str,
                     level: int = 1,
                     current_user_id: DBUser = Depends(get_current_user)):
    from .....config import config

    cache_fields = False
    if "fields" in config["cache"]:
        cache_fields = config.getboolean("cache", "fields")

    if cache_fields:
        cache_name = f"table_fields_{table_name}"
        if cache_name in cache:
            return cache[cache_name]

    try:
        schema = sqa.get_schema(table_name, level)
        if cache_fields:
            cache[cache_name] = schema
        return schema
    except:
        raise HTTPException(status_code=500, detail="Invalid Table: {}".format(table_name))


@router.get("/tableFieldSchema/{table_name}/{field_name}", response_model=FieldSchema, tags=["model"])
def get_table_field_schema(table_name: str,
                           field_name: str,
                           level: int = 1,
                           current_user_id: DBUser = Depends(get_current_user)):
    from .....config import config

    cache_fields = False
    if "fields" in config["cache"]:
        cache_fields = config.getboolean("cache", "fields")

    if cache_fields:
        cache_name = f"table_field_schema_{table_name}_{field_name}"
        if cache_name in cache:
            return FieldSchema.model_validate(cache[cache_name])

    try:
        schema = sqa.get_schema(table_name, level)
        for scheme in schema:
            if scheme["name"] == field_name:
                if cache_fields:
                    cache[cache_name] = scheme
                return FieldSchema.model_validate(scheme)
        raise HTTPException(status_code=500, detail="Invalid Field {} in Table {} ".format(field_name, table_name))
    except:
        raise HTTPException(status_code=500, detail="Invalid Table/Field: {}/{} ".format(table_name,field_name))


@router.get("/formSchema/{table_name}", response_model=FormSchema, tags=["model"])
def get_form_schema(table_name: str,
                    level: int = 1,
                    main_form: bool = True,
                    current_user_id: DBUser = Depends(get_current_user)):
    from .....config import config

    cache_forms = False
    if "forms" in config["cache"]:
        cache_forms = config.getboolean("cache", "forms")

    if cache_forms:
        cache_name = f"form_schema_{table_name}"
        if cache_name in cache:
            return FormSchema.model_validate(cache[cache_name])

    form_panels = list()
    info = sqa.get_table_info(table_name)
    form_panels.append(dict(table=table_name,
                            label=info["label"],
                            desc=info["desc"],
                            baseTable=info["baseTable"],
                            keyField=info["key"],
                            parent=None,
                            type=None,
                            use_list=False,
                            id=None,
                            actionOn=list(),
                            key=None,
                            joinlist=list(),
                            subTableType="GRID",
                            viewer=info["viewer"] if "viewer" in info else None,
                            loader=info["loader"] if "loader" in info else None,
                            documents=info["documents"] if "documents" in info else None,
                            subTables= info["subTables"] if "subTables" in info else None
                            ))

    stepper_title_fields = info["stepperTitleFields"] if "stepperTitleFields" in info else None
    schema = sqa.get_schema(table_name, level)
    scheme = form_schema(table_name, form_panels, schema, table_name, main_form,
                         except_fields=["Password", "versions"])

    f_schema = dict(stepper_title_fields=stepper_title_fields,
                    form_fields=scheme,
                    form_panels=form_panels)
    if cache_forms:
        cache[cache_name] = f_schema

    return FormSchema.model_validate(f_schema)


@router.post("/buildFormSchema/", response_model=FormSchema, tags=["model"])
def build_form_schema(params: FormSchemaParams,
                      current_user_id: DBUser = Depends(get_current_user)):

    form_panels = list()
    form_fields = list()

    for tf in params.table_field_pair:
        try:
            if not any(obj['table'] == tf.dummy_table_name for obj in form_panels):
                form_panels.append(dict(table=tf.dummy_table_name))
            schema = sqa.get_schema(tf.table_name, 1)
            for scheme in schema:
                if not (scheme["table"] == tf.table_name and
                        scheme["name"] == tf.field_name):
                    continue

                f_schema = form_field_schema(scheme)
                if tf.name is not None:
                    f_schema["name"] = tf.name
                if tf.label is not None:
                    f_schema["label"] = tf.label
                if tf.validator is not None:
                    f_schema["validator"] = tf.validator
                if tf.selectField is not None:
                    f_schema["selectField"] = tf.selectField
                    f_schema["selectFieldValue"] = tf.selectFieldValue
                if tf.selectTableFieldValue is not None:
                    f_schema["selectTableFieldValue"] = tf.selectTableFieldValue
                if tf.default is not None:
                    f_schema["default"] = tf.default
                if tf.required is not None:
                    f_schema["required"] = tf.required
                f_schema["table"] = tf.dummy_table_name
                f_schema["join"] = False
                f_schema["join_list"] = None
                if f_schema["selectKey"] is not None:
                    f_schema["type"] = "Select"
                    f_schema["length"] = 0
                    f_schema["decimals"] = 0
                    f_schema["selectTable"] = tf.table_name
                    f_schema["selectObject"] = tf.table_name
                    info = sqa.get_table_info(tf.table_name)
                    f_schema["reprField"] = info["reprField"] if "reprField" in info else None

                f_schema["modifiable"] = True
                f_schema["displayable"] = False
                form_fields.append(f_schema)
                break
        except Exception as errs:
            raise HTTPException(status_code=500,
                                detail="Invalid Table/Field: {}/{} {}".
                                format(tf.table_name, tf.field_name, str(errs)))
    return FormSchema.model_validate((dict(stepper_title_fields=None,
                                           form_fields=form_fields,
                                           form_panels=form_panels)))


@router.get("/formFieldSchema/{table_name}/{field_name}", response_model=FormField, tags=["model"])
def get_form_field_schema(table_name: str,
                          field_name: str,
                          level: int = 1,
                          current_user_id: DBUser = Depends(get_current_user)):
    from .....config import config

    cache_fields = False
    if "fields" in config["cache"]:
        cache_fields = config.getboolean("cache", "fields")

    if cache_fields:
        cache_name = f"form_field_schema_{table_name}_{field_name}"
        if cache_name in cache:
            return FormField.model_validate(cache[cache_name])

    try:
        schema = sqa.get_schema(table_name, level)
        for scheme in schema:
            if scheme["name"] == field_name:
                ff_schema = form_field_schema(scheme)
                if cache_fields:
                    cache[cache_name] = ff_schema
                return FormField.model_validate(ff_schema)
        raise HTTPException(status_code=500, detail="Invalid Field {} in Table {} ".format(field_name, table_name))
    except:
        raise HTTPException(status_code=500, detail="Invalid Table/Field: {}/{} ".format(table_name,field_name))


@router.get("/gridSchema/{table_name}", response_model=GridSchema, tags=["model"])
def get_grid_schema(table_name: str,
                    level: int = 1,
                    current_user_id: DBUser = Depends(get_current_user)):
    from .....config import config

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    cache_grids = False
    if "grids" in config["cache"]:
        cache_grids = config.getboolean("cache", "grids")

    if cache_grids:
        cache_name = f"grid_schema_{table_name}"
        if cache_name in cache:
            return GridSchema.model_validate(cache[cache_name])

    grid_tables = list()
    try:
        info = sqa.get_table_info(table_name)
    except:
        raise HTTPException(status_code=500, detail=f"getGridSchema Invalid Table {table_name}")

    except_fields = ["Password", "versions"]
    if "companyField" in info:
        if user.Role.IsAdmin:
            # admin - see all valid companies
            pass
        else:
            except_fields.append("Company")

    grid_tables.append(dict(table=table_name,
                            use_list=False,
                            parent=None,
                            field_list=None,
                            join_list=list(),
                            label=info["label"],
                            desc=info["desc"],
                            baseTable=info["baseTable"],
                            subTableType="GRID",
                            viewer=info["viewer"] if "viewer" in info else None,
                            loader=info["loader"] if "loader" in info else None,
                            documents=info["documents"] if "documents" in info else None,
                            subTables=info["subTables"] if "subTables" in info else None,
                            crud_constraint=info["crud_constraint"] if "crud_constraint" in info else None,
                            crud_options=info["crud_options"] if "crud_options" in info else None
                            )
                       )

    groups = None
    sum_fields = None
    if "sumGroups" in info:
        groups = info["sumGroups"]
    if "sum" in info:
        groups += info["sum"]
        sum_fields = info["sum"]

    schema = sqa.get_schema(table_name, level, remove_duplicate_tables=True)
    scheme = grid_schema(schema, table_name, grid_tables, table_name,
                         except_fields=except_fields, sum_groups=groups,
                         sum_fields=sum_fields
                         )

    if "runningBalance" in info and info["runningBalance"] is not None:
        for b in info["runningBalance"]:
            fld = search_list_of_dict(scheme, "name", b)
            if fld:
                rb_fld = copy.deepcopy(fld)
                rb_fld["name"] = f"RunningBalance_{b}"
                rb_fld["label"] = f"RunningBalance {fld['label']}"
                rb_fld["column_label"] = rb_fld["label"]
                rb_fld["sortable"] = False
                rb_fld["searchable"] = False
                scheme.append(rb_fld)

    g_schema = dict(grid_fields=scheme, grid_tables=grid_tables)
    if cache_grids:
        cache[cache_name] = g_schema

    return GridSchema.model_validate(g_schema)


@router.get("/auditGridSchema/{table_name}", response_model=GridSchema, tags=["model"])
def get_audit_grid_schema(table_name: str,
                          level: int = 1,
                          current_user_id: DBUser = Depends(get_current_user)):
    from .....config import config

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    try:
        app_table = sqa.get_model(table_name)
        version_table = version_class(app_table)
        # version_table: <class 'sqlalchemy.ext.declarative.api.DeclarativeMeta'>
        version_name = version_table.__table__.name
    except:
        raise HTTPException(status_code=500, detail=f"getAuditGridSchema Invalid Versioned Table {table_name}")

    cache_grids = False
    if "grids" in config["cache"]:
        cache_grids = config.getboolean("cache", "grids")

    if cache_grids:
        cache_name = f"audit_grid_schema_{version_name}"
        if cache_name in cache:
            return GridSchema.model_validate(cache[cache_name])

    grid_tables = list()
    try:
        info = sqa.get_table_info(table_name)
    except:
        raise HTTPException(status_code=500, detail=f"getGridSchema Invalid Table {table_name}")

    except_fields = ["Password", "version_parent"]
    if "companyField" in info:
        if user.Role.IsAdmin:
            # admin - see all valid companies
            pass
        else:
            except_fields.append("Company")

    grid_tables.append(dict(table=version_name,
                            use_list=False,
                            parent=None,
                            field_list=None,
                            join_list=list(),
                            label=info["label"],
                            desc=info["desc"],
                            baseTable=info["baseTable"],
                            subTableType="GRID",
                            viewer=info["viewer"] if "viewer" in info else None,
                            loader=info["loader"] if "loader" in info else None,
                            documents=info["documents"] if "documents" in info else None,
                            subTables=info["subTables"] if "subTables" in info else None,
                            crud_constraint=info["crud_constraint"] if "crud_constraint" in info else None,
                            crud_options=info["crud_options"] if "crud_options" in info else None
                            )
                       )

    schema = sqa.get_schema(table_name, level, audit=True)
    scheme = grid_schema(schema, version_name, grid_tables, version_name,
                         except_fields=except_fields)

    for s in scheme:
        if s["name"] == "transaction_id":
            s["label"] = "Start Transaction Id"
            s["column_label"] = "Start Transaction Id"
        elif s["name"] == "end_transaction_id":
            s["label"] = "End Transaction Id"
            s["column_label"] = "End Transaction Id"
        elif s["name"] == "operation_type":
            s["type"] = "String"
            s["length"] = 6
            s["label"] = "Operation Type"
            s["column_label"] = "Operation Type"
        elif s["name"] == "transaction.issued_at":
            s["label"] = "Transaction TimeStamp"
            s["column_label"] = "Transaction TimeStamp"
        elif s["name"] == "transaction.remote_addr":
            s["label"] = "Remote Address"
            s["column_label"] = "Remote Address"
        elif s["name"] == "transaction.user_id":
            s["label"] = "Transaction User"
            s["column_label"] = "Transaction User"

    g_schema = dict(grid_fields=scheme, grid_tables=grid_tables)
    if cache_grids:
        cache[cache_name] = g_schema
    return GridSchema.model_validate(g_schema)

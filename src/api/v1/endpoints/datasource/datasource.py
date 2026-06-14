import logging, shutil, io
import magic

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi_sqlalchemy import db  # an object to provide global access to a database session
from typing import List
from sqlalchemy_continuum import version_class
from sqlalchemy import select, exists, and_, UniqueConstraint


from .....db import sqa
from .....db.models.security.Users import User as DBUser
from .....security.policy import get_current_user
from .....schemas.datasource import (ListParams, ListChildParams, ListResult,
                                     ListCriteriaType,
                                     FormParams, FormParamsCriteria,
                                     FormChildParams, FormResult,
                                     build_join_alias, build_filters,
                                     build_where, query,
                                     get_table_list, form_data,
                                     CUDParams, CUDChildParams,
                                     SequentialCUDParams, SequentialCUDChildParams,
                                     CUDStatus, CUDAvail, populate_record,
                                     UploadFileResult, upload_image_file)
from .....utils.misc import get_attr, quoter
from .....config import config
from .....server.jobq.tasks import get_work_filename, get_image_filename

log = logging.getLogger(__name__)

router = APIRouter()


# You cannot send a request body using a GET operation (HTTP method).
# To send data, you have to use one of: POST (the more common), PUT, DELETE or PATCH.
@router.post("/list", response_model=ListResult, tags=["datasource"])
def get_grid_data(params: ListParams,
                  current_user_id: DBUser = Depends(get_current_user)):

    try:
        sqa.get_model(params.DbTableName)
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid DbTableName: {params.DbTableName}")

    return get_table_list(params.DbTableName, params, db.session, current_user_id)


# You cannot send a request body using a GET operation (HTTP method).
# To send data, you have to use one of: POST (the more common), PUT, DELETE or PATCH.
@router.post("/listChild", response_model=ListResult, tags=["datasource"])
def get_child_grid_data(params: ListChildParams,
                        current_user_id: DBUser = Depends(get_current_user)):

    try:
        sqa.get_model(params.ParentTable)
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid ParentTable: {params.ParentTable}")

    parent = db.session.query(sqa.get_model(params.ParentTable)).get(params.ParentRowId)
    if parent is None:
        raise HTTPException(status_code=500,
                            detail=f"Invalid ParentTable ParentRowId: {params.ParentTable} {params.ParentRowId}")
    prop = parent.get_property_by_name(params.ParentField)
    if prop is None:
        raise HTTPException(status_code=500,
                            detail=f"Invalid ParentTable ParentField: {params.ParentTable} {params.ParentField}")

    # get parent Id
    parent_id = parent.Id
    if "." in params.ParentField:  # a.b.c.d
        path = params.ParentField.split(".")[:-1]   # a.b.c
        for p in path:
            parent = get_attr(parent, p)
            parent_id = parent.Id

    db_table_name = list(prop.remote_side)[0].table.name
    key = list(prop.remote_side)[0].key
    where = f"{key} = {parent_id}"

    return get_table_list(db_table_name, params, db.session, current_user_id, where)

@router.post("/auditList", response_model=ListResult, tags=["datasource"])
def get_audit_grid_data(params: ListParams,
                        current_user_id: DBUser = Depends(get_current_user)):
    try:
        table_class = sqa.get_model(params.DbTableName)
        version_table = version_class(table_class)
        # version_table: <class 'sqlalchemy.ext.declarative.api.DeclarativeMeta'>
        table_name = version_table.__table__.name
        sqa.get_model(table_name) # side effect - exception if table_name is not valid
    except:
        raise HTTPException(status_code=500, detail=f"getAuditGridData Invalid Versioned Table {params.DbTableName}")

    for crit in params.Criteria:
        if crit["field"] == "operation_type":
            if crit["value"].casefold() == "create":
                crit["value"] = 0
            elif crit["value"].casefold() == "update":
                crit["value"] = 1
            elif crit["value"].casefold() == "delete":
                crit["value"] = 2

    results = get_table_list(table_name, params, db.session, current_user_id,
                             audit=True,
                             table_class=table_class)

    for row in results.data:
        if row["operation_type"] == 0:
            row["operation_type"] = "Create"
        elif row["operation_type"] == 1:
            row["operation_type"] = "Update"
        elif row["operation_type"] == 2:
            row["operation_type"] = "Delete"
    return results


# You cannot send a request body using a GET operation (HTTP method).
# To send data, you have to use one of: POST (the more common), PUT, DELETE or PATCH.
@router.post("/formData", response_model=FormResult, tags=["datasource"])
def get_form_data_by_row_id(params: FormParams,
                            current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    try:
        sqa.get_model(params.DbTableName)
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid DbTableName: {params.DbTableName}")

    if params.Mode.value == "Create":
        if params.RowId != 0:
            raise HTTPException(status_code=500,
                                detail="RowId Should be 0 for Mode Create")
    elif params.RowId < 1:
        raise HTTPException(status_code=500,
                            detail=f"Invalid RowId for Mode {params.Mode.value}")

    if params.RowId == 0:
        return dict(data=dict())

    if params.CompanyRowId is None:
        params.CompanyRowId = user.Company_Id
    if params.Locale is None:
        params.Locale = user.Settings.Locale
    if params.Timezone is None:
        params.Timezone = user.Settings.Timezone

    record = db.session.query(sqa.get_model(params.DbTableName)).get(params.RowId)
    if record is None:
        raise HTTPException(status_code=500,
                                detail=f"No {params.DbTableName} Record found for RowId {params.RowId} in {params.Mode.value} Mode")
    return form_data(record, params)


@router.post("/formDataCriteria", response_model=FormResult, tags=["datasource"])
def get_form_data_by_criteria(params: FormParamsCriteria,
                              current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    try:
        sqa.get_model(params.DbTableName)
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid DbTableName: {params.DbTableName}")

    if params.Mode.value == "Create":
        if params.Criteria:
            raise HTTPException(status_code=500,
                                detail="Criteria Should be null for Mode Create")
    elif not params.Criteria:
        raise HTTPException(status_code=500,
                            detail=f"Invalid Criteria for Mode {params.Mode.value}")

    company_ids = list()
    # valid companies
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

    if params.Criteria:
        sort = list()
        columns = list()
        joins = list()
        join_tables = dict()
        filters, joins, join_tables = build_filters(params.DbTableName, params.Criteria,
                                                    joins, join_tables)
        alias = build_join_alias(joins, join_tables)
        where = build_where(params.DbTableName, params.Timezone, filters,
                            ListCriteriaType.ALL, join_tables, alias,
                            user.Company_Id, company_ids)

        record = query(db.session, params.DbTableName, columns,
                       where, sort, join_tables, joins, alias
                       ).first()
        if record is None:
            return dict(data=dict())
    else:
        return dict(data=dict())

    return form_data(record, params)

# You cannot send a request body using a GET operation (HTTP method).
# To send data, you have to use one of: POST (the more common), PUT, DELETE or PATCH.
@router.post("/formChildData", response_model=FormResult, tags=["datasource"])
def get_child_form_data(params: FormChildParams,
                        current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    try:
        sqa.get_model(params.ParentTable)
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid ParentTable: {params.ParentTable}")

    parent = db.session.query(sqa.get_model(params.ParentTable)).get(params.ParentRowId)
    if parent is None:
        raise HTTPException(status_code=500,
                            detail=f"Invalid ParentTable ParentRowId: {params.ParentTable} {params.ParentRowId}")
    prop = parent.get_property_by_name(params.ParentField)
    if prop is None:
        raise HTTPException(status_code=500,
                            detail=f"Invalid ParentTable ParentField: {params.ParentTable} {params.ParentField}")

    if params.Mode.value == "Create":
        if params.RowId != 0:
            raise HTTPException(status_code=500,
                                detail="RowId Should be 0 for Mode Create")
    elif params.RowId < 1:
        raise HTTPException(status_code=500,
                            detail=f"Invalid RowId for Mode {params.Mode.value}")

    if params.RowId == 0:
        return dict(data=dict())

    if params.CompanyRowId is None:
        params.CompanyRowId = user.Company_Id
    if params.Locale is None:
        params.Locale = user.Settings.Locale
    if params.Timezone is None:
        params.Timezone = user.Settings.Timezone

    db_table_name = list(prop.remote_side)[0].table.name

    record = db.session.query(sqa.get_model(db_table_name)).get(params.RowId)
    if record is None:
        raise HTTPException(status_code=500,
                            detail=f"No {db_table_name}.{params.ParentField} Record found for RowId {params.RowId} in {params.Mode.value} Mode")

    return form_data(record, params)


@router.post("/isTableAvail", response_model=CUDAvail, tags=["datasource"])
def is_table_available(params: CUDParams,
                       current_user_id: DBUser = Depends(get_current_user)):
    # validate
    try:
        table = sqa.get_model(params.DbTableName).__table__
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid DbTableName: {params.DbTableName}")

    if params.RowId:
        record = db.session.query(sqa.get_model(params.DbTableName)).get(params.RowId)
        if record is None:
            return CUDAvail(IsAvail=False)
        return CUDAvail(IsAvail=True)

    # check constraints
    for constraint in table.constraints:
        if isinstance(constraint, UniqueConstraint):
            cols = [c.name for c in constraint.columns]

            if all(c in params.Data for c in cols):
                where = ""
                for c in cols:
                    where += (f"{' and ' if where != '' else ''}" 
                              f"{table.c[c]} = {quoter(params.Data[c])}")
                record = (db.session.query(sqa.get_model(params.DbTableName)).
                          filter(sqa.where(where)).first())
                if record is None:
                    return CUDAvail(IsAvail=False)
                return CUDAvail(IsAvail=True)

    # check unique index
    for idx in table.indexes:
        if idx.unique:
            cols = [c.name for c in idx.columns]

            if all(c in params.Data for c in cols):
                where = ""
                for c in cols:
                    where += (f"{' and ' if where != '' else ''}" 
                              f"{table.c[c]} = {quoter(params.Data[c])}")
                record = (db.session.query(sqa.get_model(params.DbTableName)).
                          filter(sqa.where(where)).first())
                if record is None:
                    return CUDAvail(IsAvail=False)
                return CUDAvail(IsAvail=True)

    # check multiple data columns
    where = ""
    for k, v in params.Data.items():
        where += (f"{' and ' if where != '' else ''}"
                  f"{table.c[k]} = {quoter(v)}")
    record = (db.session.query(sqa.get_model(params.DbTableName)).
              filter(sqa.where(where)).first())
    if record is None:
        return CUDAvail(IsAvail=False)
    return CUDAvail(IsAvail=True)


# https://restfulapi.net/rest-put-vs-post/
# Use PUT when you want to modify a singular resource which is already a part of resources collection.
# PUT replaces the resource in its entirety. Use PATCH if request updates part of the resource.
# Use POST when you want to add a child resource under resources collection.
@router.post("/createTable", response_model=CUDStatus, tags=["datasource"])
def create_table(params: CUDParams,
                 current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    # validate
    try:
        record = sqa.get_model(params.DbTableName)()
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid DbTableName: {params.DbTableName}")

    if params.RowId:
        raise HTTPException(status_code=500,
                            detail=f"Invalid RowId for createTable: {params.RowId}")

    # table validation
    validate = getattr(record, "validate_create", None)
    if validate is not None:
        is_ok, message = validate(user.Id, params.CompanyRowId, params.Locale, params.Timezone, params.Data)
        if not is_ok:
            raise HTTPException(status_code=500, detail=message)

    # field validation
    # TODO: fields validation

    # defaults
    if params.CompanyRowId is None:
        params.CompanyRowId = user.Company_Id
    if params.Locale is None:
        params.Locale = user.Settings.Locale
    if params.Timezone is None:
        params.Timezone = user.Settings.Timezone

    # create
    try:
        with db.session.no_autoflush:
            if params.Schema is None:
                populate_record(db.session, record, params.DbTableName, params.CompanyRowId, params.Timezone,
                                params.Data, create=True)
            else:
                populate_record(db.session, record, params.DbTableName, params.CompanyRowId, params.Timezone,
                                params.Data, params.Schema.form_fields, params.Schema.form_panels,
                                create=True)

        db.session.add(record)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        log.error(f"v1.datasource.create_table error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))

    return CUDStatus(success=True, message="OK", RecordRowId=record.Id)


@router.post("/createChildTable", response_model=CUDStatus, tags=["datasource"])
def create_child_table(params: CUDChildParams,
                       current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    # validate
    try:
        if params.join_list:
            table_name = params.join_list[-1][2]
        else:
            table_name = params.DbTableName
        record = sqa.get_model(table_name)()
        is_poly_base = record.is_poly_base()
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid DbTableName: {params.DbTableName}")

    if is_poly_base:
        poly_on = record.get_poly_base_on_name()
        try:
            record = record.get_poly_base_on_obj(params.Data[poly_on])
        except Exception as err:
            raise HTTPException(status_code=500,
                                detail=f"Invalid Polymorphic Identity: {params.Data[poly_on]} for {params.DbTableName}")

    if params.RowId:
        raise HTTPException(status_code=500,
                            detail=f"Invalid RowId for createChildTable: {params.RowId}")

    # table validation
    validate = getattr(record, "validate_create", None)
    if validate is not None:
        is_ok, message = validate(user.Id, params.CompanyRowId, params.Locale, params.Timezone, params.Data)
        if not is_ok:
            raise HTTPException(status_code=500, detail=message)

    # field validation
    # TODO: fields validation

    # defaults
    if params.CompanyRowId is None:
        params.CompanyRowId = user.Company_Id
    if params.Locale is None:
        params.Locale = user.Settings.Locale
    if params.Timezone is None:
        params.Timezone = user.Settings.Timezone

    # create
    try:
        with db.session.no_autoflush:
            if params.Schema is None:
                populate_record(db.session, record, params.DbTableName, params.CompanyRowId, params.Timezone,
                                params.Data, create=True)
            else:
                populate_record(db.session, record, params.DbTableName, params.CompanyRowId, params.Timezone,
                                params.Data, params.Schema.form_fields, params.Schema.form_panels,
                                create=True)
        db.session.add(record)
        parent = db.session.query(sqa.get_model(params.ParentTable)).with_for_update().get(params.ParentRowId)
        if parent is None:
            raise HTTPException(status_code=500,
                                detail=f"No {params.ParentTable} Parent Record found for RowId {params.ParentRowId} in Create Mode")

        parent_field = get_attr(parent, params.ParentField)
        if isinstance(parent_field, list):
            parent_field.append(record)
        else:
            parent_field = record
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        log.error(f"v1.datasource.create_child_table error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))

    return CUDStatus(success=True, message="OK", RecordRowId=record.Id)


# https://restfulapi.net/rest-put-vs-post/
# Use PUT when you want to modify a singular resource which is already a part of resources collection.
# PUT replaces the resource in its entirety. Use PATCH if request updates part of the resource.
# Use POST when you want to add a child resource under resources collection.
@router.put("/updateTable", response_model=CUDStatus, tags=["datasource"])
def update_table(params: CUDParams,
                 current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    try:
        sqa.get_model(params.DbTableName)
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid DbTableName: {params.DbTableName}")

    record = db.session.query(sqa.get_model(params.DbTableName)).with_for_update().get(params.RowId)
    if record is None:
        raise HTTPException(status_code=500,
                            detail=f"No {params.DbTableName} Record found for RowId {params.RowId} in Update Mode")

    # table validation
    validate = getattr(record, "validate_update", None)
    if validate is not None:
        is_ok, message = validate(user.Id, params.CompanyRowId, params.Locale, params.Timezone, params.Data)
        if not is_ok:
            raise HTTPException(status_code=500, detail=message)

    # field validation
    # TODO: fields validation

    # defaults
    if params.CompanyRowId is None:
        params.CompanyRowId = user.Company_Id
    if params.Locale is None:
        params.Locale = user.Settings.Locale
    if params.Timezone is None:
        params.Timezone = user.Settings.Timezone

    # update
    try:
        with db.session.no_autoflush:
            if params.Schema is None:
                populate_record(db.session, record, params.DbTableName, params.CompanyRowId, params.Timezone,
                                params.Data, create=False)
            else:
                populate_record(db.session, record, params.DbTableName, params.CompanyRowId, params.Timezone,
                                params.Data, params.Schema.form_fields, params.Schema.form_panels,
                                create=False)

        db.session.add(record)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        log.error(f"v1.datasource.update_table error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))

    return CUDStatus(success=True, message="OK", RecordRowId=record.Id)


@router.put("/sequentialUpdateTable", response_model=CUDStatus, tags=["datasource"])
def seq_update_table(params: SequentialCUDParams,
                     current_user_id: DBUser = Depends(get_current_user)):

    records = params.Data
    for record in records:
        params.Data = record
        params.RowId = record["Id"]
        update_table(params, current_user_id)

    return CUDStatus(success=True, message="OK", RecordRowId=0)


@router.put("/updateChildTable", response_model=CUDStatus, tags=["datasource"])
def update_child_table(params: CUDChildParams,
                       current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    parent = db.session.query(sqa.get_model(params.ParentTable)).get(params.ParentRowId)
    if parent is None:
        raise HTTPException(status_code=500,
                            detail=f"No {params.ParentTable} Parent Record found for RowId {params.ParentRowId} in Update Mode")

    try:
        model = sqa.get_model(params.DbTableName)()
        is_poly_base = model.is_poly_base()
        poly_on = None
        if is_poly_base:
            poly_on = model.get_poly_base_on_name()
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid DbTableName: {params.DbTableName}")

    # (psycopg2.errors.FeatureNotSupported) FOR UPDATE cannot be applied to the nullable side of an outer join
    # remove with_for_update() - investigate why
    record = db.session.query(sqa.get_model(params.DbTableName)).get(params.RowId)
    if record is None:
        raise HTTPException(status_code=500,
                            detail=f"No {params.DbTableName} Record found for RowId {params.RowId} in Update Mode")

    # table validation
    validate = getattr(record, "validate_update", None)
    if validate is not None:
        is_ok, message = validate(user.Id, params.CompanyRowId, params.Locale, params.Timezone, params.Data)
        if not is_ok:
            raise HTTPException(status_code=500, detail=message)

    # field validation
    # TODO: fields validation

    # defaults
    if params.CompanyRowId is None:
        params.CompanyRowId = user.Company_Id
    if params.Locale is None:
        params.Locale = user.Settings.Locale
    if params.Timezone is None:
        params.Timezone = user.Settings.Timezone

    # update
    try:
        if is_poly_base:
            # delete old record - edited record might have changed record type
            db.session.delete(record)
            db.session.commit()
            # create new record  - might be a different record type
            record = sqa.get_model(params.DbTableName)()
            try:
                record = record.get_poly_base_on_obj(params.Data[poly_on])
            except Exception as err:
                raise Exception(f"Invalid Polymorphic Identity: {params.Data[poly_on]} for {params.DbTableName}")

        with db.session.no_autoflush:
            if params.Schema is None:
                populate_record(db.session, record, params.DbTableName, params.CompanyRowId, params.Timezone,
                                params.Data, create=False)
            else:
                populate_record(db.session, record, params.DbTableName, params.CompanyRowId, params.Timezone,
                                params.Data, params.Schema.form_fields, params.Schema.form_panels,
                                create=False)

        db.session.add(record)

        parent = db.session.query(sqa.get_model(params.ParentTable)).with_for_update().get(params.ParentRowId)
        parent_field = get_attr(parent, params.ParentField)
        if isinstance(parent_field, list):
            parent_field.append(record)
        else:
            parent_field = record

        db.session.commit()
    except Exception as err:
        db.session.rollback()
        log.error(f"v1.datasource.update_child_table error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))

    return CUDStatus(success=True, message="OK", RecordRowId=record.Id)


@router.put("/sequentialUpdateChildTable", response_model=CUDStatus, tags=["datasource"])
def seq_update_child_table(params: SequentialCUDChildParams,
                           current_user_id: DBUser = Depends(get_current_user)):

    records = params.Data
    for record in records:
        params.Data = record
        params.RowId = record["Id"]
        update_child_table(params, current_user_id)

    return CUDStatus(success=True, message="OK", RecordRowId=0)


@router.delete("/deleteTable", response_model=CUDStatus, tags=["datasource"])
def delete_table(params: CUDParams,
                 current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    # validate
    try:
        sqa.get_model(params.DbTableName)()
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid DbTableName: {params.DbTableName}")

    record = db.session.query(sqa.get_model(params.DbTableName)).with_for_update().get(params.RowId)
    if record is None:
        raise HTTPException(status_code=500,
                            detail=f"No {params.DbTableName} Record found for RowId {params.RowId} in Delete Mode")

    # table validation

    validate = getattr(record, "validate_delete", None)
    if validate is not None:
        is_ok, message = validate(user.Id, params.CompanyRowId, params.Locale, params.Timezone, params.Data)
        if not is_ok:
            raise HTTPException(status_code=500, detail=message)

    try:
        db.session.delete(record)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        log.error(f"v1.datasource.delete_table error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))

    return CUDStatus(success=True, message="OK", RecordRowId=record.Id)


@router.delete("/sequentialDeleteTable", response_model=CUDStatus, tags=["datasource"])
def seq_delete_table(params: SequentialCUDParams,
                     current_user_id: DBUser = Depends(get_current_user)):

    records = params.Data
    for record in records:
        params.Data = record
        params.RowId = record["Id"]
        delete_table(params, current_user_id)

    return CUDStatus(success=True, message="OK", RecordRowId=0)


@router.delete("/deleteChildTable", response_model=CUDStatus, tags=["datasource"])
def delete_child_table(params: CUDChildParams,
                       current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    # validate
    try:
        sqa.get_model(params.DbTableName)()
    except Exception as err:
        raise HTTPException(status_code=500,
                            detail=f"Invalid DbTableName: {params.DbTableName}")

    # (psycopg2.errors.FeatureNotSupported) FOR UPDATE cannot be applied to the nullable side of an outer join
    # remove with_for_update() - investigate why
    record = db.session.query(sqa.get_model(params.DbTableName)).get(params.RowId)
    if record is None:
        raise HTTPException(status_code=500,
                            detail=f"No {params.DbTableName} Record found for RowId {params.RowId} in Delete Mode")

    # table validation
    validate = getattr(record, "validate_delete", None)
    if validate is not None:
        is_ok, message = validate(user.Id, params.CompanyRowId, params.Locale, params.Timezone, params.Data)
        if not is_ok:
            raise HTTPException(status_code=500, detail=message)

    try:
        db.session.delete(record)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        log.error(f"v1.datasource.delete_child_table error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))

    return CUDStatus(success=True, message="OK", RecordRowId=record.Id)


@router.delete("/sequentialDeleteChildTable", response_model=CUDStatus, tags=["datasource"])
def seq_delete_child_table(params: SequentialCUDChildParams,
                           current_user_id: DBUser = Depends(get_current_user)):

    records = params.Data
    for record in records:
        params.Data = record
        params.RowId = record["Id"]
        delete_child_table(params, current_user_id, db.session)

    return CUDStatus(success=True, message="OK", RecordRowId=0)


@router.post("/upload", response_model=UploadFileResult, tags=["datasource"])
async def upload_file(file: UploadFile = File(...),
                      current_user_id: DBUser = Depends(get_current_user)):
    HEADER_SIZE = 8192  # 8 KB
    head = await file.read(HEADER_SIZE)
    if not head:
        raise HTTPException(400, "Empty file")
    mime = magic.from_buffer(head, mime=True)

    if "image" in mime.lower():
        max_size = int(config["image"]["file_max_size"])
    else:
        if not mime in config["workfile"]["mime_types"]:
            raise HTTPException(400, "Unsupported File Type")

        max_size = int(config["workfile"]["file_max_size"])

    remaining = await file.read(max_size - len(head) + 1)
    if len(head) + len(remaining) > max_size:
        raise HTTPException(413, "File too large")

    contents = head + remaining

    if "image" in mime.lower():
        try:
            return upload_image_file(contents)
        except Exception as err:
            raise HTTPException(400, str(err))

    # Note that we are generating our own filename instead of trusting
    # the incoming filename since that might result in insecure paths.
    ext = file.filename.rsplit('.', 1)[-1]
    file_name = get_work_filename(config) + '.' + ext
    with open(file_name, "wb+") as buffer:
        buffer.write(contents)

    return UploadFileResult(filenames=[file_name],
                            formats=[mime])


@router.post("/uploads", response_model=UploadFileResult, tags=["datasource"])
async def upload_files(files: List[UploadFile] = File(...),
                       current_user_id: DBUser = Depends(get_current_user)):
    filenames = list()
    formats = list()
    for file in files:
        try:
            result = upload_file(file, current_user_id)
            filenames.append(result.filenames[0])
            formats.append(result.formats[0])
        except Exception as err:
            raise HTTPException(400, str(err))

    return UploadFileResult(filenames=filenames, formats=formats)

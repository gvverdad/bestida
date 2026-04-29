import logging, json

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ......db import sqa
from ......db.models.functions import get_tables_choices
from ......db.models.security.Users import User as DBUser
from ......services import templates
from ......security.policy import get_current_user
from ......schemas.datasource import (CUDParams, CUDStatus, populate_record,
                                       ListGridParams, ListResult, get_table_list)
from ......schemas.model import GridSchema
from ...model.model import get_grid_schema

log = logging.getLogger(__name__)

router = APIRouter()

"""
@router.get("/importtables", response_class=HTMLResponse, tags=["pages"])
def import_tables_page(request: Request,
                       current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    context = dict(request=request,
                   tables=get_tables_choices())

    return templates.TemplateResponse("pages/database/importtables.html", context)
"""

@router.get("/importtablesgridschema", response_model=GridSchema, tags=["pages"])
def get_import_tables_grid_schema(current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    except_fields = list()
    except_fields.append("Company")
    except_fields.append("Program")
    if user.Role.Group.IsAdmin:
        pass  # for clarity
    elif user.Role.IsAdmin:
        pass  # for clarity
    else:
        except_fields.append("Role")
        except_fields.append("User")

    schema = get_grid_schema("Rulesets", 1, current_user_id)

    columns = list()
    for field in schema.grid_fields:
        allow = True
        for except_fld in except_fields:
            if field.name.startswith(except_fld):
                allow = False
                break
        if not allow:
            continue
        columns.append(field)

    return GridSchema.model_validate(dict(
        grid_fields=columns,
        grid_tables=schema.grid_tables
    ))


@router.post("/importtablesrulesets", response_model=ListResult, tags=["pages"])
def get_import_tables_rulesets(params: ListGridParams,
                               current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)
    program = (db.session.query(sqa.get_model("Programs")).
               filter(sqa.where("Program = 'ImportTables' and Type = 'Script'")).first())
    if program is None:
        raise HTTPException(status_code=500,
                            detail=f"Invalid Program: ImportTables/Script")

    if params.Criteria is None:
        params.Criteria = list()

    # only current company
    params.Criteria.append(dict(field="Program_Id", op="0", value=program.Id))
    if user.Role.Group.IsAdmin:
        pass  # for clarity
    elif user.Role.IsAdmin:
        params.Criteria.append(dict(field="Role.Group_Id", op="0", value=user.Role.Group_Id))
    else:
        params.Criteria.append(dict(field="User_Id", op="0", value=current_user_id))

    return get_table_list("Rulesets", params, db.session, current_user_id)


@router.post("/importtables", response_model=CUDStatus, tags=["pages"])
def create_import_tables_task(params: CUDParams,
                              current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)
    program = (db.session.query(sqa.get_model("Programs")).
               filter(sqa.where("Program = 'ImportTables' and Type = 'Script'")).first())
    if program is None:
        raise HTTPException(status_code=500,
                            detail=f"Invalid Program: ImportTables/Script")

    # defaults
    if params.CompanyRowId is None:
        params.CompanyRowId = user.Company_Id
    if params.Locale is None:
        params.Locale = user.Settings.Locale
    if params.Timezone is None:
        params.Timezone = user.Settings.Timezone

    try:
        # Rulesets
        record = sqa.get_model("Rulesets")()
        record.Company_Id = params.CompanyRowId
        record.Program_Id = program.Id
        record.Role_Id = user.Role_Id
        record.User_Id = user.Id
        record.Title = params.Data["Title"]
        record.Params = json.dumps(params.Data["Params"])
        db.session.add(record)

        # Tasks
        params.Data["Company"] = dict(Id=user.Company_Id)
        params.Data["Program"] = dict(Id=program.Id)
        params.Data["Role"] = dict(Id=user.Role_Id)
        params.Data["User"] = dict(Id=user.Id)
        params.Data["RunScript"] = "tasks.system.import.importtables.ImportTables"
        params.Data["Session"] = str(dict(locale=params.Locale, timezone=params.Timezone))

        record = sqa.get_model("Tasks")()
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
        log.error(f"v1.pages.database.import.create_import_tables_task error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))

    return dict(success=True, message="OK", RecordRowId=record.Id)


@router.put("/importtables", response_model=CUDStatus, tags=["pages"])
def update_import_tables_task(params: CUDParams,
                              current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)
    program = (db.session.query(sqa.get_model("Programs")).
               filter(sqa.where("Program = 'ImportTables' and Type = 'Script'")).first())
    if program is None:
        raise HTTPException(status_code=500,
                            detail=f"Invalid Program: ImportTables/Script")

    # defaults
    if params.CompanyRowId is None:
        params.CompanyRowId = user.Company_Id
    if params.Locale is None:
        params.Locale = user.Settings.Locale
    if params.Timezone is None:
        params.Timezone = user.Settings.Timezone

    record = db.session.query(sqa.get_model("Rulesets")).get(params.RowId)
    if record is None:
        raise HTTPException(status_code=500,
                            detail=f"No Rulesets Record found for RowId {params.RowId} in Update Mode")
    try:
        # Rulesets
        record.Title = params.Data["Title"]
        record.Params = json.dumps(params.Data["Params"])
        db.session.add(record)

        # Tasks
        params.Data["Company"] = dict(Id=user.Company_Id)
        params.Data["Program"] = dict(Id=program.Id)
        params.Data["Role"] = dict(Id=user.Role_Id)
        params.Data["User"] = dict(Id=user.Id)
        params.Data["RunScript"] = "tasks.system.import.importtables.ImportTables"
        params.Data["Session"] = str(dict(locale=params.Locale, timezone=params.Timezone))

        record = sqa.get_model("Tasks")()
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
        log.error(f"v1.pages.database.import.update_import_tables_task error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))

    return dict(success=True, message="OK", RecordRowId=record.Id)

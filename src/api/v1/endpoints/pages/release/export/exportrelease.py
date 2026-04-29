import logging, json

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from .......db import sqa
from .......db.models.security.Users import User as DBUser
from .......services import templates
from .......security.policy import get_current_user
from .......schemas.datasource import (CUDParams, CUDStatus, populate_record,
                                       ListGridParams, ListResult, get_table_list)
from .......schemas.model import GridSchema
from ....model.model import get_grid_schema

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/exportreleasetables", response_class=HTMLResponse, tags=["pages"])
def export_release_tables_page(request: Request,
                               current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    context = dict(request=request)

    return templates.TemplateResponse("pages/release/exportrelease.html", context)


@router.get("/exportreleasegridschema", response_model=GridSchema, tags=["pages"])
def get_export_release_tables_grid_schema(current_user_id: DBUser = Depends(get_current_user)):

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

    return GridSchema(grid_fields=columns, grid_tables=schema.grid_tables)


@router.post("/exportreleaserulesets", response_model=ListResult, tags=["pages"])
def get_export_release_tables_rulesets(params: ListGridParams,
                                       current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)
    program = (db.session.query(sqa.get_model("Programs")).
               filter(sqa.where("Program = 'ExportReleaseTables' and Type = 'Script'")).first())
    if program is None:
        raise HTTPException(status_code=500,
                            detail=f"Invalid Program: ExportReleaseTables/Script")

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

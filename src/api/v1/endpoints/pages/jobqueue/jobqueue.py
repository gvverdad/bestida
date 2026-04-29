import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ......db import sqa
from ......db.models.security.Users import User as DBUser
from ......services import templates
from ......security.policy import get_current_user

from ......schemas.model import GridSchema, FormSchema
from ......schemas.datasource import (ListGridParams, ListResult, get_table_list)
from ...model.model import get_grid_schema, get_form_schema

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/jobqueues", response_class=HTMLResponse, tags=["pages"])
def jobqueue_page(request: Request,
                  current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    context = dict(request=request)

    return templates.TemplateResponse("pages/jobqueues.html", context)


@router.get("/jobqueuegridschema", response_model=GridSchema, tags=["pages"])
def get_jobqueue_grid_schema(current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    except_fields = list()
    if user.Role.Group.IsAdmin:
        pass  # for clarity
    elif user.Role.IsAdmin:
        except_fields.append("Role")
    else:
        except_fields.append("Company")
        except_fields.append("Role")
        except_fields.append("User")

    schema = get_grid_schema("Tasks", 1, current_user_id)

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


@router.get("/jobqueueformschema", response_model=FormSchema, tags=["pages"])
def get_jobqueue_form_schema(current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    except_columns = ["Company", "Program", "User", "RunScript", "Role"]
    schema = get_form_schema("Tasks", 1, True, current_user_id)

    columns = list()
    for field in schema.form_fields:
        field.modifiable = True
        if field.name in except_columns:
            field.modifiable = False
        columns.append(field)

    return FormSchema.model_validate(dict(
        form_fields=columns,
        form_panels=schema.form_panels
    ))


@router.post("/jobqueuedata", response_model=ListResult, tags=["pages"])
def get_jobqueue_data(params: ListGridParams,
                      current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    if params.Criteria is None:
        params.Criteria = list()

    if user.Role.Group.IsAdmin:
        pass  # for clarity only
    elif user.Role.IsAdmin:
        params.Criteria.append(dict(field="Role.Group_Id", op="0", value=user.Role.Group_Id))
    else:
        params.Criteria.append(dict(field="User_Id", op="0", value=current_user_id))

    return get_table_list("Tasks", params, db.session, current_user_id)

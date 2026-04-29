import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ......db import sqa
from ......db.models.security.Users import User as DBUser
from ......services import templates
from ......security.policy import get_current_user
from ......schemas.model import GridSchema
from ......schemas.datasource import (ListGridParams, ListResult, get_table_list)
from ...model.model import get_grid_schema

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/bookmarks", response_class=HTMLResponse, tags=["pages"])
def bookmark_page(request: Request,
                  current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    context = dict(request=request)

    return templates.TemplateResponse("pages/bookmarks.html", context)


@router.get("/bookmarkgridschema", response_model=GridSchema, tags=["pages"])
def get_bookmark_grid_schema(current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    except_fields = list()
    if user.Role.Group.IsAdmin:
        pass  # for clarity
    elif user.Role.IsAdmin:
        pass  # for clarity
    else:
        except_fields.append("Company")
        except_fields.append("User")

    schema = get_grid_schema("Bookmarks", 1, current_user_id)

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

@router.post("/bookmarkdata", response_model=ListResult, tags=["pages"])
def get_bookmark_data(params: ListGridParams,
                     current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    if params.Criteria is None:
        params.Criteria = list()

    if user.Role.Group.IsAdmin:
        pass  # for clarity only
    elif user.Role.IsAdmin:
        params.Criteria.append(dict(field="User.Role.Group_Id", op="0", value=user.Role.Group_Id))
    else:
        params.Criteria.append(dict(field="User_Id", op="0", value=current_user_id))

    return get_table_list("Bookmarks", params, db.session, current_user_id)

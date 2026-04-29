import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ......db import sqa
from ......db.models.security.Users import User as DBUser
from ......services import templates
from ......security.policy import get_current_user
from ......schemas.model import GridSchema, FormSchema
from ......schemas.datasource import (ListGridParams, ListResult, get_table_list,
                                      CUDStatus)
from ...model.model import get_grid_schema, get_form_schema

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/notifications", response_class=HTMLResponse, tags=["pages"])
def notifications_page(request: Request,
                       current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    context = dict(request=request)

    return templates.TemplateResponse("pages/notifications.html", context)


@router.get("/notificationgridschema", response_model=GridSchema, tags=["pages"])
def get_notification_grid_schema(current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    except_fields = list()
    except_fields.append("Company")
    if user.Role.Group.IsAdmin:
        pass  # for clarity
    elif user.Role.IsAdmin:
        pass  # for clarity
    else:
        except_fields.append("User")

    schema = get_grid_schema("Notifications", 1, current_user_id)

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


@router.get("/notificationformschema", response_model=FormSchema, tags=["pages"])
def get_notification_form_schema(current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    except_columns = ["SpoolTitle", "SpoolFile"]
    schema = get_form_schema("Notifications", 1, True, current_user_id)

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


@router.post("/notificationdata", response_model=ListResult, tags=["pages"])
def get_notification_data(params: ListGridParams,
                          current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    if params.Criteria is None:
        params.Criteria = list()

    if user.Role.Group.IsAdmin:
        pass  # for clarity
    elif user.Role.IsAdmin:
        params.Criteria.append(dict(field="User.Role.Group_Id", op="0", value=user.Role.Group_Id))
    else:
        params.Criteria.append(dict(field="User_Id", op="0", value=current_user_id))

    return get_table_list("Notifications", params, db.session, current_user_id)


@router.put("/notificationsreadall", response_model=CUDStatus, tags=["pages"])
def flag_my_notifications_as_read(current_user_id: DBUser = Depends(get_current_user)):

    records = (db.session.query(sqa.get_model("Notifications")).
               filter(sqa.where(f"User_Id = {current_user_id} and Read = False")).
               all())
    if records is not None:
        for r in records:
            r.Read = True
            db.session.add(r)
        db.session.commit()

    return dict(success=True, message="OK", RecordRowId=0)

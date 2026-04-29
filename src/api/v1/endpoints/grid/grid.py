import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from .....db import sqa
from .....db.models.security.Users import User as DBUser
from .....cache import cache
from .....config import config
from .....services import templates
from .....security.policy import create_access_token, get_current_user

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/grid/{program}", response_class=HTMLResponse, tags=["pages"])
def grid_page(request: Request,
              program: str,
              current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    prog = db.session.query(sqa.get_model("Programs")).\
        filter(sqa.where(f"Programs.Program = '{program}' and Programs.Type = 'Grid'")).first()

    # multiple is a boolean attribute in ui-datatable and defaults to false
    # in HTML, boolean attributes are dictated by whether they are present or not,
    # not by the string value
    # therefore to allow for multiple selection multiple = "multiple"
    # else multiple = ""
    multiple = ""
    add_button = "add-button"
    copy_button = "copy-button"
    update_button = "update-button"
    delete_button = "delete-button"
    filter_button = "filter-button"
    column_button = "column-button"
    bookmark_button = "bookmark-button"
    refresh_button = "refresh-button"
    auto_refresh_button = "auto-refresh-button"
    download_button = "download-button"
    print_button = "print-button"

    context = dict(request=request,
                   title=prog.Name,
                   program=program,
                   table=prog.Table,
                   multiple=multiple,
                   addbutton=add_button,
                   copybutton=copy_button,
                   updatebutton=update_button,
                   deletebutton=delete_button,
                   filterbutton=filter_button,
                   columnbutton=column_button,
                   bookmarkbutton=bookmark_button,
                   refreshbutton=refresh_button,
                   autorefreshbutton=auto_refresh_button,
                   downloadbutton=download_button,
                   printbutton=print_button)

    return templates.TemplateResponse("datatable/datatable.html", context)

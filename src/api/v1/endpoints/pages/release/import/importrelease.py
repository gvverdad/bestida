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


@router.get("/importreleasetables", response_class=HTMLResponse, tags=["pages"])
def import_release_tables_page(request: Request,
                               current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    context = dict(request=request)

    return templates.TemplateResponse("pages/release/importrelease.html", context)

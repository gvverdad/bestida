import logging

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ......db import sqa
from ......db.models.security.Users import User as DBUser
from ......services import templates
from ......security.policy import get_current_user
from ......schemas.menu import walk_programs
from ......db.models.functions import get_locale_choices


log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/launcher", response_class=HTMLResponse, tags=["pages"])
def launcher_page(request: Request,
                  current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    context = dict(request=request,
                   programs=walk_programs(user.Role.StartMenu, user))

    return templates.TemplateResponse("pages/launcher.html", context)

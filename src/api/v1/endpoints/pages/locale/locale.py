import logging

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ......db import sqa
from ......db.models.security.Users import User as DBUser
from ......services import templates
from ......security.policy import get_current_user
from ......schemas.datasource import CUDStatus
from ......db.models.functions import get_locale_choices


log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/setlocale", response_class=HTMLResponse, tags=["pages"])
def locale_page(request: Request,
                current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    context = dict(request=request,
                   locale=user.Settings.Locale,
                   locales=get_locale_choices())

    return templates.TemplateResponse("pages/setlocale.html", context)


@router.put("/setlocale", response_model=CUDStatus, tags=["pages"])
def update_locale(request: Request,
                  locale: str = Form(),
                  current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)
    user.Settings.Locale = locale

    db.session.add(user)
    db.session.commit()

    return dict(success=True, message="OK")

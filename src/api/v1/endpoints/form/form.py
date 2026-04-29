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


@router.get("/form/{program}", response_class=HTMLResponse, tags=["pages"])
def form_page(request: Request,
              program: str,
              current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    prog = db.session.query(sqa.get_model("Programs")).\
        filter(sqa.where(f"Programs.Program = '{program}' and Programs.Type = 'Form'")).first()

    context = dict(request=request,
                   program=program,
                   title=prog.Name)

    return templates.TemplateResponse("form/form.html", context)

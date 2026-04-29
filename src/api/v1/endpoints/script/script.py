import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from .....db import sqa
from .....db.models.security.Users import User as DBUser
from .....services import templates
from .....security.policy import get_current_user

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/script/{program}", response_class=HTMLResponse, tags=["pages"])
def script_page(request: Request,
                program: str,
                current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    prog = db.session.query(sqa.get_model("Programs")).\
        filter(sqa.where(f"Programs.Program = '{program}' and Programs.Type = 'Script'")).first()

    context = dict(request=request,
                   program=program,
                   title=prog.Name,
                   path=prog.Path,
                   component=prog.Component,
                   template=prog.Template)

    if prog.Template is None or prog.Template == "":
        return templates.TemplateResponse("script/script.html", context)

    return templates.TemplateResponse(prog.Template, context)

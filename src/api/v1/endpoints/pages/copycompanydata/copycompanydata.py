import logging, json

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ......db import sqa
from ......db.models.security.Users import User as DBUser
from ......services import templates
from ......security.policy import get_current_user
from ......schemas.security import get_companies_list

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/copycompanydata", response_class=HTMLResponse, tags=["pages"])
def copy_company_page(request: Request,
                      current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    context = dict(request=request,
                   company=user.Company_Id,
                   companies=get_companies_list(user))

    return templates.TemplateResponse("pages/copycompanydata.html", context)

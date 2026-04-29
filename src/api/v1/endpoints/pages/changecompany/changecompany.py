import logging

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ......db import sqa
from ......db.models.security.Users import User as DBUser
from ......services import templates
from ......security.policy import get_current_user
from ......schemas.datasource import CUDStatus
from ......schemas.security import get_companies_list

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/changecompany", response_class=HTMLResponse, tags=["pages"])
def change_company_page(request: Request,
                        current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    context = dict(request=request,
                   company=user.Company_Id,
                   companies=get_companies_list(user))

    return templates.TemplateResponse("pages/changecompany.html", context)


@router.put("/changecompany", response_model=CUDStatus, tags=["pages"])
def update_change_company(request: Request,
                          company: str = Form(),
                          current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)
    user.Company_Id = company

    db.session.add(user)
    db.session.commit()

    return dict(success=True, message="OK")

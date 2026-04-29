import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ......db import sqa
from ......db.models.security.Users import User as DBUser
from ......services import templates
from ......security.policy import get_current_user

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/profile", response_class=HTMLResponse, tags=["pages"])
def profile_page(request: Request,
                 current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)
    personal = user.Personal.data_to_dict(depth=1,
                                          except_fields=["Password", "versions",
                                                         "CreateOpId_Id", "CreateOpId",
                                                         "ModifiedOpId_Id", "ModifiedOpId",
                                                         "CreateTimeStamp", "ModifiedTimeStamp",
                                                         "ItemUser", "ItemUser_Id",
                                                         "ItemPerson", "TypeOfAddress",
                                                         "TypeOfPhone", "TypeOfEmail",
                                                         "TypeOfPerson", "Title_Id",
                                                         "Gender_Id", "Type_Id",
                                                         "Locality_Id", "State_Id",
                                                         "Postcode_Id"
                                                         ],
                                          m2m_merge=True)
    context = dict(request=request,
                   rowid=user.Personal.Id,
                   personal=personal)

    return templates.TemplateResponse("pages/profile/profile.html", context)

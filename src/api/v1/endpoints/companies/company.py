import logging

from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from .....db import sqa
from .....db.models.security.Users import User as DBUser
from .....security.policy import get_current_user
from .....schemas.datasource import (ListGridParams, ListResult, get_table_list)
from .....schemas.security import get_companies_list


log = logging.getLogger(__name__)

router = APIRouter()


@router.post("/companiesdata", response_model=ListResult, tags=["companies"])
def get_companies_data(params: ListGridParams,
                       current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    if params.Criteria is None:
        params.Criteria = list()

    recs = []
    if user.Role.Group.IsAdmin:
        companies = db.session.query(sqa.get_model("Companies")).all()
        for coy in companies:
            recs.append(coy.Id)
    else:
        companies = get_companies_list(user)
        for coy in companies:
            recs.append(coy[0])

    # op=14 IN LIST
    params.Criteria.append(dict(field="Id", op="14", value=recs))

    return get_table_list("Companies", params, db.session, current_user_id)

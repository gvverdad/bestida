import logging

from fastapi import HTTPException, Cookie
from fastapi_sqlalchemy import db  # an object to provide global access to a database session
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from ..config import config
from ..db import sqa
from ..middleware import get_current_request
from ..utils.crypt import CryptText

log = logging.getLogger(__name__)


def create_access_token(data: dict):
    to_encode = data.copy()

    return CryptText(to_encode["id"]).encrypt()


def get_current_user(token: str = Cookie(default=None)):
    # "token" is the key name defined in set_cookie
    try:
        user_id = CryptText(token).decrypt()
    except:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    user = db.session.query(sqa.get_model("Users")). \
        filter(sqa.where("Users.Id=={}".format(user_id))).first()

    if user is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid User"
        )
    return user.Id


def get_current_uid():
    try:
        # https://www.starlette.io/requests/ for details
        request = get_current_request()
        # "token" is the key name defined in set_cookie
        token = request.cookies.get('token')
        user_id = CryptText(token).decrypt()
    except:
        user_id = 1

    return user_id


def get_request_client():
    try:
        # https://www.starlette.io/requests/ for details
        request = get_current_request()
        return f"{request.client.host}:{request.client.port}"
    except:
        return None

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


@router.get("/home", response_class=HTMLResponse, tags=["pages"])
def home_page(request: Request,
              current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    bookmarks = (db.session.query(sqa.get_model("Bookmarks")).
                 filter(sqa.where(f"Bookmarks.Company_Id = {user.Company_Id} and Bookmarks.User_Id = {user.Id} "
                                  f"and Bookmarks.HomePage = True")).
                 order_by(sqa.sort_asc("Bookmarks", "HomePageSequence")).
                 all())

    home_bookmarks = []
    active_page = 0
    for idx, book in enumerate(bookmarks):
        if book.URL == user.Settings.HomeActivePage:
            active_page = idx

        home_bookmarks.append(dict(url=book.URL, title=book.Desc,
                                   program=book.Program.Program,
                                   type=book.Program.Type))

    context = dict(request=request,
                   activepage=active_page,
                   bookmarks=home_bookmarks
                   )

    return templates.TemplateResponse("pages/home.html", context)

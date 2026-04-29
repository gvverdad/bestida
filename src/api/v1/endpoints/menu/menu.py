import logging
from typing import List

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from .....db import sqa
from .....db.models.security.Users import User as DBUser
from .....schemas.menu import MainMenu, BookmarkMenu, walk_menu, walk_bookmarks
from .....schemas.security import get_program_state
from .....security.policy import get_current_user
from .....utils.misc import get_timestamp

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/mainMenu", response_model=List[MainMenu], tags=["menu"])
def get_main_menu(request: Request,
                  current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    return walk_menu(user.Role.StartMenu, user, user.Role.StartMenu_Id)


@router.get("/bookmarksMenu", response_model=List[BookmarkMenu], tags=["menu"])
def get_bookmark_menu(request: Request,
                      current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    return walk_bookmarks(db.session, user)


@router.post("/addToBookmarks", response_model=List[BookmarkMenu], tags=["menu"])
def add_to_bookmarks(request: Request,
                     title: str = Form(...),
                     home_page: bool = Form(...),
                     home_page_seq: int = Form(...),
                     page_type: str = Form(...),
                     program: str = Form(...),
                     company_id: int = Form(...),
                     current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)
    company = db.session.query(sqa.get_model("Companies")).get(company_id)

    prog = db.session.query(sqa.get_model("Programs")).\
        filter(sqa.where(f"Programs.Program = '{program}' and Programs.Type = '{page_type}'")).first()
    if prog is None:
        prog = db.session.query(sqa.get_model("Programs")). \
            filter(sqa.where(f"Programs.Program = '{program}'")).first()
        if prog is None:
            raise HTTPException(status_code=500,
                                detail=f"Invalid Program: {program} Type: {page_type}")

    new_prog_id = "Bookmark" + str(get_timestamp())
    # program
    new_prog = sqa.get_model("Programs")()
    new_prog.Program = new_prog_id
    new_prog.Name = title
    new_prog.Type = prog.Type
    if prog.Override:
        new_prog.URL = prog.URL
        new_prog.Override = prog.Override
    else:
        new_prog.Override = False

    new_prog.Table = prog.Table
    new_prog.Path = prog.Path
    new_prog.Component = prog.Component

    new_prog.GridDepth = prog.GridDepth
    new_prog.FormDepth = prog.FormDepth
    new_prog.GridSchema = prog.GridSchema
    new_prog.FormSchema = prog.FormSchema
    new_prog.RunLevel = prog.RunLevel
    new_prog.CreateLevel = prog.CreateLevel
    new_prog.UpdateLevel = prog.UpdateLevel
    new_prog.DeleteLevel = prog.DeleteLevel
    db.session.add(new_prog)

    # program state
    state = get_program_state(db.session, company, user, prog)
    if state is not None:
        new_state = sqa.get_model("ProgramStates")()
        new_state.Company = state.Company
        new_state.Program = new_prog
        new_state.Param1 = state.Param1
        new_state.Param2 = state.Param2
        new_state.Param3 = state.Param3
        new_state.Param4 = state.Param4
        new_state.Param5 = state.Param5
        new_state.Role = user.Role
        new_state.User = user
        new_state.Depth = state.Depth
        new_state.CurrentPage = 1
        new_state.PageSize = state.PageSize
        new_state.AutoRefresh = False
        new_state.RefreshInterval = state.RefreshInterval
        new_state.State = state.State
        db.session.add(new_state)

    # bookmark
    bookmark = sqa.get_model("Bookmarks")()
    bookmark.Company = company
    bookmark.User = user
    bookmark.Program = new_prog
    bookmark.URL = new_prog.URL
    bookmark.Desc = title
    bookmark.HomePage = home_page
    bookmark.HomePageSequence = home_page_seq
    db.session.add(bookmark)

    # copy all subPrograms
    progs = (db.session.query(sqa.get_model("Programs")).
             filter(sqa.where(f"Programs.Id != {prog.Id} and Programs.Program startswith ('{prog.Program}.')"))
             .all())
    if progs is not None:
        for p in progs:
            # bad table names design - Programs startwith above
            if prog.Program == "Programs" and p.Program == "ProgramStates":
                continue

            new_prog = sqa.get_model("Programs")()
            new_prog.Program = p.Program.replace(prog.Program,new_prog_id)
            new_prog.Name = p.Name
            new_prog.Type = p.Type
            new_prog.URL = p.URL.replace(prog.Program,new_prog_id)
            new_prog.Override = p.Override
            new_prog.Table = p.Table
            new_prog.Path = p.Path
            new_prog.Component = p.Component
            new_prog.GridDepth = p.GridDepth
            new_prog.FormDepth = p.FormDepth
            new_prog.GridSchema = p.GridSchema
            new_prog.FormSchema = p.FormSchema
            new_prog.RunLevel = p.RunLevel
            new_prog.CreateLevel = p.CreateLevel
            new_prog.UpdateLevel = p.UpdateLevel
            new_prog.DeleteLevel = p.DeleteLevel
            db.session.add(new_prog)

            state = get_program_state(db.session, company, user, p)
            if state is not None:
                new_state = sqa.get_model("ProgramStates")()
                new_state.Company = state.Company
                new_state.Program = new_prog
                new_state.Param1 = state.Param1
                new_state.Param2 = state.Param2
                new_state.Param3 = state.Param3
                new_state.Param4 = state.Param4
                new_state.Param5 = state.Param5
                new_state.Role = user.Role
                new_state.User = user
                new_state.Depth = state.Depth
                new_state.CurrentPage = 1
                new_state.PageSize = state.PageSize
                new_state.AutoRefresh = False
                new_state.RefreshInterval = state.RefreshInterval
                new_state.State = state.State
                db.session.add(new_state)

    db.session.commit()

    return get_bookmark_menu(request, current_user_id)

import logging, ast, json
from datetime import datetime, timedelta, timezone
from ast import literal_eval

from fastapi import APIRouter, Request, Depends, status, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from .....db import sqa
from .....db.models.security.Users import User as DBUser
from .....db.models.system.Programs import PROGRAM_SYS_MENU
from .....db.models.functions import get_theme_choices
from .....config import config
from .....services import templates
from .....security.policy import create_access_token, get_current_user
from .....schemas.menu import walk_menu, walk_bookmarks
from .....schemas.datasource import (CUDStatus, FormResult, EnumResult,
                                     ListGridParams, ListResult, get_table_list, ListCriteriaType)
from .....schemas.security import get_program_state as schemas_get_program_state
from .....schemas.security import (get_gravatar, ProgramStateParams,
                                   UpdateProgramStateParams, get_companies_list)
from .....utils.misc import copy_nested_fields

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_class=HTMLResponse, tags=["security"])
def index_page(request: Request):
    message = request.query_params.get("message")
    context = dict(request=request,
                   message=message)
    return templates.TemplateResponse("security/login.html", context)


@router.get("/logout", tags=["security"])
def log_out(request: Request):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie("token")

    return response


@router.get("/notfound", tags=["security"])
def not_found(request: Request):
    response = RedirectResponse('/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie("token")

    return response


@router.post("/login", tags=["security"])
async def get_access_token(request: Request):
    form_data = await request.form()

    username = form_data.get("username")
    password = form_data.get("password")

    user = db.session.query(sqa.get_model("Users")).\
        filter(sqa.where("Users.UserId=='{}'".format(username))).first()

    if not user or user.Password != password:
        raise HTTPException(status_code=400,
                            detail="Invalid Username or Password")
    elif user.Inactive:
        raise HTTPException(status_code=400, detail="Inactive User")
    elif user.ExpiryDate <= datetime.utcnow().date():
        raise HTTPException(status_code=400, detail="Expired User")

    token = create_access_token(data=dict(id=user.Id))
    utc_now = datetime.now(timezone.utc)
    try:
        expire = utc_now + timedelta(minutes=int(config["token"]["expire_minutes"]))
    except:
        expire = utc_now + timedelta(minutes=15)

    response = RedirectResponse('/main', status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="token", value=token, httponly=True, expires=expire)

    return response


@router.get("/current_user", response_model=FormResult, tags=["security"])
def get_current_user_data(request: Request,
                          current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    result = dict()
    result["data"] = user.data_to_dict(depth=1,
                                       except_fields=["Password", "versions",
                                                      "CreateOpId_Id", "CreateOpId",
                                                      "ModifiedOpId_Id", "ModifiedOpId",
                                                      "CreateTimeStamp", "ModifiedTimeStamp",
                                                      "Spoolers", "Tasks", "Users", "Roles",
                                                      "Groups", "SidebarState", "MenuState",
                                                      "NavState", "OtherStates",
                                                      "ItemUser", "ItemUser_Id",
                                                      "ItemPerson", "ItemPerson_Id"
                                                      ],
                                       m2m_merge=True)
    result["data"]["Personal"]["GravatarId"] = get_gravatar(result["data"]["Personal"]["GravatarId"])

    return result


@router.get("/main", response_class=HTMLResponse, tags=["security"])
def main_page(request: Request,
              current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)
    main_menu = walk_menu(user.Role.StartMenu, user, user.Role.StartMenu_Id)
    bookmark_menu = walk_bookmarks(db.session, user)

    notifs = (db.session.query(sqa.get_model("Notifications")).
              filter(sqa.where(f"User_Id = {current_user_id} and Read = False")).
              all())
    total_notifications = None
    if len(notifs) > 99:
        total_notifications = "99+"
    else:
        total_notifications = str(len(notifs))

    themes = dict(config.items("themes"))
    theme = themes[user.Settings.Theme]

    val = user.Settings.MenuState
    try:
        menu_state = json.loads(val)  # convert to dict if ever
    except:
        try:
            menu_state = ast.literal_eval(val)  # convert to dict if ever
        except:
            menu_state = val

    val = user.Settings.NavState
    try:
        nav_state = json.loads(val)  # convert to dict if ever
    except:
        try:
            nav_state = ast.literal_eval(val)  # convert to dict if ever
        except:
            nav_state = val
    if not nav_state:
        nav_state = list()
        nav_state.append(dict(path="/home", title="Home"))
    else:
        nav = list()
        # make sure breadcrumb is a valid Program
        for state in nav_state:
            url = state["path"]
            if url == "/home":
                nav.append(state)
                continue
            prog = (db.session.query(sqa.get_model("Programs")).
                    filter(sqa.where(f"URL = '{url}'")).first())
            if prog is not None:
                nav.append(state)
            elif url in PROGRAM_SYS_MENU:
                nav.append(state)
        nav_state = nav

    change_password = False
    active_page = user.Settings.ActivePage
    if user.password_expiry_date < datetime.utcnow():
        change_password = True
        nav_state = list()
        nav_state.append(dict(path="/home", title="Home"))
        nav_state.append(dict(path="/changepassword", title="Change Password"))
        active_page = "/changepassword"

    context = dict(request=request,
                   theme=theme,
                   main_menu=main_menu,
                   menu_state=menu_state,
                   bookmark_menu=bookmark_menu,
                   nav_state=nav_state,
                   change_password=change_password,
                   active_page=active_page,
                   notifications=total_notifications)
    return templates.TemplateResponse("layout/main.html", context)


@router.get("/themes", response_model=EnumResult, tags=["security"])
def get_themes(request: Request,
               current_user_id: DBUser = Depends(get_current_user)):
    data = get_theme_choices()
    result = dict(recordsTotal=len(data), data=data)
    return result


@router.post("/changeTheme", response_model=CUDStatus, tags=["security"])
def change_theme(theme: str = Form(),
                 current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)
    user.Settings.Theme = theme

    db.session.add(user)
    db.session.commit()

    return dict(success=True, message="OK")


@router.post("/updateMenuState", response_model=CUDStatus, tags=["security"])
def update_menu_state(menu_state: str = Form(),
                      current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    user.Settings.MenuState = menu_state

    db.session.add(user)
    db.session.commit()

    return dict(success=True, message="OK")


@router.post("/updateNavState", response_model=CUDStatus, tags=["security"])
def update_nav_state(history_state: str = Form(),
                     current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    user.Settings.NavState = history_state

    db.session.add(user)
    db.session.commit()

    return dict(success=True, message="OK")


@router.post("/updateActivePage", response_model=CUDStatus, tags=["security"])
def update_nav_state(active_page: str = Form(),
                     current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    user.Settings.ActivePage = active_page

    db.session.add(user)
    db.session.commit()

    return dict(success=True, message="OK")


@router.post("/updateHomeActivePage", response_model=CUDStatus, tags=["security"])
def update_nav_state(active_page: str = Form(),
                     current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    user.Settings.HomeActivePage = active_page

    db.session.add(user)
    db.session.commit()

    return dict(success=True, message="OK")


@router.post("/updateProgramState", tags=["security"])
def update_program_state(params: UpdateProgramStateParams,
                         current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    program = (db.session.query(sqa.get_model("Programs"))
               .filter(sqa.where(f"Programs.Program = '{params.Program}' and Programs.Type = '{params.ProgramType}'"))
               .first())
    if program is None:
        raise HTTPException(status_code=500, detail=f"Invalid Program: {params.Program} Type: {params.ProgramType}")

    company_id = params.CompanyRowId
    if company_id is None:
        company_id = user.Company_Id
    coy = db.session.query(sqa.get_model("Companies")).get(company_id)
    if coy is None:
        raise HTTPException(status_code=500, detail="Invalid Company Id {:d}".format(company_id))

    where = (f"ProgramStates.Company_Id = {company_id} and "
             f"ProgramStates.Program_Id = {program.Id}")
    if params.Param1 is not None and params.Param1.strip():
        where += f" and ProgramStates.Param1 = '{params.Param1}'"
    else:
        where += " and ProgramStates.Param1 = None"
    if params.Param2 is not None and params.Param2.strip():
        where += f" and ProgramStates.Param2 = '{params.Param2}'"
    else:
        where += " and ProgramStates.Param2 = None"
    if params.Param3 is not None and params.Param3.strip():
        where += f" and ProgramStates.Param3 = '{params.Param3}'"
    else:
        where += " and ProgramStates.Param3 = None"
    if params.Param4 is not None and params.Param4.strip():
        where += f" and ProgramStates.Param4 = '{params.Param4}'"
    else:
        where += " and ProgramStates.Param4 = None"
    if params.Param5 is not None and params.Param5.strip():
        where += f" and ProgramStates.Param5 = '{params.Param5}'"
    else:
        where += " and ProgramStates.Param5 = None"

    where += (f"ProgramStates.Role_Id = {user.Role_Id} and "
              f"ProgramStates.User_Id = {user.Id}")

    state = db.session.query(sqa.get_model("ProgramStates")).\
        filter(sqa.where(where)).first()

    if state is None:
        state = sqa.get_model("ProgramStates")()
        state.Company = user.Company
        state.Program = program
        state.Param1 = params.Param1 if params.Param1 is not None and params.Param1.strip() else None
        state.Param2 = params.Param2 if params.Param2 is not None and params.Param2.strip() else None
        state.Param3 = params.Param3 if params.Param3 is not None and params.Param3.strip() else None
        state.Param4 = params.Param4 if params.Param4 is not None and params.Param4.strip() else None
        state.Param5 = params.Param5 if params.Param5 is not None and params.Param5.strip() else None
        state.Role = user.Role
        state.User = user

    state.Depth = params.Level
    state.CurrentPage = params.CurrentPage
    state.PageSize = params.PageSize
    state.AutoRefresh = params.AutoRefresh
    state.RefreshInterval = params.RefreshInterval

    state.State = str(params.State)  # save dict to string

    db.session.add(state)
    db.session.commit()


@router.post("/getProgramState", response_model=UpdateProgramStateParams, tags=["security"])
def get_program_state(params: ProgramStateParams,
                      current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    program = (db.session.query(sqa.get_model("Programs"))
               .filter(sqa.where(f"Programs.Program = '{params.Program}' and Programs.Type = '{params.ProgramType}'"))
               .first())
    if program is None:
        #raise HTTPException(status_code=500, detail="Invalid Program: {} Type: {}".format(params.Program,
        #                                                                                  params.ProgramType))
        result = dict(CompanyRowId=None,
                      Program=params.Program,
                      ProgramType=params.ProgramType,
                      Param1=None,
                      Param2=None,
                      Param3=None,
                      Param4=None,
                      Param5=None,
                      Level=1,
                      CurrentPage=0,
                      PageSize=10,
                      AutoRefresh=False,
                      RefreshInterval=60,
                      State=dict())
        return result

    company = params.CompanyRowId
    if company is None:
        company = user.Company_Id
    coy = db.session.query(sqa.get_model("Companies")).get(company)
    if coy is None:
        raise HTTPException(status_code=500, detail="Invalid Company {}".format(company))

    state = schemas_get_program_state(db.session, coy, user, program,
                                      params.Param1, params.Param2,
                                      params.Param3, params.Param4, params.Param5)

    result = dict(CompanyRowId=company,
                  Program=program.Program,
                  ProgramType=program.Type,
                  Param1=params.Param1,
                  Param2=params.Param2,
                  Param3=params.Param3,
                  Param4=params.Param4,
                  Param5=params.Param5,
                  Level=1,
                  CurrentPage=0,
                  PageSize=10,
                  AutoRefresh=False,
                  RefreshInterval=60,
                  State=dict())

    if state:
        result["Level"] = state.Depth
        result["CurrentPage"] = state.CurrentPage
        result["PageSize"] = state.PageSize
        result["AutoRefresh"] = state.AutoRefresh
        result["RefreshInterval"] = state.RefreshInterval
        result["State"] = literal_eval(state.State)  # convert string to dict

    return result


@router.get("/mynotifications", response_model=ListResult, tags=["security"])
def get_my_notifications(request: Request,
                         current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    params = ListGridParams
    params.Depth = 1
    params.CompanyRowId = user.Company_Id
    params.Locale = user.Settings.Locale
    params.Timezone = user.Settings.Timezone
    params.FieldList = ["Id", "Title", "Text", "Read", "CreateTimeStamp", "SpoolTitle", "SpoolFile"]
    params.Criteria = [
        dict(field="User_Id", op=0, value=current_user_id),  # op=0 EQUAL
        dict(field="Read", op=0, value=False)     # op=0 EQUAL
    ]
    params.CriteriaType = ListCriteriaType.ALL
    # sort by CreateTimeStamp descending
    params.Columns = [
        dict(name="CreateTimeStamp", table="Notifications", sortable=True,
             options=dict(sort=True, display=True, sortDirection="desc"))
    ]
    params.Offset = 0
    params.PageSize = 9999
    params.ChoicesAsTuple = False
    params.ChoicesKey = True
    params.TextAsString = True
    params.Draw = 1
    params.SelectedRows = None

    return get_table_list("Notifications", params, db.session, current_user_id)


@router.get("/getCompaniesChoices", response_model=EnumResult, tags=["security"])
def get_valid_companies_choices(current_user_id: DBUser = Depends(get_current_user)):
    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    companies = get_companies_list(user)

    return EnumResult(
        draw=1,
        recordsTotal=len(companies),
        data=companies
    )

@router.post("/getCompaniesList", response_model=ListResult, tags=["security"])
def get_valid_companies_list(params: ListGridParams,
                             current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    companies = get_companies_list(user)

    recs = []
    for coy in companies:
        recs.append(db.session.query(sqa.get_model("Companies")).get(coy[0]))

    field_data = [r.data_to_dict(except_fields=["Password", "versions"],
                               depth=params.Depth,
                               audit=False,
                               table_class=None,
                               tuple_choice=params.ChoicesAsTuple,
                               choice_key=params.ChoicesKey,
                               text_as_string=params.TextAsString,
                               m2m_merge=False,
                               one2m_list=True,
                               ignore_calc_fields=False,
                               dump=False
                               )
                 for r in recs]

    field_list = list()
    if params.FieldList:
        for v in params.FieldList:
            if v not in field_list:
                field_list.append(v)

    if field_list:
        data = list()
        for r in field_data:
            data.append(copy_nested_fields(r, field_list))
    else:
        data = field_data

    return ListResult(
        draw=params.Draw,
        recordsTotal=len(recs),
        selectedRows=params.SelectedRows,
        data=data
    )


@router.post("/getAllCompaniesList", response_model=ListResult, tags=["security"])
def get_all_companies_list(params: ListGridParams,
                           current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    if user.Role.Group.IsAdmin:
        recs = db.session.query(sqa.get_model("Companies")).all()
    else:
        return get_valid_companies_list(params, current_user_id)

    field_data = [r.data_to_dict(except_fields=["Password", "versions"],
                               depth=params.Depth,
                               audit=False,
                               table_class=None,
                               tuple_choice=params.ChoicesAsTuple,
                               choice_key=params.ChoicesKey,
                               text_as_string=params.TextAsString,
                               m2m_merge=False,
                               one2m_list=True,
                               ignore_calc_fields=False,
                               dump=False
                               )
                 for r in recs]

    field_list = list()
    if params.FieldList:
        for v in params.FieldList:
            if v not in field_list:
                field_list.append(v)

    if field_list:
        data = list()
        for r in field_data:
            data.append(copy_nested_fields(r, field_list))
    else:
        data = field_data

    return ListResult(
        draw=params.Draw,
        recordsTotal=len(recs),
        selectedRows=params.SelectedRows,
        data=data
    )

@router.post("/usersdata", response_model=ListResult, tags=["security"])
def get_users_data(params: ListGridParams,
                   current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    if params.Criteria is None:
        params.Criteria = list()

    if user.Role.Group.IsAdmin:
        pass
    elif user.Role.IsAdmin:
        # op=0  EQUALS
        params.Criteria.append(dict(field="Role.Group_Id", op="0", value=user.Role.Group_Id))
    else:
        # op=0  EQUALS
        params.Criteria.append(dict(field="Id", op="0", value=user.Id))

    return get_table_list("Users", params, db.session, current_user_id)

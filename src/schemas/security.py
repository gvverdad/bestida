import urllib, hashlib
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import sqa
from ..db.models.security.Users import User as DBUser
from ..db.models.company.Companies import Company as DBCompany
from ..db.models.system.Programs import Program as DBProgram


class UserData(BaseModel):
    Name: str
    Email: str
    Gravatar: str
    CompanyName: str
    GroupRole: str


class ValidationStatus(BaseModel):
    Valid: bool = False


class OtherStatesParams(BaseModel):
    State: Dict[str, Any]


class ProgramStateParams(BaseModel):
    CompanyRowId: Optional[int] = None
    Program: str
    ProgramType: str
    Param1: Optional[str] = None
    Param2: Optional[str] = None
    Param3: Optional[str] = None
    Param4: Optional[str] = None
    Param5: Optional[str] = None


class UpdateProgramStateParams(ProgramStateParams):
    Level: int = 1
    CurrentPage: int
    PageSize: int
    AutoRefresh: bool
    RefreshInterval: int
    State: Dict[str, Any]


class LogType(str, Enum):
    Debug = "DEBUG"
    Info = "INFO"
    Warn = "WARN"
    Error = "ERROR"


class ClientLoggerParams(BaseModel):
    CompanyRowId: Optional[int] = None
    Locale: Optional[str] = None
    Timezone: Optional[str] = None
    Timestamp: str
    UserAgent: str
    Type: LogType = LogType.Info
    Message: str


def get_gravatar(email: str) -> str:
    default = "mp"
    size = 100

    # construct the url
    gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(str(email).lower().encode("utf-8")).hexdigest() + "?"
    gravatar_url += urllib.parse.urlencode({'d': default, 's': str(size)})

    return gravatar_url


def get_program_state(db_session: Session,
                      company: DBCompany,
                      user: DBUser,
                      program: DBProgram,
                      param1: str = None,
                      param2: str = None,
                      param3: str = None,
                      param4: str = None,
                      param5: str = None
                      ):

    main_key = (f"ProgramStates.Company_Id = {company.Id} and " 
                f"ProgramStates.Program_Id = {program.Id}")
    if param1 is not None and param1.strip():
        main_key += f" and ProgramStates.Param1 = '{param1}'"
    else:
        main_key += " and ProgramStates.Param1 = None"
    if param2 is not None and param2.strip():
        main_key += f" and ProgramStates.Param2 = '{param2}'"
    else:
        main_key += " and ProgramStates.Param2 = None"
    if param3 is not None and param3.strip():
        main_key += " and ProgramStates.Param3 = '{param3}'"
    else:
        main_key += " and ProgramStates.Param3 = None"
    if param4 is not None and param4.strip():
        main_key += " and ProgramStates.Param4 = '{param4}'"
    else:
        main_key += " and ProgramStates.Param4 = None"
    if param5 is not None and param5.strip():
        main_key += " and ProgramStates.Param5 = '{param5}'"
    else:
        main_key += " and ProgramStates.Param5 = None"

    # User
    user_key = (f"{main_key} and "
                f"ProgramStates.Role_Id = {user.Role_Id} and "
                f"ProgramStates.User_Id = {user.Id}")
    state = (db_session.query(sqa.get_model("ProgramStates")).
             filter(sqa.where(user_key)).first())
    # Role
    if state is None:
        role_key = (f"{main_key} and "
                    f"ProgramStates.Role_Id = {user.Role_Id}")
        state = (db_session.query(sqa.get_model("ProgramStates")).
                 filter(sqa.where(role_key)).first())
    # Company
    if state is None:
        state = (db_session.query(sqa.get_model("ProgramStates")).
                 filter(sqa.where(main_key)).first())
    # Setup Companies
    if state is None:
        setup_group = (db_session.query(sqa.get_model("Groups")).
                       filter(sqa.where("IsAdmin = true")).first())
        if setup_group is not None:
            for coy in setup_group.Companies:
                coy_key = (f"ProgramStates.Company_Id = {coy.Id} and "
                           f"ProgramStates.Program_Id = {program.Id}")
                if param1 is not None and param1.strip():
                    coy_key += f" and ProgramStates.Param1 = '{param1}'"
                else:
                    coy_key += " and ProgramStates.Param1 = None"
                if param2 is not None and param2.strip():
                    coy_key += f" and ProgramStates.Param2 = '{param2}'"
                else:
                    coy_key += " and ProgramStates.Param2 = None"
                if param3 is not None and param3.strip():
                    coy_key += f" and ProgramStates.Param3 = '{param3}'"
                else:
                    coy_key += " and ProgramStates.Param3 = None"
                if param4 is not None and param4.strip():
                    coy_key += f" and ProgramStates.Param4 = '{param4}'"
                else:
                    coy_key += " and ProgramStates.Param4 = None"
                if param5 is not None and param5.strip():
                    coy_key += f" and ProgramStates.Param5 = '{param5}'"
                else:
                    coy_key += " and ProgramStates.Param5 = None"

                state = (db_session.query(sqa.get_model("ProgramStates")).
                         filter(sqa.where(coy_key)).first())
                if state is not None:
                    break

    return state


def get_companies_list(user: DBUser) -> List:
    company_list = []
    for coy in user.Role.Group.Companies:
        company_list.append((coy.Id, coy.Name))
    return company_list


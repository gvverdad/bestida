import logging
from fastapi import APIRouter, Depends, Request
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from .....db import sqa
from .....db.models.security.Users import User as DBUser
from .....security.policy import get_current_user
from .....schemas.datasource import EnumResult
from .....db.models.functions import (get_timezone_choices, get_locale_choices,
                                      get_country_choices, get_currency_choices,
                                      get_queue_choices)
from .....schemas.datasource import FormResult

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/getLocaleList", response_model=EnumResult, tags=["system"])
def get_locale_list(request: Request,
                    current_user_id: DBUser = Depends(get_current_user)):
    locales = get_locale_choices()

    results = dict()
    results["draw"] = 1
    results["recordsTotal"] = len(locales)
    results["data"] = locales

    return results


@router.get("/getTimezoneList", response_model=EnumResult, tags=["system"])
def get_timezone_list(request: Request,
                      current_user_id: DBUser = Depends(get_current_user)):
    timezones = get_timezone_choices()

    results = dict()
    results["draw"] = 1
    results["recordsTotal"] = len(timezones)
    results["data"] = timezones

    return results


@router.get("/getCurrencyList", response_model=EnumResult, tags=["system"])
def get_currency_list(request: Request,
                      current_user_id: DBUser = Depends(get_current_user)):
    currencies = get_currency_choices()

    results = dict()
    results["draw"] = 1
    results["recordsTotal"] = len(currencies)
    results["data"] = currencies

    return results


@router.get("/getCountriesList", response_model=EnumResult, tags=["system"])
def get_countries_list(request: Request,
                       current_user_id: DBUser = Depends(get_current_user)):
    countries = get_country_choices()

    results = dict()
    results["draw"] = 1
    results["recordsTotal"] = len(countries)
    results["data"] = countries

    return results


@router.get("/getQueuesList", response_model=EnumResult, tags=["system"])
def get_queues_list(request: Request,
                    current_user_id: DBUser = Depends(get_current_user)):
    queues = get_queue_choices()

    results = dict()
    results["draw"] = 1
    results["recordsTotal"] = len(queues)
    results["data"] = queues

    return results


@router.get("/getProgram/{program}/{program_type}/{level}",
            response_model=FormResult, tags=["system"])
def get_program(request: Request,
                program,
                program_type,
                level: int = 1,
                current_user_id: DBUser = Depends(get_current_user)):

    except_fields = ["CreateOpId", "ModifiedOpId", "Menus", "Bookmarks", "ProgramStates", "Rulesets", "versions"]

    record = db.session.query(sqa.get_model("Programs")).\
        filter(sqa.where("Programs.Program = '{}' and Programs.Type = '{}'".format(program, program_type))).first()

    result = dict()
    if record:
        result["data"] = record.data_to_dict(except_fields=except_fields,
                                             depth=level,
                                             tuple_choice=False,
                                             choice_key=True,
                                             m2m_merge=True)
    else:
        result["data"] = dict()

    return result

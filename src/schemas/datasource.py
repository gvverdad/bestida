import pytz, logging, json, string, datetime, ast, io
from enum import Enum, IntEnum
import dateutil.parser
from typing import List, Dict, Optional, Any, Tuple
from PIL import Image

from sqlalchemy import func, asc, desc
from sqlalchemy.orm import Session, class_mapper
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.inspection import inspect
from pydantic import BaseModel

from ..db import sqa
from .model import FormSchema, FormField, FormPanel, GridSubTableType
from ..utils.misc import (quoter, set_attr, get_attr, get_dict, copy_nested_fields,
                          string_to_type)
from ..config import config
from ..server.jobq.tasks import get_image_filename


log = logging.getLogger(__name__)


class Params(BaseModel):
    Depth: int = 1
    CompanyRowId: Optional[int] = None
    Locale: Optional[str] = None
    Timezone: Optional[str] = None
    FieldList: Optional[List[str]] = None


class ListCriteriaType(IntEnum):
    ALL = 0
    ANY = 1
    NONE = 2
    NOT_ALL = 3


class ListGridParams(Params):
    Criteria: Optional[List[Dict[str, Any]]] = None
    # list of dict [{"field": "UserId", "op": "12", "value": "gvv"},
    #               {"field": "Personal.Gender.Gender", "op": "0", "value": "Male"}]
    # UserId contains "gvv", Personal.Gender.Gender == "Male"
    CriteriaType: ListCriteriaType = ListCriteriaType.ALL
    Columns: Optional[List[Dict[str, Any]]] = None
    # list of dict [{"name": "Id", "label": "Id", "column_label": "Id", "table": "SatDraws", "type": "Integer",
    #               "child_name": "Id", "required": true, "modifiable": false, "sortable": true, "visible": true,
    #               'options': {'sort': True, 'display': 'true', 'sortDirection': 'none'}},
    #               ...]
    Offset: int = 0
    # Paging first record indicator.
    # This is the start point in the current data set (0 index based - i.e. 0 is the first record).
    PageSize: int = 20
    # Number of records that the table can display in the current draw.
    # It is expected that the number of records returned will be equal to this number,
    # unless the server has fewer records to return.
    # Note that this can be -1 to indicate that all records should be returned
    # (although that negates any benefits of server-side processing!)
    ChoicesAsTuple: bool = False
    # choices field returned as tuple (key, value)
    ChoicesKey: bool = True
    # if ChoicesAsTuple is False then
    # if ChoicesKey is True then return key else return value
    TextAsString: bool = True
    # display datatype Text as String else will be converted to Object
    Draw: int = 1
    # Draw counter. To ensure that the Ajax returns from server-side processing requests are
    # drawn in sequence (Ajax requests are asynchronous and thus can return out of sequence).
    # This is used as part of the draw return parameter.
    SelectedRows: Optional[List[int]] = None
    # selected rows to check if row ids still exist within this criteria


class ListParams(ListGridParams):
    DbTableName: str


class ListChildParams(ListGridParams):
    ParentTable: str
    ParentField: str
    ParentRowId: int


class ListResult(BaseModel):
    recordsTotal: int
    # Total records, after filtering (i.e. the total number of records after filtering has been applied -
    # not just the number of records being returned for this page of data).
    data: List[Dict[str, Any]]
    draw: int = 1
    # The draw counter that this object is a response to - from the draw parameter sent as part of
    # the data request. Note that it is strongly recommended for security reasons that you cast this
    # parameter to an integer, rather than simply echoing back to the client what it sent in the
    # draw parameter, in order to prevent Cross Site Scripting (XSS) attacks.
    selectedRows: Optional[List[int]] = None
    # selected rows where row ids still exist within given criteria


class EnumResult(BaseModel):
    recordsTotal: int
    # Total records, after filtering (i.e. the total number of records after filtering has been applied -
    # not just the number of records being returned for this page of data).
    data: List[Tuple[Any, ...]]
    draw: int = 1
    # The draw counter that this object is a response to - from the draw parameter sent as part of
    # the data request. Note that it is strongly recommended for security reasons that you cast this
    # parameter to an integer, rather than simply echoing back to the client what it sent in the
    # draw parameter, in order to prevent Cross Site Scripting (XSS) attacks.


def build_joins(field_name: str,
                joins: Optional[List[Tuple[str, str, str, str, bool, str]]] = None,
                join_tables: Optional[Dict[str, int]] = None):
    """
    build join path
    :param field_name: field name in table_name.field_name format
                    table_name is Db TableName NOT TableClassName (Mapper)
                    ie. Programs.Name NOT Program.Name
    :param joins: join structure
        joins element: (table, "key", "joinTable", "alias", "nullable", "cardinality")
        joins:  [('Countries', 'CreateOpId', 'Users', u'Countries_CreateOpId'),
                ('Countries', 'ModifiedOpId', 'Users', u'Countries_ModifiedOpId')]
    :param join_tables: joinTables count
        join_tables:  {'Users': 2}
    :return: joins = list(), join_tables = dict()
    """
    if joins is None:
        joins = list()
    if join_tables is None:
        join_tables = dict()

    # populate joins
    if "." in field_name:
        # field_name has table_name in the . format
        join_list = sqa.get_joinlist(field_name)
        if join_list:
            for j in join_list:
                # (table, "key", "joinTable", "alias", "nullable", "cardinality")
                # check if unique
                if not any(jp == j for jp in joins):
                    joins.append(j)
                    # count join tables
                    if j[2] not in join_tables:
                        join_tables[j[2]] = 0
                    join_tables[j[2]] += 1

    return joins, join_tables


def build_join_alias(joins: List[Optional[Tuple[str, str, str, str, bool, str]]],
                     join_tables: Dict[str, int]):
    """
    build join alias
    :param joins: join structure
        joins element: (table, "key", "joinTable", "alias", "nullable", "cardinality")
        joins:  [('Countries', 'CreateOpId', 'Users', u'Countries_CreateOpId'),
                ('Countries', 'ModifiedOpId', 'Users', u'Countries_ModifiedOpId')]
    :param join_tables: joinTables count
        join_tables:  {'Users': 2}
    :return:
        alias: {'Countries_CreateOpId': <AliasedClass at 0x54e1890; User>,
                'Countries_ModifiedOpId': <AliasedClass at 0x54e1050; User>}
    """
    alias = dict()
    # setup alias
    for j in joins:
        if join_tables[j[2]] > 1:
            alias[j[3]] = sqa.set_alias(j[2])

    return alias


def build_sort(db_table_name: str,
               columns: List[Optional[Dict[str, Any]]]):
    """
    :param db_table_name: Db TableName NOT TableClassName (Mapper)
                        ie. Programs NOT Program
    :param columns:
    # list of dict [{"name": "Id", "label": "Id", "column_label": "Id", "table": "SatDraws", "type": "Integer",
    #               "child_name": "Id", "required": true, "modifiable": false, "sortable": true, "visible": true,
    #               'options': {'sort': True, 'display': 'true', 'sortDirection': 'none'}},
    #               ...]
    :return:
    """
    join_tables = dict()  # join tables count
    joins = list()
    sort = list()
    # populate joins
    if columns:
        for o in columns:
            if not o["options"]["display"]:
                continue

            try:
                direct = o["options"]["sortDirection"]
            except:
                continue
            if direct == "none":
                continue

            col = o["name"]

            if "." in col:
                if db_table_name not in col:
                    col = f"{db_table_name}.{col}"
                joins, join_tables = build_joins(col, joins, join_tables)

                join_list = sqa.get_joinlist(col)
                if join_list:
                    # join_list = [(table, "key", "joinTable", "alias", "nullable", "cardinality")]
                    tf = col.split(".")
                    sort.append((join_list[-1][2] + "." + tf[-1], direct, join_list[-1][3]))
                else:
                    tf = col.split(".")
                    sort.append((tf[-1], direct, None))
            else:
                sort.append((col, direct, None))

    info = sqa.get_table_info(db_table_name)
    if "sum" not in info:
        # always sort by MainTable.Id to keep query consistent during page change
        id_found = [s for s in sort if s[0] == "Id"]
        if not id_found:
            sort.append(("Id", "asc", None))

    return sort, joins, join_tables


def build_field_joins(db_table_name: str,
                      columns: List[Optional[Dict[str, Any]]],
                      joins: List[Optional[Tuple[str, str, str, str, bool, str]]],
                      join_tables: Dict[str, int]):

    if columns:
        for fld in columns:
            if fld["options"]["display"]:
                col = fld["name"]
                if "." in col:
                    if db_table_name not in col:
                        col = f"{db_table_name}.{col}"
                    joins, join_tables = build_joins(col, joins, join_tables)
    return joins, join_tables


def build_filters(db_table_name: str,
                  criteria: List[Optional[Dict[str, Any]]],
                  joins: List[Optional[Tuple[str, str, str, str, bool, str]]],
                  join_tables: Dict[str, int]):
    """
    :param db_table_name: Db TableName NOT TableClassName (Mapper)
                        ie. Programs NOT Program
    :param criteria:
    # list of dict [{"field": "UserId", "op": "12", "value": "gvv"},
    #               {"field": "Personal.Gender.Gender", "op": "0", "value": "Male"}]
    # UserId contains "gvv", Personal.Gender.Gender == "Male"
    :param joins: join structure
        joins element: (table, "key", "joinTable", "alias", "nullable", "cardinality")
        joins:  [('Countries', 'CreateOpId', 'Users', u'Countries_CreateOpId'),
                ('Countries', 'ModifiedOpId', 'Users', u'Countries_ModifiedOpId')]
    :param join_tables: joinTables count
        join_tables:  {'Users': 2}
    :return:
    """
    filters = list()
    if criteria:
        for c in criteria:
            col = c["field"]
            if "." in col:
                if db_table_name not in col:
                    col = f"{db_table_name}.{col}"
                joins, join_tables = build_joins(col, joins, join_tables)

            filters.append(c)

    return filters, joins, join_tables


def build_where(db_table_name: str,
                timezone: str,
                filters: Optional[List[Dict[str, Any]]] = None,
                criteria_type: ListCriteriaType = ListCriteriaType.ALL,
                join_tables: Optional[Dict[str, int]] = None,
                alias: Optional[Dict[str, Any]] = None,
                company_id: Optional[int] = None,
                company_ids: Optional[List[int]] = None,
                where: str = None):
    """
    :param db_table_name: Db TableName NOT TableClassName (Mapper)
                        ie. Programs NOT Program
    :param timezone:
    :param filters: list of {field, value, operation} dict
                [{'field': 'Gender', 'value': 'female', 'op': '0'},..]
                where op:
                0=EQUALS
                1=NOT EQUALS
                2=LESS THAN
                3=LESS THAN or EQUALS
                4=GREATER THAN
                5=GREATER THAN or EQUALS
                6=BETWEEN
                7=NOT BETWEEN
                8=IN LIST
                9=NOT IN LIST
                10=BEGINS
                11=NOT BEGINS
                12=ENDS
                13=NOT ENDS
                14=CONTAINS
                15=NOT CONTAINS
                16=EMPTY
                17=NOT EMPTY
    :param criteria_type: 0=ALL; 1=ANY; 2=NONE; 3=NOT ALL
    :param join_tables: joinTable count
            join_tables:  {'Users': 2}
    :param alias: join tables alias
        alias: {'Countries_CreateOpId': <AliasedClass at 0x54e1890; User>,
                'Countries_ModifiedOpId': <AliasedClass at 0x54e1050; User>}
    :param company_id: Company ID
    :param company_ids:
    :param where: external defined where
    :return:
    """
    if filters is None:
        filters = list()
    if join_tables is None:
        join_tables = dict()
    if alias is None:
        alias = dict()

    if where is None:
        # check if Company Exists in table
        table_company_field = None
        company_field = None
        info = sqa.get_table_info(db_table_name)
        if info is not None and "companyField" in info:
            company_field = info["companyField"]
            table_company_field = company_field
            if company_field.endswith("_Id"):
                table_company_field = company_field[:-3]
        if company_field is not None:
            # check if company_field in filters
            found = False
            for f in filters:
                if (table_company_field == f["field"] or
                    f"{table_company_field}." in f["field"]):
                    found = True
                    break
            if not found:
                where = f"{company_field} = {company_id}"
            elif company_ids:
                where = f"{company_field} in ({str(company_ids).strip('[]')})"

    # filters
    # [{'field': 'Gender', 'value': 'female', 'op': '0'},..]
    #
    if filters:
        if where is not None:
            if criteria_type.value > 1:
                where += " and not ("
            else:
                where += " and ("
        else:
            if criteria_type.value > 1:
                where = "not ("
            else:
                where = "("

        i = 1
        for f in filters:
            k = f["field"]
            if i > 1:
                if criteria_type.value == 0:  # ALL
                    where += " and "
                elif criteria_type.value == 1:  # ANY
                    where += " or "
                elif criteria_type.value == 2:  # NONE
                    where += " and "
                elif criteria_type.value == 3:  # NOT ALL
                    where += " or "
            i += 1

            # join_tables is joinTable count
            # join_tables:  {'Users': 2}
            ins_attr = None
            if "." in k:
                if db_table_name not in k:
                    k = f"{db_table_name}.{k}"
                join_list = sqa.get_joinlist(k)

                if join_list:
                    # join_list: [(table, "key", "joinTable", "alias", "nullable")]
                    tf = k.split(".")
                    ins_attr = sqa.instrumented_attr(join_list[-1][2], tf[-1],
                                                     alias)  # <class 'sqlalchemy.orm.attributes.InstrumentedAttribute'>
                    if join_tables[join_list[-1][2]] > 1:
                        # use alias table
                        k = join_list[-1][3] + "." + tf[-1]
            if ins_attr is None:
                ins_attr = sqa.instrumented_attr(db_table_name,
                                                 k)  # <class 'sqlalchemy.orm.attributes.InstrumentedAttribute'>

            if "." not in k:
                k = f"{db_table_name}.{k}"

            try:
                value_type = ins_attr.type.__class__.__name__
            except:
                # must be hybrid_property
                value_type = None

            op = int(f["op"])
            if op > 5 and op < 10:  # BETWEEN,LIST
                list_val = f["value"]
                if not isinstance(f["value"], list):
                    # must be string - convert to list maintaining datatype
                    list_val = []
                    if "," in f["value"]:
                        for v in f["value"].split(","):
                            if isinstance(v, dict):
                                list_val.append(v)
                            else:
                                list_val.append(string_to_type(value_type, v.strip()))
                    else:
                        list_val.append(f["value"])
                # convert list to value string
                val = ""
                for idx, v in enumerate(list_val):
                    if op < 8 and idx > 1:
                        # BETWEEN
                        break
                    if isinstance(v, dict):
                        key = k.split(".")[-1]
                        val += (("," if val != "" else "") +
                                quoter(v[key], return_string=True))
                    else:
                        val += (("," if val != "" else "") +
                                quoter(v, return_string=True))
            elif value_type == "DateTime":
                # parse filter["value"] to datetime
                # convert naive datetime to timezone aware datetime
                # convert timezone aware to utc datetime
                # then remove tzinfo so val is now utc naive
                if op > 15:
                    val = None
                else:
                    val = '{:%Y-%m-%d %H:%M:%S}'.format(pytz.timezone(timezone).
                                                        localize(dateutil.parser.parse(f["value"])).
                                                        astimezone(pytz.UTC).replace(tzinfo=None))
            elif value_type == "Date":
                if op > 15:
                    val = None
                else:
                    val = '{:%Y-%m-%d}'.format(dateutil.parser.parse(f["value"]).date())
            elif value_type == "Time":
                if op > 15:
                    val = None
                else:
                    val = '{:%H:%M:%S}'.format(dateutil.parser.parse(f["value"]).time())
            elif value_type == "Boolean":
                if op < 2:
                    val = f["value"]
                else:  # op > 15
                    val = False
            else:
                if type(f["value"]) is dict:
                    key = k.split(".")[-1]
                    val = quoter(f["value"][key], value_type)
                else:
                    val = quoter(f["value"], value_type)
                if op > 15:
                    val = ""

            if op == 0:  # EQUALS
                where += f" {k} = {val} "
            elif op == 1:  # NOT EQUALS
                where += f" {k} != {val} "
            elif op == 2:  # LESS THAN
                where += f" {k} < {val} "
            elif op == 3:  # LESS THAN OR EQUALS
                where += f" {k} <= {val} "
            elif op == 4:  # GREATER THAN
                where += f" {k} > {val} "
            elif op == 5:  # GREATER THAN OR EQUALS
                where += f" {k} >= {val} "
            elif op == 6:  # BETWEEN
                where += f" {k} between ({val}) "
            elif op == 7:  # NOT BETWEEN
                where += f" not {k} between ({val}) "
            elif op == 8:  # IN LIST
                where += f" {k} in ({val}) "
            elif op == 9:  # NOT IN LIST
                where += f" not {k} in ({val}) "
            elif op == 10:  # BEGINS
                where += f" {k} startswith ({val}) "
            elif op == 11:  # NOT BEGINS
                where += f" not {k} startswith ({val}) "
            elif op == 12:  # ENDS
                where += f" {k} endswith ({val}) "
            elif op == 13:  # NOT ENDS
                where += f" not {k} endswith ({val}) "
            elif op == 14:  # CONTAINS
                where += f" {k} contains ({val}) "
            elif op == 15:  # NOT CONTAINS
                where += f" not {k} contains ({val}) "
            elif op == 16:  # EMPTY
                where += f" ({k} = None or {k} = {val}) "
            # TODO: get this to work - not empty should also check for space/s
            elif op == 17:  # NOT EMPTY
                where += f" ({k} != None or {k} != {val}) "

        where += ")"
    print("schema.datasource.build_where:", where)
    return where


def query(db_session: Session,
          db_table_name: str,
          columns: List[Optional[Dict[str, Any]]],
          where: Optional[str] = None,
          sort: Optional[List[Tuple[str, str, str]]] = None,
          join_tables: Optional[Dict[str, int]] = None,
          joins: Optional[List[Tuple[str, str, str, str, bool, str]]] = None,
          alias: Optional[Dict[str, Any]] = None):
    """
    :param db_session:  sqlalchemy.orm.Session
    :param db_table_name: db table name NOT mapper table class name
                        ie: Programs NOT Program
    :param columns:
    # list of dict [{"name": "Id", "label": "Id", "column_label": "Id", "table": "SatDraws", "type": "Integer",
    #               "child_name": "Id", "required": true, "modifiable": false, "sortable": true, "visible": true,
    #               'options': {'sort': True, 'display': 'true', 'sortDirection': 'none'}},
    #               ...]
    :param where: where string
    :param sort: list of tuples [(field_name, direction, alias,),..]
        field_name
        direction: asc or desc
        alias
    :param join_tables: joinTable count
            join_tables:  {'Users': 2}
    :param joins: join structure
            joins element: (table, "key", "joinTable", "alias", "nullable", "cardinality")
            joins:  [('Countries', 'CreateOpId', 'Users', u'Countries_CreateOpId'),
                    ('Countries', 'ModifiedOpId', 'Users', u'Countries_ModifiedOpId')]
    :param alias: join tables alias
        alias: {'Countries_CreateOpId': <AliasedClass at 0x54e1890; User>,
                'Countries_ModifiedOpId': <AliasedClass at 0x54e1050; User>}
    :return: list of db.models record db_table_name instances
        [<gvv.db.models.system.Programs.Program object at 0x7f1d30bf3588>,
        <gvv.db.models.system.Programs.Program object at 0x7f1d30bf3828>]
    """
    if sort is None:
        sort = list()
    if join_tables is None:
        join_tables = dict()
    if joins is None:
        joins = list()
    if alias is None:
        alias = dict()
    # TODO: handle sum and running balance in one query

    info = sqa.get_table_info(db_table_name)
    # query
    if "sum" in info:
        qry = db_session.query()
        for col in columns:
            if col["options"]["display"]:
                col_name = f"{db_table_name}.{col['name']}"
                if col["name"] in info["sum"]:
                    qry = qry.add_columns(func.sum(sqa.get_column(col_name)).
                                          label(col["name"]))
                else:
                    qry = qry.add_columns(sqa.get_column(col_name).label(col['name']))
                    qry = qry.group_by(sqa.get_column(col_name))
                    qry = qry.order_by(asc(sqa.get_column(col_name)))
    elif "runningBalance" in info:
        qry = db_session.query()
    else:
        qry = db_session.query(sqa.get_model(db_table_name))
        # session.query(Countries).join(Countries.CreateOpId).order_by(Users.Name)

    for j in joins:
        # join_list: (table, "key", "joinTable", "alias", "nullable", "cardinality")
        try:
            if join_tables[j[2]] > 1:
                # using alias for this join table
                if j[4]: # nullable
                    qry = qry.outerjoin(alias[j[3]], sqa.instrumented_attr(j[0], j[1]))
                else:
                    qry = qry.join(alias[j[3]], sqa.instrumented_attr(j[0], j[1]))
            else:
                if j[4]:  # nullable
                    qry = qry.outerjoin(sqa.instrumented_attr(j[0], j[1]))
                else:
                    qry = qry.join(sqa.instrumented_attr(j[0], j[1]))
        except:
            continue

    sorts = list()
    for k, v, al in sort:
        col = k.strip()
        if v == "asc":
            if "." in col:
                tf = col.split(".")
                if join_tables[tf[0]] > 1 and al is not None:
                    # using alias for this join table
                    srt = asc(sqa.instrumented_attr(al, tf[1]))
                else:
                    srt = asc(sqa.instrumented_attr(tf[0], tf[1]))
            else:
                srt = asc(sqa.instrumented_attr(db_table_name, col))
        else:
            if "." in col:
                tf = col.split(".")
                if join_tables[tf[0]] > 1 and al is not None:
                    # using alias for this join table
                    srt = desc(sqa.instrumented_attr(al, tf[1]))
                else:
                    srt = desc(sqa.instrumented_attr(tf[0], tf[1]))
            else:
                srt = desc(sqa.instrumented_attr(db_table_name, col))

        qry = qry.order_by(srt)
        sorts.append(srt)

    if "runningBalance" in info:
        for col in columns:
            if col["name"] == "Id":
                col_name = f"{db_table_name}.{col['name']}"
                qry = qry.add_columns(sqa.get_column(col_name).label(col["name"]))
            elif col["options"]["display"]:
                if col["name"].startswith("RunningBalance_"):
                    col_name = col["name"].replace("RunningBalance_", "").strip()
                    qry = qry.add_columns(
                        func.sum(sqa.get_column(col_name)).over(
                            order_by=[s for s in sorts]
                        ).label(col["name"])
                    )
                else:
                    col_name = f"{db_table_name}.{col['name']}"
                    qry = qry.add_columns(sqa.get_column(col_name).label(col["name"]))

    if where is not None:
        qry = qry.filter(sqa.where(where, table_name=db_table_name, alias=alias))

    return qry


# https://gist.github.com/hest/8798884
def get_record_count(qry: Session.query):
    count_q = qry.statement.with_only_columns([func.count()]).order_by(None)
    count = qry.session.execute(count_q).scalar()
    if count is None:
        return 0
    return count


def result_page(qry: Session.query,
                start: int,
                page_size: int,
                total_records: int):

    if page_size == -1:
        start = 0
        page_size = total_records

    return qry.limit(page_size).offset(start)


def valid_selected_rows(qry: Session.query,
                        rows: List[int]) -> List[int]:

    recs = qry.all()
    selected_rows = [r.Id for r in recs if r.Id in rows]

    # TODO: below is faster but gets complicated when qry has joins
    # error "column reference Id is ambiguous"

    #q_ids = qry.statement.with_only_columns([sqa.get_column("Id")])
    #ids = qry.session.execute(q_ids)
    #selected_rows = [r.Id for r in ids if r.Id in rows]

    return selected_rows


def get_table_list(db_table_name: str,
                   params: ListParams,
                   session: Session,
                   current_user_id: int,
                   where: str = None,
                   audit: bool = False,
                   table_class: DeclarativeMeta = None) -> ListResult:

    user = session.query(sqa.get_model("Users")).get(current_user_id)

    company_ids = list()
    # valid companies
    if params.CompanyRowId is None:
        company_ids.append(user.Company_Id)
    else:
        company_ids.append(params.CompanyRowId)
    for coys in user.Role.Group.Companies:
        if coys.Id not in company_ids:
            company_ids.append(coys.Id)

    if params.Locale is None:
        params.Locale = user.Settings.Locale
    if params.Timezone is None:
        params.Timezone = user.Settings.Timezone


    info = sqa.get_table_info(db_table_name)

    sort, joins, join_tables = build_sort(db_table_name, params.Columns)
    joins, join_tables = build_field_joins(db_table_name, params.Columns,
                                           joins, join_tables)
    filters, joins, join_tables = build_filters(db_table_name, params.Criteria,
                                                joins, join_tables)
    alias = build_join_alias(joins, join_tables)
    where = build_where(db_table_name, params.Timezone, filters,
                        params.CriteriaType, join_tables, alias,
                        user.Company_Id, company_ids, where)

    qry = query(session, db_table_name, params.Columns,
                where, sort, join_tables, joins, alias
                )

    if "sum" in info:
        total_records = len(qry.all())
    else:
        total_records = get_record_count(qry)

    # handle filter changes
    if total_records < params.Offset:
        params.Offset = 0

    if params.SelectedRows is not None and len(params.SelectedRows) > 0:
        params.SelectedRows = valid_selected_rows(qry, params.SelectedRows)

    recs = result_page(qry, params.Offset, params.PageSize, total_records)
    if "sum" in info or "runningBalance" in info:
        # isinstance(r, tuple):
        # <class 'sqlalchemy.util._collections.result'>
        data = [result_to_dict(r, info, params.Columns, [], index=idx)
                           for idx, r in enumerate(recs)]
    else:
        field_list = list()
        if params.FieldList:
            for v in params.FieldList:
                if v not in field_list:
                    field_list.append(v)

        if audit:
            except_fields = ["Password", "version_parent"]
        else:
            except_fields = ["Password", "versions"]

        field_data = [r.data_to_dict(except_fields=except_fields,
                               depth=params.Depth,
                               audit=audit,
                               table_class=table_class,
                               tuple_choice=params.ChoicesAsTuple,
                               choice_key=params.ChoicesKey,
                               text_as_string=params.TextAsString,
                               m2m_merge=True,
                               one2m_list=True,
                               ignore_calc_fields=False,
                               dump=False
                               )
                           for r in recs]
        if field_list:
            data = list()
            for r in field_data:
                data.append(copy_nested_fields(r, field_list))
        else:
            data = field_data

    return ListResult(
        draw=params.Draw,
        recordsTotal=total_records,
        selectedRows=params.SelectedRows,
        data=data
    )


class FormMode(str, Enum):
    Create = "Create"
    Update = "Update"
    Delete = "Delete"


class FormParamsCommon(Params):
    Mode: FormMode = FormMode.Create
    ChoicesAsTuple: bool = True
    # choices field returned as tuple (key, value)
    ChoicesKey: bool = False
    # if ChoicesAsTuple is False then
    # if ChoicesKey is True then return key else return value
    TextAsString: bool = True
    # display datatype Text as String else will be converted to Object


# FormParams by RowId
class FormParams(FormParamsCommon):
    DbTableName: str
    RowId: int = 0


class FormChildParams(FormParamsCommon):
    ParentTable: str
    ParentField: str
    ParentRowId: int
    RowId: int = 0


# FormParams by Criteria
class FormParamsCriteria(FormParamsCommon):
    DbTableName: str
    Criteria: Optional[List[Dict[str, Any]]] = None
    # list of dict [{"field": "UserId", "op": "12", "value": "gvv"},
    #               {"field": "Personal.Gender.Gender", "op": "0", "value": "Male"}]
    # UserId contains "gvv", Personal.Gender.Gender == "Male"


class FormResult(BaseModel):
    data: Dict[str, Any]


def form_data(record: DeclarativeMeta,
              params: FormParamsCommon) -> FormResult:

    field_list = list()
    if params.FieldList:
        for v in params.FieldList:
            if v not in field_list:
                field_list.append(v)

    result = dict()
    field_data = record.data_to_dict(except_fields=["Password", "versions"],
                                     depth=params.Depth,
                                     tuple_choice=params.ChoicesAsTuple,
                                     choice_key=params.ChoicesKey,
                                     text_as_string=True,
                                     m2m_merge=False,
                                     one2m_list=True,
                                     ignore_calc_fields=False,
                                     dump=False)
    if field_list:
        result["data"] = list()
        for r in field_data:
            result["data"].append(copy_nested_fields(r, field_list))
    else:
        result["data"] = field_data

    return result


class CUDAvail(BaseModel):
    IsAvail: bool


class CUD(BaseModel):
    """
        Create, Update, Delete Table Parameters
    """
    Depth: int = 1
    DbTableName: str
    CompanyRowId: Optional[int] = None
    Locale: Optional[str] = None
    Timezone: Optional[str] = None
    RowId: int = 0
    Schema: Optional[FormSchema] = None


class CUDParams(CUD):
    """
        Create, Update, Delete Table Parameters
    """
    Data: Dict[str, Any]


class SequentialCUDParams(CUD):
    """
        Create, Update, Delete Table Parameters
    """
    Data: List[Dict[str, Any]]


class CUDChildParams(CUDParams):
    """
        Create, Update, Delete Child Table Parameters
    """
    ParentTable: str
    ParentField: str
    ParentRowId: int
    join_list: Optional[List[List[Any]]] = None


class SequentialCUDChildParams(SequentialCUDParams):
    """
        Create, Update, Delete Child Table Parameters
    """
    ParentTable: str
    ParentField: str
    ParentRowId: int
    join_list: Optional[List[List[Any]]] = None


class CUDStatus(BaseModel):
    """
        Create, Update, Delete Table Status
    """
    success: bool
    message: str
    RecordRowId: int = 0

def get_form_fields(table_name, fields, key, except_fields=[]):
    table_class = sqa.get_model(table_name)

    for column in inspect(table_class).columns:
        if column.key in except_fields:
            continue
        if "modifiable" in column.info and not column.info["modifiable"]:
            continue
        if "hidden" in column.info and column.info["hidden"]:
            continue

        name = column.name
        use_list = False
        join=False
        join_list = None
        for fk in column.foreign_keys:
            # name = ItemWarehouse_Id
            fKey = str(fk.column)  # Warehouses.Id
            sufix = ("_%s" % fKey.split(".")[-1]) # _Id
            if sufix in name:
                name = name.replace(sufix, "").strip() # ItemWarehouse
                mapper = class_mapper(table_class)
                prop = mapper.attrs.get(name)
                join=True
                use_list = prop.uselist
                join_list = sqa.get_joinlist(f"{table_class.__table__.name}.{name}")
                break

        if len(key.split(".")) == 1:
            key_string = name
        else:
            key_string = f"{key.split('.', 1)[-1]}.{name}"

        fld_type =  column.type.__class__.__name__
        if "choices" in column.info:
            fld_type = "Enum"
        elif "selectKey" in column.info and column.info["selectKey"] is not None:
            fld_type = "Select"

        fields.append(FormField(
            name=key_string,
            label=column.info["label"] if "label" in column.info else column.key,
            table=table_class.__table__.name,
            type=fld_type,
            listFormat=column.info["listFormat"] if "listFormat" in column.info else False,
            case=column.info["case"] if "case" in column.info else None,
            use_list=use_list,
            join=join,
            join_list=join_list,
            field_name=name
        ))


def get_form_panels(table_name, panels, fields, key, except_fields=[]):

    get_form_fields(table_name, fields, key, except_fields)

    table_class = sqa.get_model(table_name)
    relationships = inspect(table_class).relationships
    for rel_name, rel in relationships.items():
        if rel_name in except_fields:
            continue
        if "hidden" in rel.info and rel.info["hidden"]:
            continue

        if rel.direction.name != "ONETOMANY":
            continue
        try:
            rel_col = table_class.__table__.columns[f"{rel_name}_Id"]
            if "modifiable" in rel_col.info and not rel_col.info["modifiable"]:
                continue
        except:
            pass
        key_string = f"{key}.{rel_name}"
        info = sqa.get_table_info(rel.mapper.class_.__tablename__)
        join_list = sqa.get_joinlist(f"{table_class.__table__}.{rel_name}")

        panels.append(FormPanel(table=rel.mapper.class_.__tablename__,
                        label=info["label"],
                        desc=info["desc"],
                        baseTable=info["baseTable"],
                        keyField=info["key"],
                        parent=table_name,
                        type=rel.direction.name,
                        use_list=rel.uselist,
                        # Users.Personal.Address.State after split is Personal.Address.State
                        # remove main table
                        id=key_string.split(".", 1)[-1],
                        actionOn=list(),
                        key=key_string,
                        join_list=join_list,
                        field_list=rel_name,
                        gridSubTableType=GridSubTableType.Grid if rel.uselist else GridSubTableType.Form,
                        requiredEntry=rel.info["requiredEntry"] if "requiredEntry" in rel.info else None,
                        viewer=info["viewer"] if "viewer" in info else None,
                        loader=info["loader"] if "loader" in info else None,
                        document=info["document"] if "document" in info else None
                        )
                   )
        get_form_fields(rel.mapper.class_.__tablename__, fields, key_string, except_fields)
        # ONETOONE - dive one level down
        if not rel.uselist:
            get_form_panels(rel.mapper.class_.__tablename__, panels, fields, key_string, except_fields)

def populate_record(db_session: Session,
                    record: DeclarativeMeta,
                    table_name: str,
                    company_rowid: int,
                    timezone: str,
                    form_data: Dict[str, Any],
                    schema_form_fields=None,
                    schema_form_panels=None,
                    create: bool = False):
    """
        populate database record with web json data
    :param db_session:
    :param record:
    :param table_name:
    :param company_rowid:
    :param timezone:
    :param form_data:
    :param schema_form_fields:
    :param schema_form_panels:
    :param create:
    :return:
    """
    if create:  # create record
        company_field = None
        info = sqa.get_table_info(table_name)
        if info is not None and "companyField" in info:
            company_field = info["companyField"]
        # Company Table Primary Key is Id
        # in create mode Id should not be populated
        if company_field is not None and company_field != "Id":
            try:
                if "." in company_field:
                    company = company_field.split(".")[-1]
                else:
                    company = company_field
                setattr(record, company, company_rowid)
            except Exception as err:
                log.info(f"schemas.datasource.populate_record company_field Exception: {str(err)}")
    if schema_form_fields is None:
        for key, value in form_data.items():
            try:
                set_attr(record, key, value)
            except Exception as err:
                log.info(f"schemas.datasource.populate_record schema_form_fields=None set_attr Exception: {key} : {str(err)}")
    elif schema_form_panels is None:
        for field in schema_form_fields:
            try:
                set_attr(record, field.field_name, convert_data(db_session, field, timezone, form_data))
            except Exception as err:
                log.info(f"schemas.datasource.populate_record schema_form_panels=None set_attr Exception: {field.table} : {field.field_name} : {field.type} : {str(err)}")
        # get form panels beyond level 1
        panels = list()
        schema = list()
        get_form_panels(table_name, panels, schema, table_name, ["versions"])
        if len(panels):
            populate_record(db_session, record, table_name, company_rowid, timezone, form_data,
                            schema, panels, create)
    else:
        for panel in schema_form_panels:
            form_fields = [field for field in schema_form_fields if field.table == panel.table]
            if panel.use_list:
                items = get_attr(record, panel.id, [])
                # delete existing records not in form data
                for idx, item in enumerate(items):
                    found = False
                    for d in get_dict(form_data, panel.id, []):
                        if "__mode" not in d and d["Id"] == get_attr(item, "Id", None):
                            found = True
                            break
                    if not found:
                        deleted_item = items.pop(idx)
                        db_session.delete(deleted_item)

                for item in get_dict(form_data, panel.id, []):
                    found = False
                    rec = None
                    # get existing record
                    if "__mode" not in item:
                        for r in items:
                            if item["Id"] == get_attr(r, "Id", None):
                                found = True
                                rec = r
                                break
                    del item["Id"]

                    if not found:
                        if panel.join_list:
                            t_name = panel.join_list[-1][2]
                        else:
                            t_name = panel.table

                        rec = sqa.get_model(t_name)()
                        if rec.is_poly_base():
                            poly_on = rec.get_poly_base_on_name()
                            rec = rec.get_poly_base_on_obj(get_dict(item, poly_on))

                    populate_record(db_session, rec, panel.table, company_rowid, timezone, item,
                                    form_fields, schema_form_panels=None, create=True)
                    if not found:
                        db_session.add(rec)
                        items.append(rec)

                set_attr(record, panel.id, items)
            else:
                if panel.id is not None:
                    if panel.join_list:
                        t_name = panel.join_list[-1][2]
                    else:
                        t_name = panel.table
                    rec = sqa.get_model(t_name)()
                    if rec.is_poly_base():
                        poly_on = rec.get_poly_base_on_name()
                        rec = rec.get_poly_base_on_obj(get_dict(form_data, poly_on))
                    for field in form_fields:
                        try:
                            set_attr(rec, field.field_name, convert_data(db_session, field, timezone, form_data))
                        except AttributeError as err:
                            log.info(f"schemas.datasource.populate_record set_attr AttributeError: {field.table} : {field.field_name} : {field.type} : {str(err)}")

                    db_session.add(rec)
                    set_attr(record, panel.id, rec)
                else:
                    for field in form_fields:
                        try:
                            set_attr(record, field.name, convert_data(db_session, field, timezone, form_data))
                        except AttributeError as err:
                            log.info(f"schemas.datasource.populate_record set_attr AttributeError: {field.table} : {field.name} : {field.type} : {str(err)}")


def convert_data(db_session: Session,
                 field: FormField,
                 timezone: str,
                 data: Dict[str, Any]):
    """
    convert web json data to python data type
    NOTE: datetime,time,date in database is in utc - naive datetime
    :db_session:
    :field:
    :timezone:
    :data:
    :return: python field value
    """
    name = field.name
    if get_dict(data, name) is None:
        name = field.field_name
        if get_dict(data, name) is None:
            log.info(f"schemas.datasource.convert_data Name Exception: {name} : {field.name} : {field.field_name}")
            return None

    val = get_dict(data, name)
    try:
        if field.use_list:
            list_val = list()
            if val is not None:
                for idx, ele in enumerate(val):
                    list_val.append(convert_data2(db_session, field, timezone, ele))
            return list_val
        else:
            return convert_data2(db_session, field, timezone, val)
    except Exception as err:
        log.info(f"schemas.datasource.convert_data Value Exception: {name} : {field.type} : {val} : {str(err)}")
        return None


def convert_data2(db_session: Session,
                  field: FormField,
                  timezone: str,
                  value: Any):

    # TODO: use utils.misc.string_to_type function instead of duplicating it here
    if field.listFormat:
        value = str(value or "")
    elif field.type == "String":
        if field.case == "uppercase":
            value = value.upper()
        elif field.case == "lowercase":
            value = value.lower()
        elif field.case == "capitalize":
            value = string.capwords(value)  # like css text-transform capitalize
    elif field.type == "Select":
        table = field.selectTable or field.join_list[0][2]
        val = value
        if isinstance(value, dict):
            val = value["Id"]  # must be a record
        if isinstance(value, str) and value.strip() == "":
            value = None
        else:
            try:
                value = db_session.query(sqa.get_model(table)).get(int(val))
            except Exception as err:
                log.exception(f"schemas.datasource.convert_data2 Select Exception: {table} : {val} : {str(err)}")
                raise ValueError(f"Invalid Select Id: {table} : {val}")
    elif field.type == "Enum":
        if isinstance(value, list) and len(value) > 0:
            value = value[0]
    elif field.type == "Boolean":
        if isinstance(value, str) and value.strip() == "":
            value = False
    elif field.type == "Integer":
        if isinstance(value, str) and value.strip() == "":
            value = 0
            #if field.required:
            #    value = 0
            #else:
            #    value = None
    elif field.type == "BigInteger":
        if isinstance(value, str) and value.strip() == "":
            value = 0
            #if field.required:
            #    value = 0
            #else:
            #    value = None
    elif field.type == "Numeric":
        if isinstance(value, str) and value.strip() == "":
            value = 0
            #if field.required:
            #    value = 0
            #else:
            #    value = None
    elif field.type == "Text":
        if isinstance(value, dict):
            value = json.dumps(value)  # must be json
        else:
            value = str(value)
    elif field.type == "Date":
        try:
            # value is iso date string - yyyy-MM-dd  "2024-12-31"
            if isinstance(value, str) and value.strip() == "":
                value = None
            else:
                value = dateutil.parser.parse(value).date()
        except ValueError:
            log.exception(f"schemas.datasource.convert_data2 Invalid Date: {field.name} : {value}")
            raise ValueError(f"Invalid Date: {field.name} : {value}")
    elif field.type == "Time":
        try:
            # value is iso datetime string - yyyy-MM-dd'T'HH:mm:ss "2024-12-31T14:30:45"
            if isinstance(value, str) and value.strip() == "":
                value = None
            else:
                value = dateutil.parser.parse(value).time()
        except ValueError:
            log.exception(f"schemas.datasource.convert_data2 Invalid Time: {field.name} : {value}")
            raise ValueError(f"Invalid Time: {field.name} : {value}")
    elif field.type == "DateTime":
        try:
            # value is iso datetime string with timezone - yyyy-MM-dd HH:mm:ssXXX  "2024-12-31T14:30:45+11"
            if isinstance(value, str) and value.strip() == "":
                value = None
            else:
                # convert timezone aware datetime to utc datetime
                # then remove tzinfo so value is now naive
                #
                # original value = 2025-01-02T20:07:00GMT+11
                # dateutil.parser.parse bug interprets original value as 2025-01-02T20:07:00-11
                # fixed by removing GMT/UTC
                # fixed value = 2025-01-02 20:07:00+11:00
                # utc value = 2025-01-02 09:07:00+00:00
                # naive value = 2025-01-02 09:07:00
                val = value.replace("GMT","").replace("UTC","")
                if val.endswith("Z") or val.endswith("+00:00") or val.endswith("-00:00"):
                    # already in utc make it naive
                    val2 = dateutil.parser.parse(val)
                else:
                    # convert to utc
                    val2 = dateutil.parser.parse(val).astimezone(pytz.UTC)
                # make it naive
                value = val2.replace(tzinfo=None)
        except ValueError:
            log.exception(f"schemas.datasource.convert_data2 Invalid DateTime: {field.name} : {value}")
            raise ValueError(f"Invalid DateTime: {field.name} : {value}")

    return value


def result_to_dict(result: Tuple[Any],
                   info: Dict[str, Any],
                   columns: List[Dict[str, Any]],
                   except_fields: List[str],
                   index: Optional[int] = None,
                   text_as_string: Optional[bool] = False):
    """
    mimic model.data_to_dict()
    :param result: data record
    :param columns: grid schema
    :param index: record number
    :param text_as_string:
    :return: a nested dict based on grid_schema
    """
    data = dict()
    if index is not None:
        data["Id"] = index

    field_list = list()
    if "runningBalance" in info:
        for col in columns:
            if col["name"] == "Id":
                field_list.append(col)
            elif col["options"]["display"]:
                field_list.append(col)
    else:
        field_list = [col for col in columns if col["options"]["display"]]
    for col, value in zip(field_list, result):
        if col["name"] in except_fields:
            continue
        if col["name"] == "Id":
            data["Id"] = value
            continue

        cur = data
        parts = col["name"].split(".")

        for key in parts[:-1]:
            cur = cur.setdefault(key, {})

        val = value
        if isinstance(value, datetime.datetime):
                # see schemas.datasource.convert_data2 DateTime
                # val is utc and stored as naive datetime
                # val is naive datetime. add Z to look like utc
            val = value.isoformat() + "Z"  # utc
        elif isinstance(value, (datetime.date, datetime.time)):
            val = value.isoformat()
        elif col["type"] == "Numeric":
            val = str(value)
        elif col["type"] == "Text" and not text_as_string:
            try:
                val = json.loads(value)  # convert to dict
            except:
                try:
                    val = ast.literal_eval(value)  # convert to dict
                except:
                    val = value

        cur[parts[-1]] = val

    return data

class UploadFileResult(BaseModel):
    filenames: List[str]
    formats: List[str] = None

def upload_image_file(contents: bytes) -> UploadFileResult:
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()  # validates structure
    except Exception:
        raise "Invalid Image"
    # reopen (img.verify() destroys the stream):
    img = Image.open(io.BytesIO(contents))
    if img.format not in config["image"]["formats"]:
        raise "Unsupported Image Format"

    # convert to our app standard WEBP format and strips everything except pixels
    clean = Image.new(img.mode, img.size)  # create a brand-new image buffer
    clean.putdata(list(img.getdata()))  # read only raw pixel data

    output = io.BytesIO()  # create an in memory file
    clean.save(output, format="WEBP", quality=85)  # 100 = wasteful no benefit
    output.seek(0)  # rewind so can be read later

    # write to file with new filename
    file_name = get_image_filename(config) + ".webp"
    with open(file_name, "wb+") as buffer:
        buffer.write(output.read())

    return UploadFileResult(filenames=[file_name],
                            formats=["WEBP"])


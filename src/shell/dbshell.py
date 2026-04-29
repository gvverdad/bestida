from tabulate import tabulate

from sqlalchemy.ext.declarative.api import DeclarativeMeta

from src.db import db_session, sqa
from src.schemas.datasource import (build_sort, build_field_joins, build_filters,
                                    build_join_alias, build_where,
                                    result_page, get_record_count, query,
                                    ListCriteriaType, valid_selected_rows,
                                    result_to_dict)
from src.schemas.model import grid_schema
from src.utils.misc import (search_list_of_dict, get_dict)


from src.schemas.security import get_companies_list
from src.utils.misc import copy_nested_fields

# run "./shellserver src.shell.dbshell development.ini" in /home/gvv/Projects/bestida


def run(app):
    session = db_session()

    user = session.query(sqa.get_model("Users")).get(1)
    coys = get_companies_list(user)
    company_ids = list()
    for coy in coys:
        company_ids.append(coy[0])

    criteria = list()
    criteria_type = ListCriteriaType.ALL

    table_name = "ProgramStates"
    include_fields = [
                      "Company.CompanyId",
                      "Program.Program",
                      "Program.Type"
    ]
    except_fields = ["Password", "version"]
    """ op
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
    """
    criteria.append(dict(field='Program.Program', value="GridMenus", op=0))
    criteria.append(dict(field='Company.Id', value="1,2", op=8))

    where = None
    offset = 0
    page_size = 999
    selected_rows = None
    audit = False

    info = sqa.get_table_info(table_name)

    grid_tables = list()
    grid_tables.append(dict(table=table_name,
                            use_list=False,
                            parent=None,
                            field_list=None,
                            join_list=list(),
                            label=info["label"],
                            desc=info["desc"],
                            baseTable=info["baseTable"],
                            subTableType="GRID",
                            document=info["document"] if "document" in info else None,
                            crud_constraint=info["crud_constraint"] if "crud_constraint" in info else None,
                            crud_options=info["crud_options"] if "crud_options" in info else None
                            )
                       )

    schema = sqa.get_schema(table_name, 1, remove_duplicate_tables=True)
    scheme = grid_schema(schema, table_name, grid_tables, table_name,
                         except_fields=except_fields
                         )

    header = list()
    columns = list()
    for fld in include_fields:
        field = search_list_of_dict(scheme, "name", fld)
        if field:
            field["options"] = {
                "sort": False,
                "sortDirection": "none",
                "display": field["visible"],
                "modifiable": field["modifiable"]
            }
            header.append(field["column_label"])
            columns.append(field)

    sort, joins, join_tables = build_sort(table_name, columns)
    joins, join_tables = build_field_joins(table_name, columns,
                                           joins, join_tables)
    filters, joins, join_tables = build_filters(table_name, criteria,
                                                joins, join_tables)
    alias = build_join_alias(joins, join_tables)

    where = build_where(table_name, user.Settings.Timezone, filters,
                        criteria_type, join_tables, alias,
                        user.Company_Id, company_ids,
                        where)

    qry = query(session, table_name, columns,
                where, sort, join_tables, joins, alias
                )
    print(qry)
    total_records = get_record_count(qry)
    # handle filter changes
    if total_records < offset:
        offset = 0

    if selected_rows is not None and len(selected_rows) > 0:
        selected_rows = valid_selected_rows(qry, selected_rows)

    recs = result_page(qry, offset, page_size, total_records)
    if "sum" in info:
        # isinstance(r, tuple):
        # <class 'sqlalchemy.util._collections.result'>
        data = [result_to_dict(r, info, columns, [], index=idx)
                           for idx, r in enumerate(recs)]
    else:
        field_list = list()

        if audit:
            except_fields = ["Password", "version_parent"]
        else:
            except_fields = ["Password", "versions"]

        field_data = [r.data_to_dict(except_fields=except_fields,
                               depth=1,
                               audit=audit,
                               table_class=None,
                               tuple_choice=False,
                               choice_key=True,
                               text_as_string=True,
                               m2m_merge=False,
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

    table = list()
    for d in data:
        row = list()
        for f in include_fields:
            row.append(get_dict(d, f))
        table.append(row)

    print(tabulate(table, headers=header))
    print("Total Records:", total_records)

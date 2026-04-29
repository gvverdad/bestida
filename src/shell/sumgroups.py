from tabulate import tabulate

from sqlalchemy.ext.declarative.api import DeclarativeMeta

from src.db import db_session, sqa
from src.schemas.datasource import (build_sort, build_field_joins, build_filters,
                                    build_join_alias, build_where, get_record_count,
                                    result_page, result_to_dict, query,
                                    ListCriteriaType, valid_selected_rows)
from src.schemas.model import grid_schema
from src.utils.misc import (search_list_of_dict, copy_nested_fields, get_dict)


# run "./shellserver src.shell.sumgroups development.ini" in /home/gvv/Projects/bestida

def run(app):
    session = db_session()

    user = session.query(sqa.get_model("Users")).get(1)

    table_name = "FGStocks"
    info = sqa.get_table_info(table_name)

    except_fields = ["Password", "version"]
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

    groups = None
    sum_fields = None
    if "sumGroups" in info:
        groups = info["sumGroups"]
    if "sum" in info:
        groups += info["sum"]
        sum_fields = info["sum"]

    schema = sqa.get_schema(table_name, 1, remove_duplicate_tables=True)
    scheme = grid_schema(schema, table_name, grid_tables, table_name,
                         except_fields=except_fields,
                         sum_groups=groups,
                         sum_fields=sum_fields
                         )

    include_fields = [#"Company.CompanyId",
                        "SKU.ItemColourFitDim.ItemProduct.Style",
                        "SKU.ItemColourFitDim.Colour.Colour",
                        "SKU.ItemColourFitDim.Fitting.Fitting",
                        "SKU.ItemColourFitDim.Dimension.Dimension",
                        #"SKU.Size.Size",
                        #"Location.ItemWarehouseArea.ItemWarehouse.Warehouse",
                        #"Location.ItemWarehouseArea.Area",
                        #"Location.Location",
                        "OnHand"]

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

    company_ids = [user.Company_Id]
    criteria = []
    criteria_type = ListCriteriaType.ALL
    where = None
    offset = 0
    page_size = 20
    selected_rows = None
    audit = False

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
    #if "sum" in info:
    #    total_records = len(qry.all())
    #else:
    #    total_records = get_record_count(qry)

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
    total = 0
    print(data)
    for d in data:
        row = list()
        total += d["OnHand"]
        for f in include_fields:
            row.append(get_dict(d, f))
        table.append(row)

    print(tabulate(table, headers=header))
    print("Total OnHand:", total)
    print("Total Records:", total_records)

"""
def query(db_session: Session,
          db_table_name: str,
          columns: List[Optional[Dict[str, Any]]],
          where: Optional[str] = None,
          sort: Optional[List[Tuple[str, str, str]]] = None,
          join_tables: Optional[Dict[str, int]] = None,
          joins: Optional[List[Tuple[str, str, str, str, bool]]] = None,
          alias: Optional[Dict[str, Any]] = None):
    ###
    :param db_session:  sqlalchemy.orm.Session
    :param db_table_name: db table name NOT mapper table class name
                        ie: Programs NOT Program
    :param columns:
    # list of dict [{"name": "Id", "label": "Id", "column_label": "Id", "table": "SatDraws", "type": "Integer",
    #               "child_name": "Id", "required": true, "modifiable": false, "sortable": true, "visible": true,
    #               'options': {'sort': True, 'display': 'true', 'sortDirection': 'none'}},
    #               ...]
    :param where: where string
    :param sort: list of tuples [(field_name, direction, alias),..]
        field_name
        direction: asc or desc
        alias
    :param join_tables: joinTable count
            join_tables:  {'Users': 2}
    :param joins: join structure
            joins element: (table, "key", "joinTable", "alias")
            joins:  [('Countries', 'CreateOpId', 'Users', u'Countries_CreateOpId'),
                    ('Countries', 'ModifiedOpId', 'Users', u'Countries_ModifiedOpId')]
    :param alias: join tables alias
        alias: {'Countries_CreateOpId': <AliasedClass at 0x54e1890; User>,
                'Countries_ModifiedOpId': <AliasedClass at 0x54e1050; User>}
    :return: list of db.models record db_table_name instances
        [<gvv.db.models.system.Programs.Program object at 0x7f1d30bf3588>,
        <gvv.db.models.system.Programs.Program object at 0x7f1d30bf3828>]
    ###
    if sort is None:
        sort = list()
    if join_tables is None:
        join_tables = dict()
    if joins is None:
        joins = list()
    if alias is None:
        alias = dict()

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
    else:
        qry = db_session.query(sqa.get_model(db_table_name))
        # session.query(Countries).join(Countries.CreateOpId).order_by(Users.Name)

    for j in joins:
        if join_tables[j[2]] > 1:
            # using alias for this join table
            if j[4]:  # nullable
                qry = qry.outerjoin(alias[j[3]], sqa.instrumented_attr(j[0], j[1]))
            else:
                qry = qry.join(alias[j[3]], sqa.instrumented_attr(j[0], j[1]))
        else:
            if j[4]: # nullable
                qry = qry.outerjoin(sqa.instrumented_attr(j[0], j[1]))
            else:
                qry = qry.join(sqa.instrumented_attr(j[0], j[1]))

    for k, v, al in sort:
        col = k.strip()

        if v == "asc":
            if "." in col:
                tf = col.split(".")
                if join_tables[tf[0]] > 1 and al is not None:
                    # using alias for this join table
                    qry = qry.order_by(asc(sqa.instrumented_attr(al, tf[1])))
                else:
                    qry = qry.order_by(asc(sqa.instrumented_attr(tf[0], tf[1])))
            else:
                qry = qry.order_by(asc(sqa.instrumented_attr(db_table_name, col)))
        else:
            if "." in col:
                tf = col.split(".")
                if join_tables[tf[0]] > 1 and al is not None:
                    # using alias for this join table
                    qry = qry.order_by(desc(sqa.instrumented_attr(al, tf[1])))
                else:
                    qry = qry.order_by(desc(sqa.instrumented_attr(tf[0], tf[1])))
            else:
                qry = qry.order_by(desc(sqa.instrumented_attr(db_table_name, col)))

    if where is not None:
        qry = qry.filter(sqa.where(where, table_name=db_table_name))

    print(qry)
    return qry


def result_to_dict(result: Tuple[Any],
                   columns: List[Dict[str, Any]],
                   except_fields: List[str] = None,
                   index: Optional[int] = None,
                   text_as_string: Optional[bool] = False):

    data = dict()
    if index is not None:
        data["Result_Id"] = index

    field_list = [col for col in columns if col["options"]["display"]]
    for col, value in zip(field_list, result):
        if col in except_fields:
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
            val = val.isoformat() + "Z"  # utc
        elif isinstance(value, (datetime.date, datetime.time)):
            val = val.isoformat()
        elif col["type"] == "Numeric":
            val = str(value)
        elif col["type"] == "Text" and not text_as_string:
            try:
                val = json.loads(value)  # convert to dict if ever
            except:
                try:
                    val = ast.literal_eval(value)  # convert to dict if ever
                except:
                    val = value

        cur[parts[-1]] = val

    return data
"""
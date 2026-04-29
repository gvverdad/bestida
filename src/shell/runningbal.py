import copy
from typing import List, Dict, Optional, Any, Tuple
from tabulate import tabulate

from sqlalchemy import func, asc, desc, case
from sqlalchemy.ext.declarative.api import DeclarativeMeta

from src.db import db_session, sqa
from src.schemas.datasource import (build_sort, build_field_joins, build_filters,
                                    build_join_alias, build_where,
                                    result_page, get_record_count, result_to_dict,
                                    ListCriteriaType, valid_selected_rows)
from src.schemas.model import grid_schema
from src.utils.misc import (search_list_of_dict, copy_nested_fields, get_dict)
from src.schemas.app.product.product import get_product_matrix

# run "./shellserver src.shell.runningbal development.ini" in /home/gvv/Projects/bestida

def run(app):
    session = db_session()

    user = session.query(sqa.get_model("Users")).get(1)

    table_name = "FGStockMovements"
    company_ids = [user.Company_Id]
    product_id = 3
    criteria = list()
    criteria_type = ListCriteriaType.ALL
    where = None
    offset = 0
    page_size = 20
    selected_rows = None
    audit = False

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

    schema = sqa.get_schema(table_name, 1, remove_duplicate_tables=True)
    scheme = grid_schema(schema, table_name, grid_tables, table_name,
                         except_fields=except_fields
                         )

    if "runningBalance" in info and info["runningBalance"] is not None:
        for b in info["runningBalance"]:
            fld = search_list_of_dict(scheme, "name", b)
            if fld:
                rb_fld = copy.deepcopy(fld)
                rb_fld["name"] = f"RunningBalance_{b}"
                rb_fld["label"] = f"RunningBalance {fld['label']}"
                rb_fld["column_label"] = rb_fld["label"]
                rb_fld["sortable"] = False
                rb_fld["searchable"] = False
                scheme.append(rb_fld)

    include_fields = [
                      "FromLocation.ItemWarehouseArea.ItemWarehouse.Warehouse",
                      "SKU.ItemColourFitDim.ItemProduct.Style",
                      "SKU.Size.Size",
                      "Qty",
                      "RunningBalance_Qty",
                      "TotalCost",
                      "RunningBalance_TotalCost",
                      "Type",
                      "Reason.Reason"]

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
    joins, join_tables = build_field_joins(table_name, columns, joins, join_tables)
    filters, joins, join_tables = build_filters(table_name, criteria,
                                                joins, join_tables)
    alias = build_join_alias(joins, join_tables)

    where = build_where(table_name, user.Settings.Timezone, filters,
                        criteria_type, join_tables, alias,
                        user.Company_Id, company_ids,
                        where)

    #qry = db_session.query(sqa.get_model(table_name))
    qry = db_session.query()
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
                srt = asc(sqa.instrumented_attr(table_name, col))
        else:
            if "." in col:
                tf = col.split(".")
                if join_tables[tf[0]] > 1 and al is not None:
                    # using alias for this join table
                    srt = desc(sqa.instrumented_attr(al, tf[1]))
                else:
                    srt = desc(sqa.instrumented_attr(tf[0], tf[1]))
            else:
                srt = desc(sqa.instrumented_attr(table_name, col))
        qry = qry.order_by(srt)
        sorts.append(srt)

    for col in columns:
        if col["options"]["display"]:
            if col["name"].startswith("RunningBalance_"):
                col_name = col["name"].replace("RunningBalance_", "").strip()
                qry = qry.add_columns(
                    func.sum(sqa.get_column(col_name)).over(
                        order_by=[s for s in sorts]
                    ).label(col["name"])
                )
            else:
                col_name = f"{table_name}.{col['name']}"
                qry = qry.add_columns(sqa.get_column(col_name).label(col["name"]))
    """
    if "runningBalance" in info and info["runningBalance"] is not None:
        for b in info["runningBalance"]:
            col_name = f"{table_name}.{b}"
            qry = qry.add_columns(
                func.sum(sqa.get_column(col_name)).over(
                    order_by=[s for s in sorts]
                ).label(f"RunningBalance_{b}")
            )
    """
    if where is not None:
        qry = qry.filter(sqa.where(where, table_name=table_name))


    print(qry)

    #total_records = len(qry.all())
    total_records = get_record_count(qry)
    print(total_records)
    #total_records = get_record_count(qry)
    # handle filter changes
    if total_records < offset:
        offset = 0

    if selected_rows is not None and len(selected_rows) > 0:
        selected_rows = valid_selected_rows(qry, selected_rows)

    recs = result_page(qry, offset, page_size, total_records)
    data = [result_to_dict(r, info, columns, [], index=idx)
                           for idx, r in enumerate(recs)]#
    #data = [r.data_to_dict(except_fields=except_fields)
    #              for r in recs]
    table = list()
    for d in data:
        row = list()
        for f in include_fields:
            row.append(get_dict(d, f))
        table.append(row)

    print()
    print(tabulate(table, headers=header))
    print("Total Records:", total_records)

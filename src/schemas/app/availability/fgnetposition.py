from typing import Optional, Any, List, Dict, Tuple

from sqlalchemy import func, case, asc, desc
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ....db import sqa
from ....cache import cache
from ....db.models.app.fgstocks.FGStocks import FGStock
from ....utils.misc import search_index_list_of_dict
from ....schemas.model import grid_schema
from ....schemas.datasource import (get_record_count, result_page, ListCriteriaType,
                                    build_sort, build_field_joins, build_filters,
                                    build_join_alias, build_where, result_to_dict)
from ....schemas.app.product.product import get_product_matrix


class NetPositionParams(BaseModel):
    CompanyRowId: int   # Company.Id
    ProductId: int   # Product.Id
    ColourId: Optional[int] = None   # Colour.Id
    FittingId: Optional[int] = None  # Fitting.Id
    DimensionId: Optional[int] = None  # Dimension.Id
    ColFitDimId: Optional[int] = None  # ProductColFitDim.Id
    WarehouseIds: Optional[List[int]] = None  # List of Warehouse.Id
    AreaId: Optional[int] = None  # WarehouseArea.Id
    LocationId: Optional[int] = None  # WarehouseLocation.Id

class NetPositionResult(BaseModel):
    NetPosition: List[List[Any]]


def get_netposition(db_session: Session,
                    company_id: int,
                    product_id: int,
                    colfitdim_id: Optional[int] = None,
                    warehouse_ids: Optional[List[int]] = None,
                    area_id: Optional[int] = None,
                    location_id: Optional[int] = None) -> List[List[Any]]:

    try:
        _, sizes = get_product_matrix(db_session, product_id)
    except Exception as err:
        raise Exception(str(err))

    if warehouse_ids is not None:
        # convert list to string with commas for where in clause
        # [1,2,3,4] to 1,2,3,4
        warehouse_ids = ','.join(f"{w}" for w in warehouse_ids)

    positions = list()
    # Header
    header = list()
    header.append("")  # no title
    header.append("Total")
    for s in sizes:
        header.append(s["Size"])
    positions.append(header)

    rec_len = len(header)

    # Stock on Hand
    live_stock = [0] * rec_len
    stock = [0] * rec_len
    stock[0] = "Stock On Hand"

    qry = db_session.query(sqa.get_model("FGStocks"))
    where = f"FGStocks.Company_Id = {company_id} "
    if colfitdim_id is not None:
        where += f"and FGStocks.SKU.ItemColourFitDim_Id = {colfitdim_id} "
        qry = qry.join(sqa.instrumented_attr("FGStocks", "SKU"))
    else:
        where += f"and FGStocks.SKU.ItemColourFitDim.ItemProduct_Id = {product_id} "
        qry = (qry.join(sqa.instrumented_attr("FGStocks", "SKU")).
               join(sqa.instrumented_attr("ProductSKUs", "ItemColourFitDim")))
    if warehouse_ids is not None:
        if location_id is not None:
            where += f"and FGStocks.Location_Id = {location_id} "
        else:
            where += f"and FGStocks.Location.ItemWarehouseArea.ItemWarehouse_Id in ({warehouse_ids}) "
            if area_id is not None:
                where += f"and FGStocks.Location.ItemWarehouseArea_Id = {area_id} "
        qry = (qry.join(sqa.instrumented_attr("FGStocks", "Location")).
               join(sqa.instrumented_attr("WarehouseLocations", "ItemWarehouseArea")))

    records = qry.filter(sqa.where(where)).all()

    live_buckets = [0] * len(sizes)
    buckets = [0] * len(sizes)
    for r in records:
        idx = search_index_list_of_dict(sizes, "Bucket", r.SKU.Size.Bucket)
        if idx == -1:
            continue
        buckets[idx] += r.OnHand
        if r.Location.Status == "Live" and r.Location.Inactive is False:
            live_buckets[idx] += r.OnHand
    stock[1] = sum(buckets)
    for i in range(2, rec_len):
        stock[i] = buckets[i-2]
    positions.append(stock)
    live_stock[1] = sum(live_buckets)
    for i in range(2, rec_len):
        live_stock[i] = live_buckets[i-2]

    # Booked
    booked = [0] * rec_len
    booked[0] = "Booked"

    qry = db_session.query(sqa.get_model("SalesOrders"))
    where = f"SalesOrders.Company_Id = {company_id} "
    if colfitdim_id is not None:
        where += f"and SalesOrders.SKU.ItemColourFitDim_Id = {colfitdim_id} "
        qry = qry.join(sqa.instrumented_attr("SalesOrders", "SKU"))
    else:
        where += f"and SalesOrders.SKU.ItemColourFitDim.ItemProduct_Id = {product_id} "
        qry = (qry.join(sqa.instrumented_attr("SalesOrders", "SKU")).
               join(sqa.instrumented_attr("ProductSKUs", "ItemColourFitDim")))
    if warehouse_ids is not None:
        where += f"and SalesOrders.Warehouse_Id in ({warehouse_ids})"

    records = qry.filter(sqa.where(where)).all()

    buckets = [0] * len(sizes)
    for r in records:
        idx = search_index_list_of_dict(sizes, "Bucket", r.SKU.Size.Bucket)
        if idx == -1:
            continue
        buckets[idx] += r.Orders
    booked[1] = sum(buckets)
    for i in range(2, rec_len):
        booked[i] = buckets[i-2]
    positions.append(booked)

    # Shipped
    shipped = [0] * rec_len
    shipped[0] = "Shipped"

    qry = db_session.query(sqa.get_model("SalesInvoices"))
    where = f"SalesInvoices.Company_Id = {company_id} "
    if colfitdim_id is not None:
        where += f"and SalesInvoices.SKU.ItemColourFitDim_Id = {colfitdim_id} "
        qry = qry.join(sqa.instrumented_attr("SalesInvoices", "SKU"))
    else:
        where += f"and SalesInvoices.SKU.ItemColourFitDim.ItemProduct_Id = {product_id} "
        qry = (qry.join(sqa.instrumented_attr("SalesInvoices", "SKU")).
               join(sqa.instrumented_attr("ProductSKUs", "ItemColourFitDim")))
    if warehouse_ids is not None:
        where += f"and SalesInvoices.Warehouse_Id in ({warehouse_ids})"

    records = qry.filter(sqa.where(where)).all()

    buckets = [0] * len(sizes)
    for r in records:
        idx = search_index_list_of_dict(sizes, "Bucket", r.SKU.Size.Bucket)
        if idx == -1:
            continue
        buckets[idx] += r.Invoices
    shipped[1] = sum(buckets)
    for i in range(2, rec_len):
        shipped[i] = buckets[i-2]
    positions.append(shipped)

    # UnShipped
    unshipped = [0] * rec_len
    unshipped[0] = "UnShipped"
    for i in range(1, rec_len):
        unshipped[i] = booked[i] - shipped[i]
    positions.append(unshipped)

    # Free To Sell
    fts = [0] * rec_len
    fts[0] = "Free To Sell"
    for i in range(1, rec_len):
        fts[i] = stock[i] - booked[i] + shipped[i]
    positions.append(fts)

    # Allocated
    allocated = [0] * rec_len
    allocated[0] = "Allocated"

    qry = db_session.query(sqa.get_model("SalesAllocations"))
    where = f"SalesAllocations.Company_Id = {company_id} "
    if colfitdim_id is not None:
        where += f"and SalesAllocations.SKU.ItemColourFitDim_Id = {colfitdim_id} "
        qry = qry.join(sqa.instrumented_attr("SalesAllocations", "SKU"))
    else:
        where += f" and SalesAllocations.SKU.ItemColourFitDim.ItemProduct_Id = {product_id} "
        qry = (qry.join(sqa.instrumented_attr("SalesAllocations", "SKU")).
               join(sqa.instrumented_attr("ProductSKUs", "ItemColourFitDim")))
    if warehouse_ids is not None:
        where += f"and SalesAllocations.Warehouse_Id in ({warehouse_ids})"

    records = qry.filter(sqa.where(where)).all()

    buckets = [0] * len(sizes)
    for r in records:
        idx = search_index_list_of_dict(sizes, "Bucket", r.SKU.Size.Bucket)
        if idx == -1:
            continue
        buckets[idx] += r.Allocations
    allocated[1] = sum(buckets)
    for i in range(2, rec_len):
        allocated[i] = buckets[i-2]
    positions.append(allocated)

    # Picked
    picked = [0] * rec_len
    picked[0] = "Picked"

    qry = db_session.query(sqa.get_model("SalesPickings"))
    where = f"SalesPickings.Company_Id = {company_id} "
    if colfitdim_id is not None:
        where += f"and SalesPickings.SKU.ItemColourFitDim_Id = {colfitdim_id} "
        qry = qry.join(sqa.instrumented_attr("SalesPickings", "SKU"))
    else:
        where += f"and SalesPickings.SKU.ItemColourFitDim.ItemProduct_Id = {product_id} "
        qry = (qry.join(sqa.instrumented_attr("SalesPickings", "SKU")).
               join(sqa.instrumented_attr("ProductSKUs", "ItemColourFitDim")))
    if warehouse_ids is not None:
        if location_id is not None:
            where += f"and SalesPickings.Location_Id = {location_id}"
        else:
            where += f"and SalesPickings.Location.ItemWarehouseArea.ItemWarehouse_Id in ({warehouse_ids}) "
            if area_id is not None:
                where += f"and SalesPickings.Location.ItemWarehouseArea_Id = {area_id}"
        qry = (qry.join(sqa.instrumented_attr("SalesPickings", "Location")).
               join(sqa.instrumented_attr("WarehouseLocations", "ItemWarehouseArea")))


    records = qry.filter(sqa.where(where)).all()

    buckets = [0] * len(sizes)
    for r in records:
        idx = search_index_list_of_dict(sizes, "Bucket", r.SKU.Size.Bucket)
        if idx == -1:
            continue
        buckets[idx] += r.Pickings
    picked[1] = sum(buckets)
    for i in range(2, rec_len):
        picked[i] = buckets[i-2]
    positions.append(picked)

    # Packed
    packed = [0] * rec_len
    packed[0] = "Packed"

    qry = db_session.query(sqa.get_model("SalesPackings"))
    where = f"SalesPackings.Company_Id = {company_id} "
    if colfitdim_id is not None:
        where += f"and SalesPackings.SKU.ItemColourFitDim_Id = {colfitdim_id} "
        qry = qry.join(sqa.instrumented_attr("SalesPackings", "SKU"))
    else:
        where += f"and SalesPackings.SKU.ItemColourFitDim.ItemProduct_Id = {product_id} "
        qry = (qry.join(sqa.instrumented_attr("SalesPackings", "SKU")).
               join(sqa.instrumented_attr("ProductSKUs", "ItemColourFitDim")))
    if warehouse_ids is not None:
        if location_id is not None:
            where += f"and SalesPackings.Location_Id = {location_id}"
        else:
            where += f"and SalesPackings.Location.ItemWarehouseArea.ItemWarehouse_Id in ({warehouse_ids}) "
            if area_id is not None:
                where += f"and SalesPackings.Location.ItemWarehouseArea_Id = {area_id}"
        qry = (qry.join(sqa.instrumented_attr("SalesPackings", "Location")).
               join(sqa.instrumented_attr("WarehouseLocations", "ItemWarehouseArea")))

    records = qry.filter(sqa.where(where)).all()

    buckets = [0] * len(sizes)
    for r in records:
        idx = search_index_list_of_dict(sizes, "Bucket", r.SKU.Size.Bucket)
        if idx == -1:
            continue
        buckets[idx] += r.Packings
    packed[1] = sum(buckets)
    for i in range(2, rec_len):
        packed[i] = buckets[i-2]
    positions.append(packed)

    # Stock Availability
    sav = [0] * rec_len
    sav[0] = "Stock Availability"
    for i in range(1, rec_len):
        sav[i] = live_stock[i] - allocated[i] - picked[i] - packed[i]
    positions.append(sav)

    # Planned PO
    planned = [0] * rec_len
    planned[0] = "Planned PO"
    positions.append(planned)

    # Outstanding PO
    outstanding = [0] * rec_len
    outstanding[0] = "Outstanding PO"
    positions.append(outstanding)

    # Projected Availability
    projected = [0] * rec_len
    projected[0] = "Projected Availability"
    for i in range(1, rec_len):
        projected[i] = stock[i] + outstanding[i] - booked[i] + shipped[i]
    positions.append(projected)

    return positions

class NetPositionDrillDownSchema(BaseModel):
    TableName: str
    ProductId: int

def get_drilldown_schema(db_session: Session,
                         table_name: str,
                         product_id: int) -> Dict[str, Any]:
    from ....config import config

    cache_grids = False
    if "grids" in config["cache"]:
        cache_grids = config.getboolean("cache", "grids")

    if cache_grids:
        cache_name = f"fgnetposition_drilldown_schema_{table_name}"
        if cache_name in cache:
            return cache[cache_name]

    try:
        _, sizes = get_product_matrix(db_session, product_id)
    except Exception as err:
        raise Exception(str(err))

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
                            viewer=info["viewer"] if "viewer" in info else None,
                            loader=info["loader"] if "loader" in info else None,
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

    schema = sqa.get_schema(table_name, depth=1, remove_duplicate_tables=True)
    scheme = grid_schema(schema, table_name, grid_tables, table_name,
                         except_fields=["Password", "versions"],
                         sum_groups=groups, sum_fields=sum_fields
                         )

    scheme.append(dict(
        name="Total",
        field_name="Total",
        child_name="Total",
        label="Total",
        column_label="Total",
        table=table_name,
        type="Integer",
        length=0,
        decimal=0,
        sortable=False,
        visible=True,
        sticky=True,
        modifiable=False,
        zero_as_blanks=True
    ))
    for idx, s in enumerate(sizes):
        scheme.append(dict(
            name=str(idx),
            field_name=str(idx),
            child_name=str(idx),
            label=s["Size"],
            column_label=s["Size"],
            table=table_name,
            type="Integer",
            length=0,
            decimal=0,
            sortable=False,
            visible=True,
            sticky=True,
            modifiable=False,
            zero_as_blanks=True
        ))

    g_schema = dict(grid_fields=scheme, grid_tables=grid_tables)
    if cache_grids:
        cache[cache_name] = g_schema

    return g_schema

class NetPositionDrillDownParams(NetPositionParams):
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


def get_drilldown_stock(db_session: Session,
                        user_id: int,
                        params: NetPositionDrillDownParams) -> List[Dict[str, Any]]:

    user = db_session.query(sqa.get_model("Users")).get(user_id)

    try:
        _, sizes = get_product_matrix(db_session, params.ProductId)
        # sizes = {Id=SizeBuckets.Id, Bucket=SizeBuckets.Bucket, Size=SizeBuckets.Size}
    except Exception as err:
        raise Exception(str(err))

    col_fit_dim_id = params.ColFitDimId
    if col_fit_dim_id is None and params.ColourId is not None:
        cfd_where = (f"Company_Id = {params.CompanyRowId} and "
                     f"ItemProduct_Id = {params.ProductId} and "
                     f"Colour_Id = {params.ColourId} ")
        if params.FittingId is not None:
            cfd_where += f"and Fitting_Id = {params.FittingId} "
        if params.DimensionId is not None:
            cfd_where += f"and Dimension_Id = {params.DimensionId}"

        col_fit_dim = (db_session.query(sqa.get_model("ProductColourFitDims")).
                        filter(sqa.where(cfd_where)).first())
        if col_fit_dim is not None:
            col_fit_dim_id = col_fit_dim.Id

    warehouse_ids = None
    if params.WarehouseIds is not None:
        # convert list to string with commas for where in clause
        # [1,2,3,4] to 1,2,3,4
        warehouse_ids = ','.join(f"{w}" for w in params.WarehouseIds)

    where = f"FGStocks.Company_Id = {params.CompanyRowId} "
    if col_fit_dim_id is not None:
        where += f"and FGStocks.SKU.ItemColourFitDim_Id = {col_fit_dim_id} "
    else:
        where += f"and FGStocks.SKU.ItemColourFitDim.ItemProduct_Id = {params.ProductId} "
    if warehouse_ids is not None:
        if params.LocationId is not None:
            where += f"and FGStocks.Location_Id = {params.LocationId}"
        else:
            where += f"and FGStocks.Location.ItemWarehouseArea.ItemWarehouse_Id in ({warehouse_ids}) "
            if params.AreaId is not None:
                where += f"and FGStocks.Location.ItemWarehouseArea_Id = {params.AreaId}"

    table_name = "FGStocks"
    info = sqa.get_table_info(table_name)

    sort, joins, join_tables = build_sort(table_name, params.Columns)
    joins, join_tables = build_field_joins(table_name, params.Columns,
                                           joins, join_tables)
    filters, joins, join_tables = build_filters(table_name, params.Criteria,
                                                joins, join_tables)
    alias = build_join_alias(joins, join_tables)
    where = build_where(table_name, user.Settings.Timezone, filters,
                        params.CriteriaType, join_tables, alias, params.CompanyRowId,
                        [params.CompanyRowId],
                        where)

    # pivot table
    qry = db_session.query()
    for col in params.Columns:
        if col["name"] == "Total" or (col["name"] >= "0" and col["name"] <= "99"):
            continue
        if col["options"]["display"]:
            col_name = f"{table_name}.{col['name']}"
            qry = qry.add_columns(sqa.get_column(col_name).label(col["name"]))
            qry = qry.group_by(sqa.get_column(col_name))
            qry = qry.order_by(sqa.get_column(col_name))

    qry = qry.add_columns(func.sum(sqa.get_column("FGStocks.OnHand")).
                          label("Total"))

    for idx, sb in enumerate(sizes):
        qry = qry.add_columns(
              func.sum(
                case([(sqa.get_column("FGStocks.SKU.Size_Id") == sb["Id"],
                       sqa.get_column("FGStocks.OnHand"))], else_=0)
              ).label(str(idx)))

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
                qry = qry.order_by(asc(sqa.instrumented_attr(table_name, col)))
        else:
            if "." in col:
                tf = col.split(".")
                if join_tables[tf[0]] > 1 and al is not None:
                    # using alias for this join table
                    qry = qry.order_by(desc(sqa.instrumented_attr(al, tf[1])))
                else:
                    qry = qry.order_by(desc(sqa.instrumented_attr(tf[0], tf[1])))
            else:
                qry = qry.order_by(desc(sqa.instrumented_attr(table_name, col)))

    if where is not None:
        qry = qry.filter(sqa.where(where, table_name=table_name))

    total_records = len(qry.all())
    # handle filter changes
    offset = params.Offset
    if total_records < offset:
        offset = 0

    recs = result_page(qry, offset, params.PageSize, total_records)
    # <class 'sqlalchemy.util._collections.result'>
    data = [result_to_dict(r, info, params.Columns, [], index=idx)
                           for idx, r in enumerate(recs)]
    return data


class NetPositionSalesOrderParams(NetPositionDrillDownParams):
    Status: str

def get_drilldown_salesorder(db_session: Session,
                             company_id: int,
                             product_id: int,
                             status: str,
                             colfitdim_id: Optional[int] = None,
                             warehouse_ids: Optional[List[int]] = None,
                             offset: int = 0,
                             page_size: int = 20) -> Tuple[List[Dict[str, Any]], int]:

    try:
        _, sizes = get_product_matrix(db_session, product_id)
    except Exception as err:
        raise Exception(str(err))

    if warehouse_ids is not None:
        # convert list to string with commas for where in clause
        # [1,2,3,4] to 1,2,3,4
        warehouse_ids = ','.join(f"{w}" for w in warehouse_ids)

    if status == "Booked":
        order_status = '"Open","Allocated","Picked","Packed","Despatched"'
    elif status == "Shipped":
        order_status = '"Despatched"'
    elif status == "UnShipped":
        order_status = '"Open","Allocated","Picked","Packed"'
    elif status == "Allocated":
        order_status = '"Allocated"'
    elif status == "Picked":
        order_status = '"Picked"'
    elif status == "Packed":
        order_status = '"Packed"'
    else:
        raise Exception(f"Invalid Status: {status}")
    # convert list to string with commas for where in clause
    # ["Open","Allocated","Picked","Packed"] to "Open","Allocated","Picked","Packed"
    #order_statuses = ','.join(f'"{s}"' for s in order_status)

    # Sales Order Details
    qry = db_session.query(sqa.get_model("SalesOrderDetails"))
    where = (f"SalesOrderDetails.Company_Id = {company_id} and "
             f"SalesOrderDetails.Status in ({order_status}) ")
    if colfitdim_id is not None:
        where += f"and SalesOrderDetails.Product_Id = {colfitdim_id} "
    else:
        where += f"and SalesOrderDetails.Product.ItemProduct_Id = {product_id} "
        qry = qry.join(sqa.instrumented_attr("SalesOrderDetails", "Product"))
    if warehouse_ids is not None:
        where += f"and SalesOrderDetails.Warehouse_Id in ({warehouse_ids})"

    qry = (qry.filter(sqa.where(where)).
           join(sqa.instrumented_attr("SalesOrderDetails", "ItemSalesOrderHeader")).
           order_by(sqa.sort_asc("SalesOrderHeaders", "OrderNumber")).
           order_by(sqa.sort_asc("SalesOrderDetails", "Line")))

    total_records = get_record_count(qry)
    # handle filter changes
    if total_records < offset:
        offset = 0
    records = result_page(qry, offset, page_size, total_records)

    data = list()
    for line in records:
        buckets = [0] * len(sizes)
        for siz in line.Sizes:
            idx = search_index_list_of_dict(sizes, "Bucket", siz.SKU.Size.Bucket)
            if idx == -1:
                continue
            buckets[idx] += siz.Units
        r = line.data_to_dict(except_fields=["Password", "versions"])
        r["Total"] = sum(buckets)
        for idx, s in enumerate(buckets):
            r[str(idx)] = s
        data.append(r)
    return data, total_records

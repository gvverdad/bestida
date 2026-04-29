import logging, decimal

from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ........db import sqa
from ........db.models.security.Users import User as DBUser
from ........security.policy import get_current_user
from ........schemas.datasource import (CUDStatus,ListGridParams, ListResult)
from ........schemas.model import GridSchema, GridTable, GridField, FormField
from ........utils.misc import search_list_of_dict

from ........schemas.app.stock.fgstock import (SAParams, fg_stock_adjustment)
from ........schemas.app.availability.fgavailability import (fg_stock_availability,
                                                             fg_location_stock_availability)

log = logging.getLogger(__name__)

router = APIRouter()

@router.get("/productstockadjgridschema", response_model=GridSchema, tags=["productstock"])
def get_product_stockadj_grid_schema(current_user_id: DBUser = Depends(get_current_user)):

    dummy_table = "StockAdjustmentSizes"

    grid_tables = list()
    grid_tables.append(GridTable.model_validate(dict(
        table=dummy_table,
        label="Sizes",
        documents=[
            dict(program="DocumentFGNetPosition",
                 title="Net Position",
                 params=dict(style="Style.Style",
                             colour="Colour.Colour",
                             fitting="Fitting.Fitting",
                             dimension="Dimension.Dimension",
                             warehouse="Warehouse.Warehouse",
                             area="Area.Area",
                             location="Location.Location"))
        ]
    )))

    grid_fields = list()
    # Datatable RowId = ProductSKU Id
    grid_fields.append(GridField.model_validate(dict(
        name="Id",
        label="Id",
        table=dummy_table,
        field_name="Id",
        type="Integer",
        length=0,
        column_label="Id",
        child_name="Is",
        sortable=False,
        searchable=False,
        draggable=False,
        visible=False
    )))

    grid_fields.append(GridField.model_validate(dict(
        name="Size",
        label="Size",
        table=dummy_table,
        field_name="Size",
        type="String",
        length=16,
        column_label="Size",
        child_name="Size",
        sortable=False,
        searchable=False,
        draggable=False,
        visible=True
    )))
    grid_fields.append(GridField.model_validate(dict(
        name="WhsAvail",
        label="Warehouse Availability",
        table=dummy_table,
        field_name="WhsAvail",
        type="Integer",
        length=0,
        column_label="Warehouse Availability",
        child_name="WhsAvail",
        sortable=False,
        searchable=False,
        draggable=False,
        visible=True
    )))
    grid_fields.append(GridField.model_validate(dict(
        name="LocSOH",
        label="Location Stock",
        table=dummy_table,
        field_name="LocSOH",
        type="Integer",
        length=0,
        column_label="Location Stock",
        child_name="LocSOH",
        sortable=False,
        searchable=False,
        draggable=False,
        visible=True
    )))
    grid_fields.append(GridField.model_validate(dict(
        name="LocPick",
        label="Location Picks",
        table=dummy_table,
        field_name="LocPick",
        type="Integer",
        length=0,
        column_label="Location Picks",
        child_name="LocPick",
        sortable=False,
        searchable=False,
        draggable=False,
        visible=True
    )))
    grid_fields.append(GridField.model_validate(dict(
        name="LocPack",
        label="Location Packs",
        table=dummy_table,
        field_name="LocPack",
        type="Integer",
        length=0,
        column_label="Location Packs",
        child_name="LocPack",
        sortable=False,
        searchable=False,
        draggable=False,
        visible=True
    )))
    grid_fields.append(GridField.model_validate(dict(
        name="LocAvail",
        label="Location Availability",
        table=dummy_table,
        field_name="LocAvail",
        type="Integer",
        length=0,
        column_label="Location Availability",
        child_name="LocAvail",
        sortable=False,
        searchable=False,
        draggable=False,
        visible=True
    )))
    grid_fields.append(GridField.model_validate(dict(
        name="AdjQty",
        label="Adjustment",
        table=dummy_table,
        field_name="Adj",
        type="Integer",
        length=0,
        column_label="Adjustment",
        child_name="Adjustment",
        sortable=False,
        searchable=False,
        draggable=False,
        visible=True,
        modifiable=True
    )))

    return GridSchema.model_validate(dict(
        grid_fields=grid_fields,
        grid_tables=grid_tables
    ))


@router.post("/productstockadjgriddata", response_model=ListResult, tags=["productstock"])
def get_product_stockadj_grid_data(params: ListGridParams,
                      current_user_id: DBUser = Depends(get_current_user)):

    user = db.session.query(sqa.get_model("Users")).get(current_user_id)

    records = list()
    dummy_table = "StockAdjustmentSizes"

    style = search_list_of_dict(params.Criteria,"field", "Style")
    if style is not None:
        col = search_list_of_dict(params.Criteria, "field", "Colour")
        fit = search_list_of_dict(params.Criteria, "field", "Fitting")
        dim = search_list_of_dict(params.Criteria, "field", "Dimension")
        cfd_where = (f"Company_Id = {params.CompanyRowId} and "
                     f"ItemProduct_Id = {style['value']['Id']} and "
                     f"Colour_Id = {col['value']['Id']} ")
        if fit is not None:
            cfd_where += f"and Fitting_Id = {fit['value']['Id']} "
        if dim is not None:
            cfd_where += f"and Dimension_Id = {dim['value']['Id']}"

        col_fit_dim = (db.session.query(sqa.get_model("ProductColourFitDims")).
                     filter(sqa.where(cfd_where)).first())
        if col_fit_dim is not None:
            whs = search_list_of_dict(params.Criteria, "field", "Warehouse")
            loc = search_list_of_dict(params.Criteria, "field", "Location")

            warehouse = (db.session.query(sqa.get_model("Warehouses")).
                         get(whs["value"]["Id"]))

            location = (db.session.query(sqa.get_model("WarehouseLocations")).
                         get(loc["value"]["Id"]))

            sorted_data = sorted(col_fit_dim.Sizes, key=lambda x: x.Size.Bucket)
            for sku in sorted_data:
                _, _, _, _, whs_avail = fg_stock_availability(db.session,
                                                              params.CompanyRowId,
                                                              warehouse.Id,
                                                              sku.Id)

                soh, _, pick, pack, avail = fg_location_stock_availability(db.session,
                                                                           params.CompanyRowId,
                                                                           location.Id,
                                                                           sku.Id)
                records.append(dict(Id=sku.Id,
                                    Size=sku.Size.Size,
                                    WhsAvail=whs_avail,
                                    LocSOH=soh,
                                    LocPick=pick,
                                    LocPack=pack,
                                    LocAvail=avail,
                                    AdjQty=FormField.model_validate(dict(
                                        name=f"AdjQty_{sku.Id}",
                                        field_name=f"AdjQty_{sku.Id}",
                                        label="",
                                        type="Integer",
                                        table=dummy_table,
                                        modifiable=True
                                    ))
                ))

    return ListResult.model_validate(dict(
        recordsTotal=len(records),
        data=records
    ))


@router.post("/fgstockadjustments", response_model=CUDStatus, tags=["productstock"])
def post_product_stockadj(params: SAParams,
                          current_user_id: DBUser = Depends(get_current_user)):

    try:
        message = fg_stock_adjustment(db.session,
                                      current_user_id,
                                      params)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

    return dict(success=True, message=message, RecordRowId=0)

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from ........db import sqa
from ........db.models.security.Users import User as DBUser
from ........security.policy import get_current_user
from ........schemas.model import GridSchema
from ........schemas.datasource import ListResult
from ........schemas.app.availability.fgnetposition import (NetPositionParams,
                                                            NetPositionResult,
                                                            NetPositionDrillDownSchema,
                                                            NetPositionDrillDownParams,
                                                            NetPositionSalesOrderParams,
                                                            get_netposition,
                                                            get_drilldown_schema,
                                                            get_drilldown_stock,
                                                            get_drilldown_salesorder)

log = logging.getLogger(__name__)

router = APIRouter()


# You cannot send a request body using a GET operation (HTTP method).
# To send data, you have to use one of: POST (the more common), PUT, DELETE or PATCH.
@router.post("/fgNetPosition", response_model=NetPositionResult, tags=["availability"])
def get_fg_net_position(params: NetPositionParams,
                        current_user_id: DBUser = Depends(get_current_user)):

    col_fit_dim_id = params.ColFitDimId
    if col_fit_dim_id is None and params.ColourId is not None:
        cfd_where = (f"Company_Id = {params.CompanyRowId} and "
                     f"ItemProduct_Id = {params.ProductId} and "
                     f"Colour_Id = {params.ColourId} ")
        if params.FittingId is not None:
            cfd_where += f"and Fitting_Id = {params.FittingId} "
        if params.DimensionId is not None:
            cfd_where += f"and Dimension_Id = {params.DimensionId}"

        col_fit_dim = (db.session.query(sqa.get_model("ProductColourFitDims")).
                        filter(sqa.where(cfd_where)).first())
        if col_fit_dim is not None:
            col_fit_dim_id = col_fit_dim.Id

    try:
        net_position = get_netposition(db.session,
                                       params.CompanyRowId,
                                       params.ProductId,
                                       col_fit_dim_id,
                                       params.WarehouseIds,
                                       params.AreaId,
                                       params.LocationId)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

    return NetPositionResult.model_validate(dict(NetPosition=net_position))


@router.post("/fgDrillDownSchema", response_model=GridSchema, tags=["availability"])
def get_drill_down_schema(params: NetPositionDrillDownSchema,
                          current_user_id: DBUser = Depends(get_current_user)):
    try:
        return get_drilldown_schema(db.session,
                                    params.TableName,
                                    params.ProductId)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/fgDrillDownStock", response_model=ListResult, tags=["availability"])
def get_netposition_soh_data(params: NetPositionDrillDownParams,
                             current_user_id: DBUser = Depends(get_current_user)):

    try:
        stock = get_drilldown_stock(db.session, current_user_id, params)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

    return dict(draw=1, data=stock, recordsTotal=len(stock))


@router.post("/fgDrillDownSalesOrder", response_model=ListResult, tags=["availability"])
def get_netposition_so_data(params: NetPositionSalesOrderParams,
                            current_user_id: DBUser = Depends(get_current_user)):

    col_fit_dim_id = None
    if params.ColourId is not None:
        cfd_where = (f"Company_Id = {params.CompanyRowId} and "
                     f"ItemProduct_Id = {params.ProductId} and "
                     f"Colour_Id = {params.ColourId} ")
        if params.FittingId is not None:
            cfd_where += f"and Fitting_Id = {params.FittingId} "
        if params.DimensionId is not None:
            cfd_where += f"and Dimension_Id = {params.DimensionId}"

        col_fit_dim = (db.session.query(sqa.get_model("ProductColourFitDims")).
                        filter(sqa.where(cfd_where)).first())
        if col_fit_dim is not None:
            col_fit_dim_id = col_fit_dim.Id

    try:
        orders, total_records = get_drilldown_salesorder(db.session,
                                                         params.CompanyRowId,
                                                         params.ProductId,
                                                         params.Status,
                                                         col_fit_dim_id,
                                                         params.WarehouseIds,
                                                         params.Offset,
                                                         params.PageSize)

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))

    return dict(draw=1, data=orders, recordsTotal=total_records)

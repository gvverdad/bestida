from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session
from pydantic import BaseModel

from ....db import sqa
from ....schemas.datasource import ListCriteriaType
from ..availability.fgavailability import fg_location_stock_availability, fg_stock_availability

class SAParams(BaseModel):
    CompanyRowId: Optional[int] = None
    Locale: Optional[str] = None
    Timezone: Optional[str] = None
    Data: Dict[str, Any]

def fg_stock_adjustment(db_session: Session,
                        user_id: int,
                        params: SAParams) -> str:

    user = db_session.query(sqa.get_model("Users")).get(user_id)
    if user is None:
        raise Exception(f"Invalid User.Id: {user_id}")

    if params.CompanyRowId is None:
        coy_id = user.Company_Id
    else:
        coy_id = params.CompanyRowId
    company = db_session.query(sqa.get_model("Companies")).get(coy_id)
    if company is None:
        raise Exception(f"Invalid Company.Id: {coy_id}")

    row_id = params.Data["Location"]["Id"]
    location = db_session.query(sqa.get_model("WarehouseLocations")).get(row_id)
    if location is None:
        raise Exception(f"Invalid WarehouseLocation.Id: {row_id}")

    row_id = params.Data["Reason"]["Id"]
    reason = db_session.query(sqa.get_model("FGStockAdjustmentReasons")).get(row_id)
    if reason is None:
        raise Exception(f"Invalid FGStockAdjustmentReasons.Id: {row_id}")

    cfd_where = (f"Company_Id = {coy_id} and "
                 f"ItemProduct_Id = {params.Data['Style']['Id']} and "
                 f"Colour_Id = {params.Data['Colour']['Id']} ")
    if params.Data['Fitting']:
        cfd_where += f"and Fitting_Id = {params.Data['Fitting']['Id']} "
    if params.Data['Dimension']:
        cfd_where += f"and Dimension_Id = {params.Data['Dimension']['Id']}"

    col_fit_dim = (db_session.query(sqa.get_model("ProductColourFitDims")).
                   filter(sqa.where(cfd_where)).
                   first())
    if col_fit_dim is None:
        raise Exception(f"Invalid ProductColourFitDims: {cfd_where}")

    is_ok = False
    for size in col_fit_dim.Sizes:
        name = "AdjQty_" + str(size.Id)
        if name not in params.Data:
            continue

        qty = params.Data[name]
        if qty == 0 and params.Data["AdjustmentType"] == "Adjustment":
            continue

        # validate location stock adjustment beyond minimum value
        soh_qty, _, _, _, avail_qty = fg_location_stock_availability(db_session,
                                                                     company.Id,
                                                                     location.Id,
                                                                     size.Id)

        min_qty = soh_qty - avail_qty
        if params.Data["AdjustmentType"] == "Replacement":
            if qty < 0:
                raise Exception((f"Size {size.Size.Size} Replacement Qty of {qty} "
                                 f"will result in Negative Location Stock"))
            elif qty < min_qty:
                raise Exception((f"Size {size.Size.Size} Replacement Qty of {qty} "
                                 f"is less than Minimum Qty of {min_qty} for Location"))
        else:  # Adjustment
            if (soh_qty + qty) < 0:
                raise Exception((f"Size {size.Size.Size} Adjustment Qty of {qty} "
                                 f"will result in Negative Location Stock"))
            elif (soh_qty + qty) < min_qty:
                raise Exception((f"Size {size.Size.Size} Adjustment Qty of {qty} "
                                 f"will result in Stock less than Minimum Qty of {min_qty} for Location"))

        # validate warehouse stock adjustment beyond minimum value
        soh_qty, _, _, _, avail_qty = fg_stock_availability(db_session,
                                                            company.Id,
                                                            location.ItemWarehouseArea.ItemWarehouse_Id,
                                                            size.Id)
        min_qty = soh_qty - avail_qty
        if params.Data["AdjustmentType"] == "Replacement":
            if qty < 0:
                raise Exception((f"Size {size.Size.Size} Replacement Qty of {qty} "
                                 f"will result in Negative Warehouse Stock"))
            elif qty < min_qty:
                raise Exception((f"Size {size.Size.Size} Replacement Qty of {qty} "
                                 f"is less than Minimum Qty of {min_qty} for Warehouse"))
        else:  # Adjustment
            if (soh_qty + qty) < 0:
                raise Exception((f"Size {size.Size.Size} Adjustment Qty of {qty} "
                                 f"will result in Negative Warehouse Stock"))
            elif (soh_qty + qty) < min_qty:
                raise Exception((f"Size {size.Size.Size} Adjustment Qty of {qty} "
                                 f"will result in Stock less than Minimum Qty of {min_qty} for Warehouse"))

        is_ok = True

        movement = sqa.get_model("FGStockMovements")()
        movement.Company = company
        movement.SKU = size
        movement.FromLocation = location
        movement.Qty = qty
        # TODO: apply cost
        movement.Type = "Adjustment"
        movement.AdjustmentType = params.Data["AdjustmentType"]
        movement.Reason = reason
        if "Comments" in params.Data:
            movement.Comments = params.Data["Comments"]
        if "Reference" in params.Data:
            movement.Reference = params.Data["Reference"]
        if "Document" in params.Data:
            movement.Document = params.Data["Document"]

        db_session.add(movement)

    if is_ok:
        try:
            db_session.commit()
        except Exception as err:
            raise Exception(f"schemas.app.stock.fgstock.fg_stock_adjustment commit Error: {str(err)}")

    return "FG Stock Adjustment Posted" if is_ok else "Nothing to Adjust"


class GetStockMovementsParams(BaseModel):
    Depth: int = 1
    CompanyRowId: Optional[int] = None
    Locale: Optional[str] = None
    Timezone: Optional[str] = None
    ParentRow: Optional[Dict[str, Any]] = None
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
    ChoicesAsTuple: bool = True
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
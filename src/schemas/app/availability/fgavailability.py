from sqlalchemy.orm import Session
from typing import Tuple

from ....db import sqa


def fg_stock_on_hand(db_session: Session,
                     company_id: int,
                     warehouse_id: int,
                     sku_id: int) -> int:
    units = 0
    where = (f"FGStocks.Company_Id = {company_id} and "
             f"FGStocks.SKU_Id = {sku_id} and "             
             f"FGStocks.Location.Status = \"Live\" and "
             f"FGStocks.Location.Inactive = False and "
             f"FGStocks.Location.ItemWarehouseArea.ItemWarehouse_Id = {warehouse_id}")
    soh = (db_session.query(sqa.get_model("FGStocks")).
           filter(sqa.where(where)).
           join(sqa.instrumented_attr("FGStocks", "Location")).
           join(sqa.instrumented_attr("WarehouseLocations", "ItemWarehouseArea")).
           all())
    for stock in soh:
        units += stock.OnHand
    return units


def fg_allocation(db_session: Session,
                  company_id: int,
                  warehouse_id: int,
                  sku_id: int) -> int:
    units = 0
    where = (f"SalesAllocations.Company_Id = {company_id} and "
             f"SalesAllocations.Warehouse_Id = {warehouse_id} and "
             f"SalesAllocations.SKU_Id = {sku_id} and "
             f"SalesAllocations.Warehouse.Status = \"Live\" and "
             f"SalesAllocations.Warehouse.Inactive = False")
    sales_allo = (db_session.query(sqa.get_model("SalesAllocations")).
                  filter(sqa.where(where)).
                  join(sqa.instrumented_attr("SalesAllocations", "Warehouse")).
                  first())
    if sales_allo is not None:
        units += sales_allo.Allocations
    return units


def fg_picking(db_session: Session,
               company_id: int,
               warehouse_id: int,
               sku_id: int) -> int:
    units = 0
    where = (f"SalesPickings.Company_Id = {company_id} and "
             f"SalesPickings.SKU_Id = {sku_id} and "
             f"SalesPickings.Location.Status = \"Live\" and "
             f"SalesPickings.Location.Inactive = False and "             
             f"SalesPickings.Location.ItemWarehouseArea.ItemWarehouse_Id = {warehouse_id}")
    picks = (db_session.query(sqa.get_model("SalesPickings")).
             filter(sqa.where(where)).
             join(sqa.instrumented_attr("SalesPickings", "Location")).
             join(sqa.instrumented_attr("WarehouseLocations", "ItemWarehouseArea")).
             all())
    for pick in picks:
        units += pick.Pickings
    return units


def fg_packing(db_session: Session,
               company_id: int,
               warehouse_id: int,
               sku_id: int) -> int:
    units = 0
    where = (f"SalesPackings.Company_Id = {company_id} and "
             f"SalesPackings.SKU_Id = {sku_id} and "
             f"SalesPackings.Location.Status = \"Live\" and "
             f"SalesPackings.Location.Inactive = False and "                          
             f"SalesPackings.Location.ItemWarehouseArea.ItemWarehouse_Id = {warehouse_id}")
    packs = (db_session.query(sqa.get_model("SalesPackings")).
             filter(sqa.where(where)).
             join(sqa.instrumented_attr("SalesPackings", "Location")).
             join(sqa.instrumented_attr("WarehouseLocations", "ItemWarehouseArea")).
             all())
    for pack in packs:
        units += pack.Packings
    return units


def fg_stock_availability(db_session: Session,
                          company_id: int,
                          warehouse_id: int,
                          sku_id: int) -> Tuple[int, int, int, int, int]:

    soh = fg_stock_on_hand(db_session, company_id, warehouse_id, sku_id)
    allo = fg_allocation(db_session, company_id, warehouse_id, sku_id)
    pick = fg_picking(db_session, company_id, warehouse_id, sku_id)
    pack = fg_packing(db_session, company_id, warehouse_id, sku_id)

    avail = soh - allo - pick - pack

    return soh, allo, pick, pack, avail


def fg_location_stock_on_hand(db_session: Session,
                              company_id: int,
                              location_id: int,
                              sku_id: int) -> int:
    units = 0
    where = (f"FGStocks.Company_Id = {company_id} and "
             f"FGStocks.SKU_Id = {sku_id} and "
             f"FGStocks.Location_Id = {location_id} and "
             f"FGStocks.Location.Status = \"Live\" and "
             f"FGStocks.Location.Inactive = False")
    soh = (db_session.query(sqa.get_model("FGStocks")).
           filter(sqa.where(where)).
           join(sqa.instrumented_attr("FGStocks", "Location")).
           all())
    for stock in soh:
        units += stock.OnHand
    return units


def fg_location_picking(db_session: Session,
                        company_id: int,
                        location_id: int,
                        sku_id: int) -> int:
    units = 0
    where = (f"SalesPickings.Company_Id = {company_id} and "
             f"SalesPickings.SKU_Id = {sku_id} and "
             f"SalesPickings.Location_Id = {location_id} and "
             f"SalesPickings.Location.Status = \"Live\" and "
             f"SalesPickings.Location.Inactive = False")
    picks = (db_session.query(sqa.get_model("SalesPickings")).
             filter(sqa.where(where)).
             join(sqa.instrumented_attr("SalesPickings", "Location")).
             all())
    for pick in picks:
        units += pick.Pickings
    return units


def fg_location_packing(db_session: Session,
                        company_id: int,
                        location_id: int,
                        sku_id: int) -> int:
    units = 0
    where = (f"SalesPackings.Company_Id = {company_id} and "
             f"SalesPackings.SKU_Id = {sku_id} and "
             f"SalesPackings.Location_Id = {location_id} and "
             f"SalesPackings.Location.Status = \"Live\" and "
             f"SalesPackings.Location.Inactive = False")
    packs = (db_session.query(sqa.get_model("SalesPackings")).
             filter(sqa.where(where)).
             join(sqa.instrumented_attr("SalesPackings", "Location")).
             all())
    for pack in packs:
        units += pack.Packings
    return units


def fg_location_stock_availability(db_session: Session,
                                   company_id: int,
                                   location_id: int,
                                   sku_id: int) -> Tuple[int, int, int, int, int]:
    soh = fg_location_stock_on_hand(db_session, company_id, location_id, sku_id)
    allo = 0
    # TODO: what about SalesAllocations, SalesAllocation is at the Warehouse Level Only
    pick = fg_location_picking(db_session, company_id, location_id, sku_id)
    pack = fg_location_packing(db_session, company_id, location_id, sku_id)

    avail = soh - allo - pick - pack

    return soh, allo, pick, pack, avail

from decimal import Decimal
from datetime import date, datetime
from typing import Optional, Tuple, Dict, Any

from sqlalchemy.orm import Session
from pydantic import BaseModel

from ....db import sqa
from ....db.models.app.products.ProductSKUs import ProductSKU as DBProductSKU
from ....db.models.app.products.ProductSeasons import ProductSeason as DBProductSeason
from ....db.models.app.customers.CustomerWarehouses import CustomerWarehouse as DBCustomerWarehouse
from ....db.models.app.warehouses.Warehouses import Warehouse as DBWarehouse
from ....db.models.app.salesorders.SalesOrderSources import SalesOrderSource as DBSalesOrderSource
from ....db.models.company.Companies import Company as DBCompany
from ..customer.customer import get_customer_data
from ..account.tax import get_salestax
from ....utils.misc import search_list_of_dict


class PriceKey(BaseModel):
    CompanyId: int
    SKUId: int
    CustomerId: int
    StartDate: date
    CancelDate: date
    TradeDiscountPercentage: Decimal = 0
    Volume: int = 0
    StoreId: Optional[int] = None
    DeliverViaId: Optional[int] = None
    SeasonYearId: Optional[int] = None
    ShipWarehouseId: Optional[int] = None
    OrderSourceId: Optional[int] = None


class PriceResult(BaseModel):
    PriceEx: Decimal
    PriceInc: Decimal
    SalesTax: Decimal
    SalesTaxRate: Decimal
    DiscountPercentage: Decimal
    PriceSource: str
    PriceParams: str
    PriceSourceKey: str
    DiscountSourceKey: str


def get_product_price(db_session: Session,
                      company_id: int,
                      sku_id: int,
                      customer_id: int,
                      start_date: date,
                      cancel_date: date,
                      trade_discount_percentage: Decimal = 0,
                      volume: int = 0,
                      store_id: Optional[int] = None,
                      deliver_via_id: Optional[int] = None,
                      season_year_id: Optional[int] = None,
                      ship_warehouse_id: Optional[int] = None,
                      order_source_id: Optional[int] = None) \
        -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal, str, str, str, str]:

    company = db_session.query(sqa.get_model("Companies")).get(company_id)
    if company is None:
        raise Exception(f"Invalid company_id: {company_id}")

    sku = db_session.query(sqa.get_model("ProductSKUs")).get(sku_id)
    if sku is None:
        raise Exception(f"Invalid sku_id: {sku_id}")
    
    style_id = sku.ItemColourFitDim.ItemProduct_Id
    col_fit_dim_id = sku.ItemColourFitDim_Id

    try:
        customer = get_customer_data(db_session, customer_id, store_id)
    except Exception as err:
        raise Exception(str(err))
    currency_code = customer["CustomerAccount"]["Currency"][0]

    sales_group = customer["ProcessingGroups"]["SalesGroups"]
    price_type = "SELL"
    price_date = start_date
    if sales_group:
        rrp = search_list_of_dict(sales_group, "Group", "RRPPRICE")
        if rrp is not None:
            price_type = "RRP"
        sell = search_list_of_dict(sales_group, "Group", "SELLPRICE")
        if sell is not None:
            price_type = "SELL"

        cancel = search_list_of_dict(sales_group, "Group", "CANCELDATE")
        if cancel is not None:
            price_date = cancel_date
        start = search_list_of_dict(sales_group, "Group", "STARTDATE")
        if start is not None:
            price_date = start_date

    deliver_via = None
    if deliver_via_id:
        deliver_via = db_session.query(sqa.get_model("CustomerWarehouses")).get(deliver_via_id)

    warehouse = None
    if ship_warehouse_id:
        warehouse = db_session.query(sqa.get_model("Warehouses")).get(ship_warehouse_id)

    order_source = None
    if order_source_id:
        order_source = db_session.query(sqa.get_model("SalesOrderSources")).get(order_source_id)

    season = None
    if season_year_id:
        season = db_session.query(sqa.get_model("ProductSeasons")).get(season_year_id)

    # expand params
    if sku.ItemColourFitDim.Dimension:
        col_fit_dim = (f"{sku.ItemColourFitDim.Colour.Colour} "
                       f"{sku.ItemColourFitDim.Fitting.Fitting} "
                       f"{sku.ItemColourFitDim.Dimension.Dimension}").strip()
    elif sku.ItemColourFitDim.Fitting:
        col_fit_dim = (f"{sku.ItemColourFitDim.Colour.Colour} "
                       f"{sku.ItemColourFitDim.Fitting.Fitting}").strip()
    else:
        col_fit_dim = f"{sku.ItemColourFitDim.Colour.Colour}".strip()

    params = (f"Company: {company.Name}, "
              f"Customer: {customer['Account'] if 'Account' in customer else customer['ItemCustomer']['Account']}, "
              f"DeliverVia: {deliver_via.Warehouse if deliver_via else None}, "
              f"Store: {customer['Store'] if 'Store' in customer else None}, "
              f"Currency: {currency_code}, "              
              f"Band: {customer['PriceBand']['Band'] if 'PriceBand' in customer else None}, "
              f"Style: {sku.ItemColourFitDim.ItemProduct.Style}, "
              f"ColFitDim: {col_fit_dim}, "
              f"Size: {sku.Size.Size}, "
              f"Volume: {volume}, "
              f"TradeDiscount%: {trade_discount_percentage}, "
              f"Date: {price_date:%Y-%m-%d}, "
              f"PriceType: {price_type}, "
              f"Season: {season.Season if season else None}, "
              f"ShipWarehouse: {warehouse.Warehouse if warehouse else None}, "
              f"OrderSource: {order_source.Source if order_source else None}")

    where = ""
    discount_where = ""
    price_source = ""
    price_ex = 0.0
    discount = 0.0
    contract_price_found = False
    # 1. Get Contract Price/Discount
    if price_type == "SELL":
        price_ex, discount, where = get_contract_price_discount(db_session,
                                                                company,
                                                                customer,
                                                                sku,
                                                                price_date,
                                                                volume,
                                                                deliver_via,
                                                                warehouse,
                                                                order_source
                                                                )
        if price_ex > 0:
            price_source = "ContractPrice"
            contract_price_found = True
        if discount > 0:
            discount_where = where

    # 2. Get PriceList or Price
    if price_ex == 0:
        # 2.1 PriceBand
        if customer["PriceBand_Id"] is not None:
            price_band_id = customer["PriceBand_Id"]
            # Style/ColFitDim/Size
            where = (f"Company_Id = {company_id} and Band_Id = {price_band_id} and "
                     f"Style_Id = {style_id} and ColFitDim_Id = {col_fit_dim_id} and "
                     f"SKU_Id = {sku_id} and Currency = \"{currency_code}\" and "
                     f"Type = \"{price_type}\" and EffectiveFrom <= {price_date:%Y-%m-%d} and "
                     f"EffectiveTo >= {price_date:%Y-%m-%d}")
            # get last record by EffectiveFrom Date
            price_band = db_session.query(sqa.get_model("PriceBands")).\
                filter(sqa.where(where)).\
                order_by(sqa.sort_desc("PriceBands", "EffectiveFrom")).\
                first()
            if price_band is None:
                # Style/ColFitDim
                where = (f"Company_Id = {company_id} and Band_Id = {price_band_id} and "
                         f"Style_Id = {style_id} and ColFitDim_Id = {col_fit_dim_id} and "
                         f"SKU_Id = None and Currency = \"{currency_code}\" and "
                         f"Type = \"{price_type}\" and EffectiveFrom <= {price_date:%Y-%m-%d} and "
                         f"EffectiveTo >= {price_date:%Y-%m-%d}")
                # get last record by EffectiveFrom Date
                price_band = db_session.query(sqa.get_model("PriceBands")).\
                    filter(sqa.where(where)).\
                    order_by(sqa.sort_desc("PriceBands", "EffectiveFrom")).\
                    first()
            if price_band is None:
                # Style
                where = (f"Company_Id = {company_id} and Band_Id = {price_band_id} and "
                         f"Style_Id = {style_id} and ColFitDim_Id = None and "
                         f"SKU_Id = None and Currency = \"{currency_code}\" and "
                         f"Type = \"{price_type}\" and EffectiveFrom <= {price_date:%Y-%m-%d} and "
                         f"EffectiveTo >= {price_date:%Y-%m-%d}")
                # get last record by EffectiveFrom Date
                price_band = db_session.query(sqa.get_model("PriceBands")).\
                    filter(sqa.where(where)).\
                    order_by(sqa.sort_desc("PriceBands", "EffectiveFrom")).\
                    first()
            if price_band is not None:
                price_ex = price_band.Price
                price_source = "PriceBand"
        if price_ex == 0:
            # 2.2 PriceList
            # Style/ColFitDim/Size
            where = (f"Company_Id = {company_id} and "
                     f"Style_Id = {style_id} and ColFitDim_Id = {col_fit_dim_id} and "
                     f"SKU_Id = {sku_id} and Currency = \"{currency_code}\" and "
                     f"Type = \"{price_type}\" and EffectiveFrom <= {price_date:%Y-%m-%d} and "
                     f"EffectiveTo >= {price_date:%Y-%m-%d}")
            # get last record by EffectiveFrom Date
            price_list = db_session.query(sqa.get_model("PriceLists")).\
                filter(sqa.where(where)).\
                order_by(sqa.sort_desc("PriceLists", "EffectiveFrom")).\
                first()
            if price_list is None:
                # Style/ColFitDim
                where = (f"Company_Id = {company_id} and "
                         f"Style_Id = {style_id} and ColFitDim_Id = {col_fit_dim_id} and "
                         f"SKU_Id = None and Currency = \"{currency_code}\" and "
                         f"Type = \"{price_type}\" and EffectiveFrom <= {price_date:%Y-%m-%d} and "
                         f"EffectiveTo >= {price_date:%Y-%m-%d}")
                # get last record by EffectiveFrom Date
                price_list = db_session.query(sqa.get_model("PriceLists")).\
                    filter(sqa.where(where)).\
                    order_by(sqa.sort_desc("PriceLists", "EffectiveFrom")).\
                    first()
            if price_list is None:
                # Style
                where = (f"Company_Id = {company_id} and "
                         f"Style_Id = {style_id} and ColFitDim_Id = None and "
                         f"SKU_Id = None and Currency = \"{currency_code}\" and "
                         f"Type = \"{price_type}\" and EffectiveFrom <= {price_date:%Y-%m-%d} and "
                         f"EffectiveTo >= {price_date:%Y-%m-%d}")
                # get last record by EffectiveFrom Date
                price_list = db_session.query(sqa.get_model("PriceLists")).\
                    filter(sqa.where(where)).\
                    order_by(sqa.sort_desc("PriceLists", "EffectiveFrom")).\
                    first()
            if price_list is None:
                raise Exception(f"Price not Found for: {where}")

            price_ex = price_list.Price
            price_source = "PriceList"

    # 3. Apply Discounts
    if price_type == "SELL":
        if discount > 0:
            price_source += " ContractDiscount"
            if not contract_price_found:
                # Contract Price is already Net of Discounts
                price_ex = price_ex * Decimal(1 - (discount / 100))
        elif trade_discount_percentage > 0:
            discount = trade_discount_percentage
            price_source += " TradeDiscount"
            price_ex = price_ex * Decimal(1 - (discount / 100))

    # 4. Get Sales Tax
    try:
        tax_value, tax_rate, price_inc = get_salestax(db_session,
                                                      company_id,
                                                      customer["CustomerAccount"]["Country"][0],
                                                      sku.TaxType_Id,
                                                      price_ex,
                                                      datetime.utcnow().date())
    except:
        price_inc = price_ex
        tax_value = 0.0
        tax_rate = 0.0

    return price_ex, price_inc, tax_value, tax_rate, discount, \
        price_source, params, where, discount_where


def get_contract_price_discount(db_session: Session,
                                company: DBCompany,
                                customer: Dict[str, Any],
                                sku: DBProductSKU,
                                contract_date: date,
                                volume: int = 0,
                                deliver_via: Optional[DBCustomerWarehouse] = None,
                                season: Optional[DBProductSeason] = None,
                                ship_warehouse: Optional[DBWarehouse] = None,
                                order_source: Optional[DBSalesOrderSource] = None) \
        -> Tuple[Decimal, Decimal, str]:

    currency_code = customer["CustomerAccount"]["Currency"][0]
    customer_id = customer["Id"] if "Account" in customer else customer["ItemCustomer_Id"]
    store_id = customer["Id"] if "Account" not in customer else None

    style = sku.ItemColourFitDim.ItemProduct
    col_fit_dim_id = sku.ItemColourFitDim_Id

    # 1. Customer Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = {customer_id} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.DeliverVia_Id is not None and deliver_via is not None and  \
                deliver_via.Id != rec.DeliverVia_Id:
            continue
        if rec.Store_Id is not None and store_id is not None and  \
                store_id != rec.Store_Id:
            continue
        if rec.Region_Id is not None and customer["Region_Id"] != rec.Region_Id:
            continue
        if rec.CustomerType_Id is not None and customer["Type_Id"] != rec.CustomerType_Id:
            continue
        if rec.CustomerClass_Id is not None and customer["Class_Id"] != rec.CustomerClass_Id:
            continue
        if rec.CustomerGroup_Id is not None and customer["Group_Id"] != rec.CustomerGroup_Id:
            continue
        if rec.Style_Id is not None and style.Id != rec.Style_Id:
            continue
        if rec.ColFitDim_Id is not None and col_fit_dim_id != rec.ColFitDim_Id:
            continue
        if rec.SKU_Id is not None and sku.Id != rec.SKU_Id:
            continue
        if rec.Gender_Id is not None and style.Gender_Id != rec.Gender_Id:
            continue
        if rec.Brand_Id is not None and style.Brand_Id != rec.Brand_Id:
            continue
        if rec.Category_Id is not None and style.Category_Id != rec.Category_Id:
            continue
        if rec.Fabric_Id is not None and style.Fabric_Id != rec.Fabric_Id:
            continue
        if rec.Class_Id is not None and style.Class_Id != rec.Class_Id:
            continue
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 2. Region Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = {customer['Region_Id']} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.CustomerType_Id is not None and customer["Type_Id"] != rec.CustomerType_Id:
            continue
        if rec.CustomerClass_Id is not None and customer["Class_Id"] != rec.CustomerClass_Id:
            continue
        if rec.CustomerGroup_Id is not None and customer["Group_Id"] != rec.CustomerGroup_Id:
            continue
        if rec.Style_Id is not None and style.Id != rec.Style_Id:
            continue
        if rec.ColFitDim_Id is not None and col_fit_dim_id != rec.ColFitDim_Id:
            continue
        if rec.SKU_Id is not None and sku.Id != rec.SKU_Id:
            continue
        if rec.Gender_Id is not None and style.Gender_Id != rec.Gender_Id:
            continue
        if rec.Brand_Id is not None and style.Brand_Id != rec.Brand_Id:
            continue
        if rec.Category_Id is not None and style.Category_Id != rec.Category_Id:
            continue
        if rec.Fabric_Id is not None and style.Fabric_Id != rec.Fabric_Id:
            continue
        if rec.Class_Id is not None and style.Class_Id != rec.Class_Id:
            continue
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 3. CustomerType Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and "
             f"CustomerType_Id = {customer['Type_Id']} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.CustomerClass_Id is not None and customer["Class_Id"] != rec.CustomerClass_Id:
            continue
        if rec.CustomerGroup_Id is not None and customer["Group_Id"] != rec.CustomerGroup_Id:
            continue
        if rec.Style_Id is not None and style.Id != rec.Style_Id:
            continue
        if rec.ColFitDim_Id is not None and col_fit_dim_id != rec.ColFitDim_Id:
            continue
        if rec.SKU_Id is not None and sku.Id != rec.SKU_Id:
            continue
        if rec.Gender_Id is not None and style.Gender_Id != rec.Gender_Id:
            continue
        if rec.Brand_Id is not None and style.Brand_Id != rec.Brand_Id:
            continue
        if rec.Category_Id is not None and style.Category_Id != rec.Category_Id:
            continue
        if rec.Fabric_Id is not None and style.Fabric_Id != rec.Fabric_Id:
            continue
        if rec.Class_Id is not None and style.Class_Id != rec.Class_Id:
            continue
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 4. CustomerClass Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and CustomerType_Id = None and "
             f"CustomerClass_Id = {customer['Class_Id']} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.CustomerGroup_Id is not None and customer["Group_Id"] != rec.CustomerGroup_Id:
            continue
        if rec.Style_Id is not None and style.Id != rec.Style_Id:
            continue
        if rec.ColFitDim_Id is not None and col_fit_dim_id != rec.ColFitDim_Id:
            continue
        if rec.SKU_Id is not None and sku.Id != rec.SKU_Id:
            continue
        if rec.Gender_Id is not None and style.Gender_Id != rec.Gender_Id:
            continue
        if rec.Brand_Id is not None and style.Brand_Id != rec.Brand_Id:
            continue
        if rec.Category_Id is not None and style.Category_Id != rec.Category_Id:
            continue
        if rec.Fabric_Id is not None and style.Fabric_Id != rec.Fabric_Id:
            continue
        if rec.Class_Id is not None and style.Class_Id != rec.Class_Id:
            continue
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 5. CustomerGroup Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and CustomerType_Id = None and "
             f"CustomerClass_Id = None and "
             f"CustomerGroup_Id = {customer['Group_Id']} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.Style_Id is not None and style.Id != rec.Style_Id:
            continue
        if rec.ColFitDim_Id is not None and col_fit_dim_id != rec.ColFitDim_Id:
            continue
        if rec.SKU_Id is not None and sku.Id != rec.SKU_Id:
            continue
        if rec.Gender_Id is not None and style.Gender_Id != rec.Gender_Id:
            continue
        if rec.Brand_Id is not None and style.Brand_Id != rec.Brand_Id:
            continue
        if rec.Category_Id is not None and style.Category_Id != rec.Category_Id:
            continue
        if rec.Fabric_Id is not None and style.Fabric_Id != rec.Fabric_Id:
            continue
        if rec.Class_Id is not None and style.Class_Id != rec.Class_Id:
            continue
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 6. Style Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and CustomerType_Id = None and "
             f"CustomerClass_Id = None and CustomerGroup_Id = None and "
             f"Style_Id = {style.Id} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.ColFitDim_Id is not None and col_fit_dim_id != rec.ColFitDim_Id:
            continue
        if rec.SKU_Id is not None and sku.Id != rec.SKU_Id:
            continue
        if rec.Gender_Id is not None and style.Gender_Id != rec.Gender_Id:
            continue
        if rec.Brand_Id is not None and style.Brand_Id != rec.Brand_Id:
            continue
        if rec.Category_Id is not None and style.Category_Id != rec.Category_Id:
            continue
        if rec.Fabric_Id is not None and style.Fabric_Id != rec.Fabric_Id:
            continue
        if rec.Class_Id is not None and style.Class_Id != rec.Class_Id:
            continue
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 7. Gender Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and CustomerType_Id = None and "
             f"CustomerClass_Id = None and CustomerGroup_Id = None and "
             f"Style_Id = None and ColFitDim_Id = None and SKU_Id = None and "
             f"Gender_Id = {style.Gender_Id} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.Brand_Id is not None and style.Brand_Id != rec.Brand_Id:
            continue
        if rec.Category_Id is not None and style.Category_Id != rec.Category_Id:
            continue
        if rec.Fabric_Id is not None and style.Fabric_Id != rec.Fabric_Id:
            continue
        if rec.Class_Id is not None and style.Class_Id != rec.Class_Id:
            continue
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 8. Brand Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and CustomerType_Id = None and "
             f"CustomerClass_Id = None and CustomerGroup_Id = None and "
             f"Style_Id = None and ColFitDim_Id = None and SKU_Id = None and "
             f"Gender_Id = None and "
             f"Brand_Id = {style.Brand_Id} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.Category_Id is not None and style.Category_Id != rec.Category_Id:
            continue
        if rec.Fabric_Id is not None and style.Fabric_Id != rec.Fabric_Id:
            continue
        if rec.Class_Id is not None and style.Class_Id != rec.Class_Id:
            continue
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 9. Category Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and CustomerType_Id = None and "
             f"CustomerClass_Id = None and CustomerGroup_Id = None and "
             f"Style_Id = None and ColFitDim_Id = None and SKU_Id = None and "
             f"Gender_Id = None and Brand_Id = None and "
             f"Category_Id = {style.Category_Id} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.Fabric_Id is not None and style.Fabric_Id != rec.Fabric_Id:
            continue
        if rec.Class_Id is not None and style.Class_Id != rec.Class_Id:
            continue
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 10. Fabric Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and CustomerType_Id = None and "
             f"CustomerClass_Id = None and CustomerGroup_Id = None and "
             f"Style_Id = None and ColFitDim_Id = None and SKU_Id = None and "
             f"Gender_Id = None and Brand_Id = None and "
             f"Category_Id = None and "
             f"Fabric_Id = {style.Fabric_Id} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.Class_Id is not None and style.Class_Id != rec.Class_Id:
            continue
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 11. Class Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and CustomerType_Id = None and "
             f"CustomerClass_Id = None and CustomerGroup_Id = None and "
             f"Style_Id = None and ColFitDim_Id = None and SKU_Id = None and "
             f"Gender_Id = None and Brand_Id = None and "
             f"Category_Id = None and Fabric_Id = None and "
             f"Class_Id = {style.Class_Id} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")

    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.Type_Id is not None and style.Type_Id != rec.Type_Id:
            continue
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 12. Type Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and CustomerType_Id = None and "
             f"CustomerClass_Id = None and CustomerGroup_Id = None and "
             f"Style_Id = None and ColFitDim_Id = None and SKU_Id = None and "
             f"Gender_Id = None and Brand_Id = None and "
             f"Category_Id = None and Fabric_Id = None and "
             f"Class_Id = None and "
             f"Type_Id = {style.Type_Id} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.Group_Id is not None and style.Group_Id != rec.Group_Id:
            continue
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 13. Group Level
    where = (f"Company_Id = {company.Id} and "
             f"Currency = \"{currency_code}\" and "
             f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
             f"Region_Id = None and CustomerType_Id = None and "
             f"CustomerClass_Id = None and CustomerGroup_Id = None and "
             f"Style_Id = None and ColFitDim_Id = None and SKU_Id = None and "
             f"Gender_Id = None and Brand_Id = None and "
             f"Category_Id = None and Fabric_Id = None and "
             f"Class_Id = None and Type_Id = None and "
             f"Group_Id = {style.Group_Id} and "
             f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
             f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
             f"Volume <= {volume}")
    records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
        filter(sqa.where(where)). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
        order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
        all()
    for rec in records:
        if rec.Season_Id is not None and season is not None and \
                season.Id != rec.Season_Id:
            continue
        if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                ship_warehouse.Id != rec.ShipFromWarehouse_Id:
            continue
        if rec.Source_Id is not None and order_source is not None and  \
                order_source.Id != rec.Source_Id:
            continue
        return rec.Price, rec.Discount, where

    # 14. Season Level
    if season is not None:
        where = (f"Company_Id = {company.Id} and "
                 f"Currency = \"{currency_code}\" and "
                 f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
                 f"Region_Id = None and CustomerType_Id = None and "
                 f"CustomerClass_Id = None and CustomerGroup_Id = None and "
                 f"Style_Id = None and ColFitDim_Id = None and SKU_Id = None and "
                 f"Gender_Id = None and Brand_Id = None and "
                 f"Category_Id = None and Fabric_Id = None and "
                 f"Class_Id = None and Type_Id = None and "
                 f"Group_Id = None and "
                 f"Season_Id = {season.Id} and "
                 f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
                 f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
                 f"Volume <= {volume}")
        records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
            filter(sqa.where(where)). \
            order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
            order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
            all()
        for rec in records:
            if rec.ShipFromWarehouse_Id is not None and ship_warehouse is not None and  \
                    ship_warehouse.Id != rec.ShipFromWarehouse_Id:
                continue
            if rec.Source_Id is not None and order_source is not None and  \
                    order_source.Id != rec.Source_Id:
                continue
            return rec.Price, rec.Discount, where

    # 15. Warehouse Level
    if ship_warehouse is not None:
        where = (f"Company_Id = {company.Id} and "
                 f"Currency = \"{currency_code}\" and "
                 f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
                 f"Region_Id = None and CustomerType_Id = None and "
                 f"CustomerClass_Id = None and CustomerGroup_Id = None and "
                 f"Style_Id = None and ColFitDim_Id = None and SKU_Id = None and "
                 f"Gender_Id = None and Brand_Id = None and "
                 f"Category_Id = None and Fabric_Id = None and "
                 f"Class_Id = None and Type_Id = None and "
                 f"Group_Id = None and Season_Id = None and "
                 f"ShipFromWarehouse_Id = {ship_warehouse.Id} and "
                 f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
                 f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
                 f"Volume <= {volume}")
        records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
            filter(sqa.where(where)). \
            order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
            order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
            all()
        for rec in records:
            if rec.Source_Id is not None and order_source is not None and  \
                    order_source.Id != rec.Source_Id:
                continue
            return rec.Price, rec.Discount, where

    # 16. Order Source Level
    if order_source is not None:
        where = (f"Company_Id = {company.Id} and "
                 f"Currency = \"{currency_code}\" and "
                 f"Customer_Id = None and DeliverVia_Id = None and Store_Id = None and "
                 f"Region_Id = None and CustomerType_Id = None and "
                 f"CustomerClass_Id = None and CustomerGroup_Id = None and "
                 f"Style_Id = None and ColFitDim_Id = None and SKU_Id = None and "
                 f"Gender_Id = None and Brand_Id = None and "
                 f"Category_Id = None and Fabric_Id = None and "
                 f"Class_Id = None and Type_Id = None and "
                 f"Group_Id = None and Season_Id = None and "
                 f"ShipFromWarehouse_Id = None and "
                 f"Source_Id = {order_source.Id} and "
                 f"EffectiveFrom <= {contract_date:%Y-%m-%d} and "
                 f"EffectiveTo >= {contract_date:%Y-%m-%d} and "
                 f"Volume <= {volume}")
        records = db_session.query(sqa.get_model("ContractPriceDiscounts")).\
            filter(sqa.where(where)). \
            order_by(sqa.sort_desc("ContractPriceDiscounts", "EffectiveFrom")). \
            order_by(sqa.sort_desc("ContractPriceDiscounts", "Volume")). \
            all()
        for rec in records:
            return rec.Price, rec.Discount, where

    return 0.0, 0.0, ""

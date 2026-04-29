from datetime import date
from typing import Optional, Dict, Any, List, Tuple

from sqlalchemy.orm import Session
from pydantic import BaseModel

from ....db import sqa
from ....db.models.app.products.ProductSeasons import ProductSeason as DBProductSeason
from ....db.models.app.products.Products import Product as DBProduct


class SeasonKey(BaseModel):
    CompanyId: int
    StartDate: date
    EndDate: date


class SeasonResult(BaseModel):
    Season: Optional[Dict[str, Any]] = None


def get_season(db_session: Session,
               company_id: int,
               start_date: date,
               end_date: date) -> Optional[DBProductSeason]:

    where = (f"Company_Id = {company_id} and "
             f"StartDate <= {start_date:%Y-%m-%d} and "
             f"EndDate >= {end_date:%Y-%m-%d}")

    season = (db_session.query(sqa.get_model("ProductSeasons")).
              filter(sqa.where(where)).
              order_by(sqa.sort_desc("ProductSeasons", "StartDate")).
              first())
    if season is None:
        return None

    return season.data_to_dict(except_fields=["Password", "versions",
                                              "Company_Id", "CreateOpId_Id",
                                              "CreateOpId", "CreateTimeStamp",
                                              "ModifiedOpId_Id",
                                              "ModifiedOpId", "ModifiedTimeStamp"],
                               depth=0)


def get_product_matrix(db_session: Session,
                       product_id: int,
                       valid_only: bool = False,
                       colfitdim_id: int = None,
                       allow_sales: bool = None,
                       allow_production: bool = None,
                       allow_purchasing: bool = None) -> Tuple[DBProduct, List[Dict[str, Any]]]:

    product = db_session.query(sqa.get_model("Products")).get(product_id)
    if product is None:
        raise Exception(f"Invalid Product: {product_id}")

    sizes = list()
    for size in sorted(product.SizeScale.Sizes, key=lambda s: s.Bucket):
        if valid_only:
            # check if valid sizes in all product colfitdim
            valid = False
            where = f"ItemProduct_Id = {product_id}"
            if colfitdim_id is not None:
                where += f" and Id = {colfitdim_id}"
            if allow_sales is not None:
                where += f" and AllowSales = {allow_sales}"
            if allow_purchasing is not None:
                where += f" and AllowPurchasing = {allow_purchasing}"
            if allow_production is not None:
                where += f" and AllowProduction = {allow_production}"

            colfitdim = (db_session.query(sqa.get_model("ProductColourFitDims")).
                         filter(sqa.where(where)).
                         all())
            if colfitdim is None:
                continue
            for col in colfitdim:
                for sku in col.Sizes:
                    if sku.Size.Bucket == size.Bucket:
                        if sku.Status != "NotValid":
                            valid = True
                        break
            if not valid:
                continue
        sizes.append(dict(Id=size.Id, Bucket=size.Bucket, Size=size.Size))

    return product, sizes

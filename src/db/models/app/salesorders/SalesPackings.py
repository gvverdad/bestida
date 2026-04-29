from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Index)
from sqlalchemy.orm import relationship

from src.db.models.model import Model
from src.security.policy import get_current_uid


class SalesPacking(Model):
    __versioned__ = {}
    __tablename__ = "SalesPackings"
    __table_args__ = dict(info=dict(label="Sales Packings",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id",
                                              "Location_Id"],
                                    key="SKU_Id"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SalesPacking.Company_Id")

    # Many2One
    Location_Id = Column(Integer, ForeignKey("WarehouseLocations.Id"),
                         nullable=False,
                         info=dict(label="Location",
                                   selectId="Id",
                                   selectKey="warehouse_area_location",
                                   selectFormat=["warehouse_area_location"],
                                   depth=1
                                   ))
    Location = relationship("WarehouseLocation",
                            primaryjoin="WarehouseLocation.Id==SalesPacking.Location_Id")

    # Many2One
    SKU_Id = Column(Integer, ForeignKey("ProductSKUs.Id"),
                    nullable=False,
                    info=dict(label="SKU",
                              selectId="Id",
                              selectKey="style_col_fit_dim_size",
                              selectFormat=["style_col_fit_dim_size"],
                              depth=1
                              ))
    SKU = relationship("ProductSKU",
                       primaryjoin="ProductSKU.Id==SalesPacking.SKU_Id")

    # Current Packed Units
    Packings = Column(Integer, nullable=True, default=0,
                      info=dict(label="Sales Packed Qty"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesPacking.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesPacking.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("SalesPacking_Index1", SalesPacking.Company_Id, SalesPacking.Location_Id,
      SalesPacking.SKU_Id, unique=True)
Index("SalesPacking_Index2", SalesPacking.Company_Id, SalesPacking.SKU_Id,
      SalesPacking.Location_Id, unique=True)

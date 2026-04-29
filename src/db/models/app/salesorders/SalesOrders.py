from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Index)
from sqlalchemy.orm import relationship

from src.db.models.model import Model
from src.security.policy import get_current_uid


class SalesOrder(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrders"
    __table_args__ = dict(info=dict(label="Sales Orders",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id",
                                              "Warehouse_Id"],
                                    key="SKU_Id"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SalesOrder.Company_Id")

    # Many2One
    Warehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                          nullable=False,
                          info=dict(label="Warehouse",
                                    selectId="Id", selectKey="Name", depth=1))
    Warehouse = relationship("Warehouse",
                             primaryjoin="Warehouse.Id==SalesOrder.Warehouse_Id")

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
                       primaryjoin="ProductSKU.Id==SalesOrder.SKU_Id")

    # Total Sales Orders Units ever
    Orders = Column(Integer, nullable=True, default=0,
                    info=dict(label="Sales Ordered Qty"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrder.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrder.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("SalesOrder_Index1", SalesOrder.Company_Id, SalesOrder.Warehouse_Id,
      SalesOrder.SKU_Id, unique=True)
Index("SalesOrder_Index2", SalesOrder.Company_Id, SalesOrder.SKU_Id,
      SalesOrder.Warehouse_Id, unique=True)

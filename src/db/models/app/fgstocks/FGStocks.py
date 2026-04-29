from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Index)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class FGStock(Model):
    __versioned__ = {}
    __tablename__ = "FGStocks"
    __table_args__ = dict(info=dict(label="Product Stock on Hand",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id",
                                              "Location_Id"],
                                    key="SKU_Id",
                                    sum=["OnHand"],
                                    sumGroups=[
                                        "Company.CompanyId",
                                        "Company.Name",
                                        "SKU.ItemColourFitDim.ItemProduct.Style",
                                        "SKU.ItemColourFitDim.ItemProduct.Name",
                                        "SKU.ItemColourFitDim.Colour.Colour",
                                        "SKU.ItemColourFitDim.Colour.Description",
                                        "SKU.ItemColourFitDim.Fitting.Fitting",
                                        "SKU.ItemColourFitDim.Fitting.Description",
                                        "SKU.ItemColourFitDim.Dimension.Dimension",
                                        "SKU.ItemColourFitDim.Dimension.Description",
                                        "SKU.Size.Size",
                                        "Location.ItemWarehouseArea.ItemWarehouse.Warehouse",
                                        "Location.ItemWarehouseArea.ItemWarehouse.Name",
                                        "Location.ItemWarehouseArea.Area",
                                        "Location.ItemWarehouseArea.Name",
                                        "Location.Row",
                                        "Location.Level",
                                        "Location.Bin",
                                        "Location.Location",
                                        "Location.Status"
                                    ],
                                    subTables=[
                                        dict(
                                            table="FGStockMovements",
                                            type="GRID",
                                            title="Stock Reconciliation",
                                            params={"FromLocation.ItemWarehouseArea.ItemWarehouse.Warehouse":"Location.ItemWarehouseArea.ItemWarehouse.Warehouse",
                                                    "FromLocation.ItemWarehouseArea.Area":"Location.ItemWarehouseArea.Area",
                                                    "FromLocation.Location":"Location.Location",
                                                    "SKU.ItemColourFitDim.ItemProduct.Style":"SKU.ItemColourFitDim.ItemProduct.Style",
                                                    "SKU.ItemColourFitDim.Colour.Colour":"SKU.ItemColourFitDim.Colour.Colour",
                                                    "SKU.ItemColourFitDim.Fitting.Fitting":"SKU.ItemColourFitDim.Fitting.Fitting",
                                                    "SKU.ItemColourFitDim.Dimension.Dimension":"SKU.ItemColourFitDim.Dimension.Dimension",
                                                    "SKU.Size.Size":"SKU.Size.Size"}
                                        )
                                    ]
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==FGStock.Company_Id")

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
                            primaryjoin="WarehouseLocation.Id==FGStock.Location_Id")

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
                       primaryjoin="ProductSKU.Id==FGStock.SKU_Id")

    # do not directly modify OnHand - FGStockMovements trigger will update FGStock.OnHand
    OnHand = Column(Integer, nullable=True, default=0,
                    info=dict(label="Stock On Hand",
                              modifiable=False))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==FGStock.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==FGStock.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("FGStock_Index1", FGStock.Company_Id, FGStock.Location_Id,
      FGStock.SKU_Id, unique=True)
Index("FGStock_Index2", FGStock.Company_Id, FGStock.SKU_Id,
      FGStock.Location_Id, unique=True)

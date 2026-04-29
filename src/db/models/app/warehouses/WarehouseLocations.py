from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Index,
                        Enum, Boolean, event, select)
from sqlalchemy.types import String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid


class WarehouseLocation(Model):
    __versioned__ = {}
    __tablename__ = "WarehouseLocations"
    __table_args__ = dict(info=dict(label="Warehouse Locations", desc="Locations",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["ItemWarehouseArea_Id",
                                              "Row", "Level"],
                                    key="Bin",
                                    parentTables=[
                                        dict(column="ItemWarehouseArea",
                                             table="WarehouseAreas")
                                    ],
                                    hybrids=[dict(name="is_reserved",
                                                  label="Reserved",
                                                  type="Boolean",
                                                  sortable=True,
                                                  searchable=True
                                                  ),
                                             dict(name="warehouse_area_location",
                                                  label="Warehouse/Area/Location",
                                                  type="String",
                                                  length=34,
                                                  decimals=0,
                                                  sortable=True,
                                                  searchable=True
                                                  )
                                             ]
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company",
                           primaryjoin="Company.Id==WarehouseLocation.Company_Id")

    # Many2One side of WarehouseArea
    ItemWarehouseArea_Id = Column(Integer, ForeignKey("WarehouseAreas.Id"),
                                  info=dict(label="Warehouse/Area",
                                            selectId="Id",
                                            selectKey="warehouse_area",
                                            selectFormat=["warehouse_area"],
                                            exceptSchemaFields=["Company_Id", "Company", "Locations",
                                                                "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                "versions"],
                                            depth=1))

    Row = Column(Integer, nullable=False,
                 info=dict(label="Row", min=1, max=9999))
    Level = Column(Integer, nullable=False,
                   info=dict(label="Level", min=1, max=999))
    Bin = Column(Integer, nullable=False,
                 info=dict(label="Bin", min=1, max=99999))

    Location = Column(String(16), nullable=False,
                      info=dict(label="Location",
                                modifiable=False, displayable=True,
                                selectId="Id",
                                selectKey="Location",
                                selectColumn="Location",
                                selectFormat=["Location", "ItemWarehouseArea.warehouse_area"],
                                selectTable="WarehouseLocations",
                                ))

    Dimension = Column(Integer, nullable=True, default=0,
                       info=dict(label="Bin Dimension"))
    # Many2One
    UOM_Id = Column(Integer, ForeignKey("UOMs.Id"),
                    info=dict(label="Bin Dimension UOM", selectId="Id",
                              selectKey="Description",
                              selectFormat=["Code", "Description"],
                              requiredIf="Dimension > 0",
                              depth=1))
    UOM = relationship("UOM", primaryjoin="UOM.Id==WarehouseLocation.UOM_Id")

    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User",
                                primaryjoin="User.Id==WarehouseLocation.InactiveOpId_Id")
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp",
                                         modifiable=False))

    Status = Column(Enum("Live", "Frozen", name="Location_Status"),
                    nullable=False, default="Live",
                    info=dict(label="Status"))

    # Many2One
    Reserved_Id = Column(Integer, ForeignKey("ProductSKUs.Id"),
                         nullable=True,
                         info=dict(label="Reserved for SKU - Style/Col/Fit/Dim/Size",
                                   selectTable="ProductSKUs",  # used for server update
                                   selectObject="ProductSKUs",  # used for client selection list
                                   selectId="Id",
                                   selectKey="style_col_fit_dim_size",
                                   selectFormat=["style_col_fit_dim_size"],
                                   depth=1))
    Reserved = relationship("ProductSKU",
                            primaryjoin="ProductSKU.Id==WarehouseLocation.Reserved_Id")

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==WarehouseLocation.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==WarehouseLocation.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # calculated columns
    @hybrid_property
    def is_reserved(self):
        return self.Reserved_Id is not None

    @is_reserved.expression
    def is_reserved(cls):
        return cls.Reserved_Id is not None

    @hybrid_property
    def warehouse_area_location(self):
        return self.ItemWarehouseArea.ItemWarehouse.Warehouse + " " + \
               self.ItemWarehouseArea.Area + " " + \
               self.Location

    @warehouse_area_location.expression
    def warehouse_area_location(cls):
        from .WarehouseAreas import WarehouseArea
        from .Warehouses import Warehouse

        return (select([Warehouse.Warehouse + " " +
                      WarehouseArea.Area + " " +
                      WarehouseLocation.Location]).
                where(WarehouseArea.Id == cls.ItemWarehouseArea_Id).
                where(Warehouse.Id == WarehouseArea.ItemWarehouse_Id).
                as_scalar())

    # One2Many side of FGStockMovements
    # uselist=False - this is just used in validate_delete
    FromLocations = relationship("FGStockMovement", uselist=False,
                                 back_populates="FromLocation",
                                 primaryjoin="FGStockMovement.FromLocation_Id==WarehouseLocation.Id",
                                 info=dict(hidden=True, dump=False))
    ToLocations = relationship("FGStockMovement", uselist=False,
                               back_populates="ToLocation",
                               primaryjoin="FGStockMovement.ToLocation_Id==WarehouseLocation.Id",
                               info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"

        if self.FromLocations is not None or self.ToLocations is not None:
            is_ok = False
            message = "Cannot Delete. There are Product Stock Movements linked to this Warehouse Location"

        return is_ok, message


Index("WarehouseLocation_Index1", WarehouseLocation.Company_Id,
      WarehouseLocation.ItemWarehouseArea_Id,
      WarehouseLocation.Row, WarehouseLocation.Level,
      WarehouseLocation.Bin, unique=True)
Index("WarehouseLocation_Index2", WarehouseLocation.Company_Id,
      WarehouseLocation.ItemWarehouseArea_Id,
      WarehouseLocation.Location, unique=True)
Index("WarehouseLocation_Index3", WarehouseLocation.Company_Id,
      WarehouseLocation.Reserved_Id, unique=False)


def on_warehouse_location_update(mapper, connection, target):
    row = getattr(target, "Row")
    level = getattr(target, "Level")
    bin = getattr(target, "Bin")

    loc = str(row).zfill(4) + "-" + str(level).zfill(3) + "-" + str(bin).zfill(5)

    setattr(target, "Location", loc)

    inactive = getattr(target, "Inactive")
    if inactive and getattr(target, "InactiveTimeStamp") is None:
        setattr(target, "InactiveTimeStamp", datetime.utcnow())
        setattr(target, "InactiveOpId_Id", get_current_uid())
    elif not inactive and getattr(target, "InactiveTimeStamp") is not None:
        setattr(target, "InactiveTimeStamp", None)
        setattr(target, "InactiveOpId_Id", None)


event.listen(WarehouseLocation, "before_insert", on_warehouse_location_update)  # Mapper Event
event.listen(WarehouseLocation, "before_update", on_warehouse_location_update)  # Mapper Event

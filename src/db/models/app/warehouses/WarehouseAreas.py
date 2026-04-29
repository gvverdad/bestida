from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Index,
                        String, Enum, Boolean, event, func, select, inspect)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid


class WarehouseArea(Model):
    __versioned__ = {}
    __tablename__ = "WarehouseAreas"
    __table_args__ = dict(info=dict(label="Warehouse Areas", desc="Areas",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Area",
                                    parentTables=[
                                        dict(column="ItemWarehouse",
                                             table="Warehouses")
                                    ],
                                    hybrids=[dict(name="number_of_locations",
                                                  label="Locations",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="warehouse_area",
                                                  label="Warehouse/Area",
                                                  type="String",
                                                  length=17,
                                                  decimals=0,
                                                  sortable=True,
                                                  searchable=True)
                                             ]
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company",
                           primaryjoin="Company.Id==WarehouseArea.Company_Id")

    # Many2One side of Warehouse
    ItemWarehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                              info=dict(label="Warehouse",
                                        selectId="Id", selectKey="Name",
                                        exceptSchemaFields=["Company_Id", "Company", "Areas",
                                                            "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                            "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                            "versions"],
                                        depth=1))

    Area = Column(String(8), nullable=False,
                  info=dict(label="Area", case="uppercase",
                            selectId="Id",
                            selectKey="Area",
                            selectColumn="Area",
                            selectFormat=["Area", "ItemWarehouse.Warehouse", "Name"],
                            selectTable="WarehouseAreas",
                            ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))

    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User",
                                primaryjoin="User.Id==WarehouseArea.InactiveOpId_Id")
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp",
                                         modifiable=False))

    Type = Column(Enum("Pick", "Pack", "Bulk", "Receiving",
                       name="Area_Type"),
                  nullable=False, default="Pick",
                  info=dict(label="Type"))

    Status = Column(Enum("Live", "Frozen", name="Area_Status"),
                    nullable=False, default="Live",
                    info=dict(label="Status"))

    # One2Many
    Locations = relationship("WarehouseLocation", uselist=True,
                             backref="ItemWarehouseArea",
                             cascade="all, delete-orphan",
                             info=dict(label="Locations", depth=1))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==WarehouseArea.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==WarehouseArea.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    @hybrid_property
    def number_of_locations(self):
        return len(self.Locations)

    @number_of_locations.expression
    def number_of_locations(cls):
        from .WarehouseLocations import WarehouseLocation

        return (select([func.count()]).
                where(WarehouseLocation.ItemWarehouseArea_Id == cls.Id).
                as_scalar())

    @hybrid_property
    def warehouse_area(self):
        return self.ItemWarehouse.Warehouse + " " + self.Area

    @warehouse_area.expression
    def warehouse_area(cls):
        from .Warehouses import Warehouse

        return (select([Warehouse.Warehouse + " " + WarehouseArea.Area]).
                where(Warehouse.Id == cls.ItemWarehouse_Id).
                as_scalar())

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"

        for loc in self.Locations:
            is_ok, _ = loc.validate_delete(user_rowid, company_rowid, locale, timezone, data)
            if not is_ok:
                message = "Cannot Delete. There are Stock Movements linked to this Warehouse Area"
                break

        return is_ok, message


Index("WarehouseArea_Index1", WarehouseArea.Company_Id,
      WarehouseArea.ItemWarehouse_Id, WarehouseArea.Area, unique=True)
Index("WarehouseArea_Index2", WarehouseArea.Company_Id,
      WarehouseArea.Type, unique=False)


def on_warehouse_area_update(mapper, connection, target):
    from .WarehouseLocations import WarehouseLocation

    hist_inactive = inspect(target).attrs.Inactive.history
    # new record  History(added=[False], unchanged=(), deleted=())
    # no status change History(added=(), unchanged=[False], deleted=())
    # status change History(added=[True], unchanged=(), deleted=[False])
    if isinstance(hist_inactive.deleted, list):
        if target.Inactive is True:
            setattr(target, "InactiveTimeStamp", datetime.utcnow())
            setattr(target, "InactiveOpId_Id", get_current_uid())
        else:
            setattr(target, "InactiveTimeStamp", None)
            setattr(target, "InactiveOpId_Id", None)
        connection.execute(
            WarehouseLocation.__table__.update().
            values(Inactive=target.Inactive).
            where(WarehouseLocation.ItemWarehouseArea_Id == target.Id)
        )

    hist_status = inspect(target).attrs.Status.history
    # new record  History(added=['Live'], unchanged=(), deleted=())
    # no status change History(added=(), unchanged=['Live'], deleted=())
    # status change History(added=['Frozen'], unchanged=(), deleted=['Live'])
    if isinstance(hist_status.deleted, list):
        connection.execute(
            WarehouseLocation.__table__.update().
            values(Status=target.Status).
            where(WarehouseLocation.ItemWarehouseArea_Id == target.Id)
        )


event.listen(WarehouseArea, "before_update", on_warehouse_area_update)  # Mapper Event
event.listen(WarehouseArea, "before_insert", on_warehouse_area_update)  # mapper Event

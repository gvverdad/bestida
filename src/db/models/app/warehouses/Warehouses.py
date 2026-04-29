from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Index, String,
                        Boolean, Enum, event, func, select, inspect)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid


class Warehouse(Model):
    __versioned__ = {}
    __tablename__ = "Warehouses"
    __table_args__ = dict(info=dict(label="Warehouses",
                                    companyField="Company_Id",
                                    stepperTitleFields=["Warehouse", "Name"],
                                    keyPaths=["Company_Id"],
                                    key="Warehouse",
                                    hybrids=[dict(name="number_of_areas",
                                                  label="Areas",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True)]
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==Warehouse.Company_Id")

    Warehouse = Column(String(8), nullable=False,
                       info=dict(label="Warehouse", case="uppercase",
                                 selectId="Id",
                                 selectKey="Warehouse",
                                 selectColumn="Warehouse",
                                 selectFormat=["Warehouse", "Name"],
                                 selectTable="Warehouses",
                                 documents=[dict(program="DocumentWarehouse",
                                                params=dict(warehouse="."))
                                           ]
                                 ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))

    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User",
                                primaryjoin="User.Id==Warehouse.InactiveOpId_Id")
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp",
                                         modifiable=False))
    Type = Column(Enum("Stock", "Bonded", name="Warehouse_Type"),
                  nullable=False, default="Stock",
                  info=dict(label="Type"))

    Status = Column(Enum("Live", "Frozen", name="Warehouse_Status"),
                    nullable=False, default="Live",
                    info=dict(label="Status"))

    # One2Many
    Addresses = relationship("WarehouseAddress", uselist=True,
                             backref="ItemWarehouse",
                             cascade="all, delete-orphan",
                             info=dict(requiredEntry=dict(type="AddressType.Type",
                                                          value=["MAIN"],
                                                          min=1),
                                       depth=1))

    # One2Many
    Phones = relationship("WarehousePhone", uselist=True,
                          backref="ItemWarehouse",
                          cascade="all, delete-orphan")

    # One2Many
    Emails = relationship("WarehouseEmail", uselist=True,
                          backref="ItemWarehouse",
                          cascade="all, delete-orphan")

    # One2Many
    Contacts = relationship("WarehouseContact", uselist=True,
                            backref="ItemWarehouse",
                            cascade="all, delete-orphan")

    # One2Many
    Areas = relationship("WarehouseArea", uselist=True,
                         backref="ItemWarehouse",
                         cascade="all, delete-orphan")

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Warehouse.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Warehouse.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Customer
    # uselist=False - this is just used in validate_delete
    Customers = relationship("Customer", uselist=False,
                             back_populates="ShipFromWarehouse",
                             primaryjoin="Customer.ShipFromWarehouse_Id==Warehouse.Id",
                             info=dict(hidden=True, dump=False))
    Stores = relationship("CustomerStore", uselist=False,
                          back_populates="ShipFromWarehouse",
                          primaryjoin="CustomerStore.ShipFromWarehouse_Id==Warehouse.Id",
                          info=dict(hidden=True, dump=False))
    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                               back_populates="ShipFromWarehouse",
                               primaryjoin="ContractPriceDiscount.ShipFromWarehouse_Id==Warehouse.Id",
                               info=dict(hidden=True, dump=False))

    @hybrid_property
    def number_of_areas(self):
        return len(self.Areas)

    @number_of_areas.expression
    def number_of_areas(cls):
        from .WarehouseAreas import WarehouseArea

        return (select([func.count()]).
                where(WarehouseArea.ItemWarehouse_Id == cls.Id).
                as_scalar())

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        for area in self.Areas:
            is_ok, _ = area.validate_delete(user_rowid, company_rowid, locale, timezone, data)
            if not is_ok:
                tables = "Product Stock Movements"
                break

        if self.Customers is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Customers"

        if self.Stores is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "CustomerStores"

        if self.ContractPrices is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Contract Price/Discounts"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Warehouse"

        return is_ok, message


Index("Warehouse_Index1", Warehouse.Company_Id, Warehouse.Warehouse, unique=True)
Index("Warehouse_Index2", Warehouse.Company_Id, Warehouse.Type, unique=False)


def on_warehouse_update(mapper, connection, target):
    from .WarehouseAreas import WarehouseArea
    from .WarehouseLocations import WarehouseLocation

    hist_inactive = inspect(target).attrs.Inactive.history
    # new record: History(added=[False], unchanged=(), deleted=())
    # no status change: History(added=(), unchanged=[False], deleted=())
    # status change: History(added=[True], unchanged=(), deleted=[False])
    if isinstance(hist_inactive.deleted, list):
        if target.Inactive is True:
            setattr(target, "InactiveTimeStamp", datetime.utcnow())
            setattr(target, "InactiveOpId_Id", get_current_uid())
        else:
            setattr(target, "InactiveTimeStamp", None)
            setattr(target, "InactiveOpId_Id", None)
        connection.execute(
            WarehouseArea.__table__.update().
            values(Inactive=target.Inactive).
            where(WarehouseArea.ItemWarehouse_Id == target.Id)
        )
        # above WarehouseArea update() not triggering WarehouseArea on_warehouse_area_update
        for area in target.Areas:
            connection.execute(
                WarehouseLocation.__table__.update().
                values(Inactive=target.Inactive).
                where(WarehouseLocation.ItemWarehouseArea_Id == area.Id)
            )

    hist_status = inspect(target).attrs.Status.history
    # new record: History(added=['Live'], unchanged=(), deleted=())
    # no status change: History(added=(), unchanged=['Live'], deleted=())
    # status change: History(added=['Frozen'], unchanged=(), deleted=['Live'])
    if isinstance(hist_status.deleted, list):
        connection.execute(
            WarehouseArea.__table__.update().
            values(Status=target.Status).
            where(WarehouseArea.ItemWarehouse_Id == target.Id)
        )
        # above WarehouseArea update() not triggering WarehouseArea on_warehouse_area_update
        for area in target.Areas:
            connection.execute(
                WarehouseLocation.__table__.update().
                values(Status=target.Status).
                where(WarehouseLocation.ItemWarehouseArea_Id == area.Id)
            )


event.listen(Warehouse, "before_update", on_warehouse_update)  # Mapper Event
event.listen(Warehouse, "before_insert", on_warehouse_update)  # mapper Event

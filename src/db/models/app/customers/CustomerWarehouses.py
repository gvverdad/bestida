from datetime import datetime

from sqlalchemy import event
from sqlalchemy import (Column, ForeignKey, Integer, DateTime,
                        Index, String, Boolean)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class CustomerWarehouse(Model):
    __versioned__ = {}
    __tablename__ = "CustomerWarehouses"
    __table_args__ = dict(info=dict(label="Customer Warehouses", desc="Warehouses",
                                    companyField="Company_Id",
                                    stepperTitleFields=["Warehouse", "Name"],
                                    keyPaths=["ItemCustomer_Id"],
                                    key="Warehouse",
                                    parentTables=[
                                        dict(column="ItemCustomer",
                                             table="Customers")
                                    ]
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==CustomerWarehouse.Company_Id")

    # Many2One side of Customer
    ItemCustomer_Id = Column(Integer, ForeignKey("Customers.Id"),
                             info=dict(label="Account",
                                       selectId="Id",
                                       selectKey="Name",
                                       exceptSchemaFields=["Company_Id", "Company", "Warehouses",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       depth=1))

    Warehouse = Column(String(16), nullable=False, info=dict(label="Warehouse Code",
                                                             case="uppercase",
                                                             selectId="Id",
                                                             selectKey="Warehouse",
                                                             selectColumn="Warehouse",
                                                             selectFormat=["Warehouse", "ItemCustomer.Account", "Name"],
                                                             selectTable="CustomerWarehouses",
                                                             ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))

    InterchangeNumber = Column(String(32), info=dict(label="Interchange Number"))
    CustomerNumber = Column(String(32), info=dict(label="Customer Number"))

    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User", primaryjoin="User.Id==CustomerWarehouse.InactiveOpId_Id")
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp", modifiable=False))

    # One2Many
    Addresses = relationship("CustomerWarehouseAddress", uselist=True,
                             backref="ItemCustomerWarehouse",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"],
                                       requiredEntry=dict(type="AddressType.Type",
                                                          value=["MAIN"],
                                                          min=1),
                                       depth=1))

    # One2Many
    Phones = relationship("CustomerWarehousePhone", uselist=True,
                          backref="ItemCustomerWarehouse",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Emails = relationship("CustomerWarehouseEmail", uselist=True,
                          backref="ItemCustomerWarehouse",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Contacts = relationship("CustomerWarehouseContact", uselist=True,
                            backref="ItemCustomerWarehouse",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==CustomerWarehouse.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CustomerWarehouse.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of ContractPriceDiscount
    # uselist=False - this is just used in validate_delete
    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                               back_populates="DeliverVia",
                               primaryjoin="ContractPriceDiscount.DeliverVia_Id==CustomerWarehouse.Id",
                               info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        # TODO: validate against Sales Orders
        if self.ContractPrices is not None:
            is_ok = False
            tables = "Contract Price/Discounts"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Customer Warehouse"


        return is_ok, message


Index("CustomerWarehouse_Index1", CustomerWarehouse.Company_Id,
      CustomerWarehouse.ItemCustomer_Id,
      CustomerWarehouse.Warehouse, unique=True)
Index("CustomerWarehouse_Index2", CustomerWarehouse.Company_Id,
      CustomerWarehouse.InterchangeNumber, unique=False)
Index("CustomerWarehouse_Index3", CustomerWarehouse.Company_Id,
      CustomerWarehouse.CustomerNumber, unique=False)


def on_customer_warehouse_update(mapper, connection, target):
    inactive = getattr(target, "Inactive")
    if inactive and getattr(target, "InactiveTimeStamp") is None:
        setattr(target, "InactiveTimeStamp", datetime.utcnow())
        setattr(target, "InactiveOpId_Id", get_current_uid())
    elif not inactive and getattr(target, "InactiveTimeStamp") is not None:
        setattr(target, "InactiveTimeStamp", None)
        setattr(target, "InactiveOpId_Id", None)


event.listen(CustomerWarehouse, "before_update", on_customer_warehouse_update)  # Mapper Event
event.listen(CustomerWarehouse, "before_insert", on_customer_warehouse_update)  # mapper Event

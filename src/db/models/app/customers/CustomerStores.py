from datetime import datetime

from sqlalchemy import event
from sqlalchemy import (Column, ForeignKey, Integer, DateTime,
                        Index, String, Boolean)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import (get_locale_choices, get_timezone_choices)


class CustomerStore(Model):
    __versioned__ = {}
    __tablename__ = "CustomerStores"
    __table_args__ = dict(info=dict(label="Customer Stores", desc="Stores",
                                    companyField="Company_Id",
                                    stepperTitleFields=["Store", "Name"],
                                    keyPaths=["ItemCustomer_Id"],
                                    key="Store",
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
    Company = relationship("Company", primaryjoin="Company.Id==CustomerStore.Company_Id")

    # Many2One side of Customer
    ItemCustomer_Id = Column(Integer, ForeignKey("Customers.Id"),
                             info=dict(label="Account",
                                       selectId="Id",
                                       selectKey="Name",
                                       exceptSchemaFields=["Company_Id", "Company", "Stores",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       depth=1))

    Store = Column(String(16), nullable=False, info=dict(label="Store Code",
                                                         case="uppercase",
                                                         selectId="Id",
                                                         selectKey="Store",
                                                         selectColumn="Store",
                                                         selectFormat=["Store", "ItemCustomer.Account", "Name"],
                                                         selectTable="CustomerStores",
                                                         ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))

    InterchangeNumber = Column(String(32), info=dict(label="Interchange Number"))
    CustomerNumber = Column(String(32), info=dict(label="Customer Number"))

    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User", primaryjoin="User.Id==CustomerStore.InactiveOpId_Id")
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp", modifiable=False))

    Locale = Column(String(8), nullable=True,
                    info=dict(label="Locale",
                              choices=get_locale_choices,
                              choices_getter="getLocaleList"))

    Timezone = Column(String(32), nullable=True,
                      info=dict(label="Timezone",
                                choices=get_timezone_choices,
                                choices_getter="getTimezoneList"))

    # Many2One
    Region_Id = Column(Integer, ForeignKey("CustomerRegions.Id"), nullable=True,
                       info=dict(label="Region", selectId="Id",
                                 selectKey="Description", depth=1))
    Region = relationship("CustomerRegion", primaryjoin="CustomerRegion.Id==CustomerStore.Region_Id")

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CustomerTypes.Id"), nullable=True,
                     info=dict(label="Type",
                               selectId="Id",
                               selectKey="Description",
                               depth=1))
    Type = relationship("CustomerType", primaryjoin="CustomerType.Id==CustomerStore.Type_Id")

    # Many2One
    Class_Id = Column(Integer, ForeignKey("CustomerClasses.Id"), nullable=True,
                      info=dict(label="Class", selectId="Id",
                                selectKey="Description", depth=1))
    Class = relationship("CustomerClass", primaryjoin="CustomerClass.Id==CustomerStore.Class_Id")

    # Many2One
    Group_Id = Column(Integer, ForeignKey("CustomerGroups.Id"), nullable=True,
                      info=dict(label="Group", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Group = relationship("CustomerGroup", primaryjoin="CustomerGroup.Id==CustomerStore.Group_Id")

    AllowDeliveries = Column(Boolean, default=False, info=dict(label="Allow Deliveries"))

    # Many2One
    PriceBand_Id = Column(Integer, ForeignKey("CustomerPriceBands.Id"), nullable=True,
                          info=dict(label="Price Band",
                                    selectId="Id", selectKey="Description",
                                    depth=1))
    PriceBand = relationship("CustomerPriceBand",
                             primaryjoin="CustomerPriceBand.Id==CustomerStore.PriceBand_Id")

    # Many2One
    Priority_Id = Column(Integer, ForeignKey("CustomerPriorities.Id"), nullable=True,
                         info=dict(label="Priority", selectId="Id",
                                   selectKey="Description", depth=1))
    Priority = relationship("CustomerPriority",
                            primaryjoin="CustomerPriority.Id==CustomerStore.Priority_Id")

    # Many2One
    Carrier_Id = Column(Integer, ForeignKey("Carriers.Id"), nullable=True,
                        info=dict(label="Carrier", selectId="Id",
                                  selectKey="Name", depth=1))
    Carrier = relationship("Carrier", primaryjoin="Carrier.Id==CustomerStore.Carrier_Id")

    ShipmentPercentage = Column(Integer, nullable=True,
                                info=dict(label="Shipment Percentage",
                                          numberType="percent",
                                          min=0, max=100))

    # Many2One
    ShipFromWarehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                                  nullable=True,
                                  info=dict(label="Ship From Warehouse",
                                            selectId="Id", selectKey="Name",
                                            depth=1))
    ShipFromWarehouse = relationship("Warehouse",
                                     primaryjoin="Warehouse.Id==CustomerStore.ShipFromWarehouse_Id")

    OrderDateInterval = Column(Integer, nullable=True,
                               info=dict(label="Order/Start Date Interval Days",
                                         validator=["ZeroPositive"]))

    StartDateInterval = Column(Integer, nullable=True,
                               info=dict(label="Start/Cancel Date Interval Days",
                                         validator=["ZeroPositive"]))

    # One2One side of CustomerProcessingGroup
    ProcessingGroups = relationship("CustomerProcessingGroup", uselist=False,
                                    back_populates="ItemCustomerStore",
                                    primaryjoin="CustomerProcessingGroup.ItemCustomerStore_Id==CustomerStore.Id",
                                    cascade="all, delete-orphan",
                                    info=dict(label="Processing Groups",
                                              gridSubTable=True,
                                              dumpFields=["Id"]))

    # One2Many
    Addresses = relationship("CustomerStoreAddress", uselist=True,
                             backref="ItemCustomerStore",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"],
                                       requiredEntry=dict(type="Type.Type",
                                                          value=["MAIN"],
                                                          min=1),
                                       depth=1))

    # One2Many
    Phones = relationship("CustomerStorePhone", uselist=True,
                          backref="ItemCustomerStore",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Emails = relationship("CustomerStoreEmail", uselist=True,
                          backref="ItemCustomerStore",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Contacts = relationship("CustomerStoreContact", uselist=True,
                            backref="ItemCustomerStore",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==CustomerStore.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CustomerStore.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of ContractPriceDiscount
    # uselist=False - this is just used in validate_delete
    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                               back_populates="Store",
                               primaryjoin="ContractPriceDiscount.Store_Id==CustomerStore.Id",
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
            message = f"Cannot Delete. {tables} linked to this Customer Store"

        return is_ok, message


Index("CustomerStore_Index1", CustomerStore.Company_Id,
      CustomerStore.ItemCustomer_Id,
      CustomerStore.Store, unique=True)
Index("CustomerStore_Index2", CustomerStore.Company_Id,
      CustomerStore.InterchangeNumber, unique=False)
Index("CustomerStore_Index3", CustomerStore.Company_Id,
      CustomerStore.CustomerNumber, unique=False)
Index("CustomerStore_Index4", CustomerStore.Company_Id,
      CustomerStore.Type_Id, unique=False)
Index("CustomerStore_Index5", CustomerStore.Company_Id,
      CustomerStore.Class_Id, unique=False)
Index("CustomerStore_Index6", CustomerStore.Company_Id,
      CustomerStore.Group_Id, unique=False)
Index("CustomerStore_Index7", CustomerStore.Company_Id,
      CustomerStore.Region_Id, unique=False)


def on_customer_store_update(mapper, connection, target):
    inactive = getattr(target, "Inactive")
    if inactive and getattr(target, "InactiveTimeStamp") is None:
        setattr(target, "InactiveTimeStamp", datetime.utcnow())
        setattr(target, "InactiveOpId_Id", get_current_uid())
    elif not inactive and getattr(target, "InactiveTimeStamp") is not None:
        setattr(target, "InactiveTimeStamp", None)
        setattr(target, "InactiveOpId_Id", None)


event.listen(CustomerStore, "before_update", on_customer_store_update)  # Mapper Event
event.listen(CustomerStore, "before_insert", on_customer_store_update)  # mapper Event

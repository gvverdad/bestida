from datetime import datetime

from sqlalchemy import event
from sqlalchemy import (Column, ForeignKey, Integer, DateTime,
                        Index, String, Boolean, func, select, Table)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from ...functions import (get_locale_choices, get_default_locale,
                          get_timezone_choices, get_default_timezone)

from .....security.policy import get_current_uid

keyword_customer_table = Table("keyword_customer", Model.metadata,
                               Column("keyword_id", Integer, ForeignKey("CustomerKeywords.Id")),
                               Column("customer_id", Integer, ForeignKey("Customers.Id"))
                               )
keyword_customer_table.__versioned__ = {}  # Mark the secondary table for versioning

brand_customer_table = Table("brand_customer", Model.metadata,
                             Column("brand_id", Integer, ForeignKey("ProductBrands.Id")),
                             Column("customer_id", Integer, ForeignKey("Customers.Id"))
                             )
brand_customer_table.__versioned__ = {}  # Mark the secondary table for versioning

class Customer(Model):
    __versioned__ = {}
    __tablename__ = "Customers"
    __table_args__ = dict(info=dict(label="Customers",
                                    companyField="Company_Id",
                                    stepperTitleFields=["Account", "Name"],
                                    keyPaths=["Company_Id"],
                                    key="Account",
                                    hybrids=[dict(name="number_of_warehouses",
                                                  label="Warehouses",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="number_of_stores",
                                                  label="Stores",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             ]
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==Customer.Company_Id")

    Account = Column(String(16), nullable=False,
                     info=dict(label="Account Code", case="uppercase",
                               documents=[dict(program="DocumentCustomerAccount",
                                              params=dict(account="."))
                                         ],
                               selectId="Id",
                               selectKey="Account",
                               selectColumn="Account",
                               selectFormat=["Account", "Name"],
                               selectTable="Customers",
                               ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))
    ShortName = Column(String(32), info=dict(label="Short Name"))
    TradeName = Column(String(32), info=dict(label="Trade Name"))

    # Many2Many
    Keywords = relationship("CustomerKeyword", secondary=keyword_customer_table,
                            back_populates="Customers",
                            info=dict(label="Search Keywords",
                                      selectId="Id", selectKey="Keyword",
                                      depth=1))

    InterchangeNumber = Column(String(32), info=dict(label="Interchange Number"))
    CustomerNumber = Column(String(32), info=dict(label="Customer Number"))

    InterCompany = Column(Boolean, default=False, info=dict(label="InterCompany Account"))

    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User", primaryjoin="User.Id==Customer.InactiveOpId_Id")
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp", modifiable=False))

    Locale = Column(String(8), nullable=False, default=get_default_locale,
                    info=dict(label="Locale",
                              choices=get_locale_choices,  # server getter
                              choices_getter="getLocaleList")) # client getter

    Timezone = Column(String(32), nullable=False, default=get_default_timezone,
                      info=dict(label="Timezone",
                                choices=get_timezone_choices,  # server getter
                                choices_getter="getTimezoneList")) # client getter

    # Many2One
    Region_Id = Column(Integer, ForeignKey("CustomerRegions.Id"),
                       nullable=False,
                       info=dict(label="Region", selectId="Id",
                                 selectKey="Description",
                                 depth=1))
    Region = relationship("CustomerRegion", primaryjoin="CustomerRegion.Id==Customer.Region_Id")

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CustomerTypes.Id"),
                     nullable=False, info=dict(label="Type", selectId="Id",
                                               selectKey="Description",
                                               depth=1))
    Type = relationship("CustomerType", primaryjoin="CustomerType.Id==Customer.Type_Id")

    # Many2One
    Class_Id = Column(Integer, ForeignKey("CustomerClasses.Id"), nullable=False,
                      info=dict(label="Class", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Class = relationship("CustomerClass", primaryjoin="CustomerClass.Id==Customer.Class_Id")

    # Many2One
    Group_Id = Column(Integer, ForeignKey("CustomerGroups.Id"), nullable=False,
                      info=dict(label="Group", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Group = relationship("CustomerGroup", primaryjoin="CustomerGroup.Id==Customer.Group_Id")

    AllowDeliveries = Column(Boolean, default=False, info=dict(label="Allow Deliveries"))

    # Many2One
    PriceBand_Id = Column(Integer, ForeignKey("CustomerPriceBands.Id"), nullable=True,
                          info=dict(label="Price Band",
                                    selectId="Id", selectKey="Description",
                                    depth=1))
    PriceBand = relationship("CustomerPriceBand",
                             primaryjoin="CustomerPriceBand.Id==Customer.PriceBand_Id")

    # Many2One
    Priority_Id = Column(Integer, ForeignKey("CustomerPriorities.Id"), nullable=False,
                         info=dict(label="Priority", selectId="Id",
                                   selectKey="Description",
                                   selectFormat=["Description", "Priority"],
                                   depth=1))
    Priority = relationship("CustomerPriority", primaryjoin="CustomerPriority.Id==Customer.Priority_Id")

    # Many2One
    Carrier_Id = Column(Integer, ForeignKey("Carriers.Id"), nullable=False,
                        info=dict(label="Carrier", selectId="Id",
                                  selectKey="Name",
                                  depth=1))
    Carrier = relationship("Carrier", primaryjoin="Carrier.Id==Customer.Carrier_Id")

    ShipmentPercentage = Column(Integer, nullable=False, default=100,
                                info=dict(label="Shipment Percentage",
                                          numberType="percent",
                                          min=1, max=100))
    # Many2One
    ShipFromWarehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                                  nullable=False,
                                  info=dict(label="Ship From Warehouse",
                                            selectId="Id", selectKey="Name",
                                            depth=1))
    ShipFromWarehouse = relationship("Warehouse",
                                     primaryjoin="Warehouse.Id==Customer.ShipFromWarehouse_Id")

    OrderDateInterval = Column(Integer, default=0, nullable=False,
                               info=dict(label="Order/Start Date Interval Days",
                                         validator=["ZeroPositive"]))

    StartDateInterval = Column(Integer, default=0, nullable=False,
                               info=dict(label="Start/Cancel Date Interval Days",
                                         validator=["ZeroPositive"]))

    # Many2Many
    Brands = relationship("ProductBrand", secondary=brand_customer_table,
                          back_populates="Customers",
                          info=dict(label="Customer Brands",
                                    selectId="Id", selectKey="Brand",
                                    nullable=True,
                                    depth=1))

    # One2One side of CustomerAccounts
    CustomerAccount = relationship("CustomerAccount", uselist=False,
                                   back_populates="ItemCustomer",
                                   primaryjoin="CustomerAccount.ItemCustomer_Id==Customer.Id",
                                   cascade="all, delete-orphan",
                                   info=dict(label="Customer Account",
                                             gridSubTable=True,
                                             dumpFields=["Id"]))

    # One2One side of CustomerProcessingGroup
    ProcessingGroups = relationship("CustomerProcessingGroup", uselist=False,
                                    back_populates="ItemCustomer",
                                    primaryjoin="CustomerProcessingGroup.ItemCustomer_Id==Customer.Id",
                                    cascade="all, delete-orphan",
                                    info=dict(label="Processing Groups",
                                              gridSubTable=True,
                                              dumpFields=["Id"]))

    # One2Many
    Addresses = relationship("CustomerAddress", uselist=True,
                             backref="ItemCustomer",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"],
                                       requiredEntry=dict(type="AddressType.Type",
                                                          value=["MAIN"],
                                                          min=1),
                                       depth=1))

    # One2Many
    Phones = relationship("CustomerPhone", uselist=True, backref="ItemCustomer",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Emails = relationship("CustomerEmail", uselist=True, backref="ItemCustomer",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Contacts = relationship("CustomerContact", uselist=True,
                            backref="ItemCustomer",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # One2Many
    Warehouses = relationship("CustomerWarehouse", uselist=True,
                              backref="ItemCustomer",
                              cascade="all, delete-orphan",
                              info=dict(dumpFields=["Id"]))

    # One2Many
    Stores = relationship("CustomerStore", uselist=True, backref="ItemCustomer",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User",
                              primaryjoin="User.Id==Customer.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp",
                                       modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User",
                                primaryjoin="User.Id==Customer.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp",
                                         modifiable=False))

    # One2Many side of SalesOrderHeader
    # uselist=False - this is just used in validate_delete
    SalesOrders = relationship("SalesOrderHeader", uselist=False,
                               back_populates="Customer",
                               primaryjoin="SalesOrderHeader.Customer_Id==Customer.Id",
                               info=dict(hidden=True, dump=False))

    # One2Many side of ContractPriceDiscount
    # uselist=False - this is just used in validate_delete
    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                               back_populates="Customer",
                               primaryjoin="ContractPriceDiscount.Customer_Id==Customer.Id",
                               info=dict(hidden=True, dump=False))

    @hybrid_property
    def number_of_warehouses(self):
        return len(self.Warehouses)

    @number_of_warehouses.expression
    def number_of_warehouses(cls):
        from .CustomerWarehouses import CustomerWarehouse

        return select([func.count()]).\
            where(CustomerWarehouse.ItemCustomer_Id == cls.Id).as_scalar()

    @hybrid_property
    def number_of_stores(self):
        return len(self.Stores)

    @number_of_stores.expression
    def number_of_stores(cls):
        from .CustomerStores import CustomerStore

        return select([func.count()]).\
            where(CustomerStore.ItemCustomer_Id == cls.Id).as_scalar()

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.SalesOrders is not None:
            is_ok = False
            tables = "SalesOrder Headers"

        if self.ContractPrices is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Contract Price/Discounts"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Customer"

        return is_ok, message


Index("Customer_Index1", Customer.Company_Id, Customer.Account, unique=True)
Index("Customer_Index2", Customer.Company_Id,
      Customer.InterchangeNumber, unique=False)
Index("Customer_Index3", Customer.Company_Id,
      Customer.CustomerNumber, unique=False)
Index("Customer_Index4", Customer.Company_Id, Customer.Type_Id, unique=False)
Index("Customer_Index5", Customer.Company_Id, Customer.Class_Id, unique=False)
Index("Customer_Index6", Customer.Company_Id, Customer.Group_Id, unique=False)
Index("Customer_Index7", Customer.Company_Id, Customer.Region_Id, unique=False)


def on_customer_update(mapper, connection, target):
    inactive = getattr(target, "Inactive")
    if inactive and getattr(target, "InactiveTimeStamp") is None:
        setattr(target, "InactiveTimeStamp", datetime.utcnow())
        setattr(target, "InactiveOpId_Id", get_current_uid())
    elif not inactive and getattr(target, "InactiveTimeStamp") is not None:
        setattr(target, "InactiveTimeStamp", None)
        setattr(target, "InactiveOpId_Id", None)


event.listen(Customer, "before_update", on_customer_update)  # Mapper Event
event.listen(Customer, "before_insert", on_customer_update)  # mapper Event

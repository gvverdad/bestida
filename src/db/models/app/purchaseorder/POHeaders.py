from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, String, DateTime, Date, Boolean,
                        Index, Numeric, event, func, select)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import get_currency_choices


class POHeader(Model):
    __versioned__ = {}
    __tablename__ = "POHeaders"
    __table_args__ = dict(info=dict(label="PO Header", desc="Header",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="PONumber",
                                    hybrids=[dict(name="number_of_lines",
                                                  label="Lines",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_ordered_qty",
                                                  label="Total Ordered Qty",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_open_qty",
                                                  label="Total Open Qty",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_received_qty",
                                                  label="Total Received Qty",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_returned_qty",
                                                  label="Total Returned Qty",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_cancelled_qty",
                                                  label="Total Cancelled Qty",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_ordered_value",
                                                  label="Total Ordered Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_ordered_valueinc",
                                                  label="Total Ordered ValueInc",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_open_value",
                                                  label="Total Open Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_received_value",
                                                  label="Total Received Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_despatched_value",
                                                  label="Total Despatched Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_returned_value",
                                                  label="Total Returned Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_cancelled_value",
                                                  label="Total Cancelled Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_tax",
                                                  label="Total Tax",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
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
    Company = relationship("Company", primaryjoin="Company.Id==POHeader.Company_Id")

    PONumber = Column(String(22), nullable=False,
                      info=dict(label="PO Number", case="uppercase",
                                documents=[dict(program="DocumentPO",
                                               params=dict(poNumber="PONumber"))
                                          ]
                                ))

    # Many2One
    Supplier_Id = Column(Integer, ForeignKey("Suppliers.Id"), nullable=False,
                         info=dict(label="Account",
                                   depth=1,
                                   selectId="Id",
                                   selectKey="Name",
                                   selectFormat=["Account",
                                                 "Name",
                                                 "SupplierAccount.Currency",
                                                 "POType"],
                                   selectTableFieldValue=[{"field": "Inactive", "value": False}]
                                   ))
    Supplier = relationship("Supplier",
                            primaryjoin="Supplier.Id==POHeader.Supplier_Id")

    # Many2One
    SupplierStore_Id = Column(Integer, ForeignKey("SupplierStores.Id"), nullable=True,
                              info=dict(label="Store",
                                        depth=1,
                                        requiredIf="Supplier.AllowSupplies == false",
                                        selectId="Id",
                                        selectKey="Name",
                                        selectFormat=["ItemSupplier.Account",
                                                      "Store",
                                                      "Name",
                                                      "ItemSupplier.SupplierAccount.Currency",
                                                      "POType"],
                                        selectField="ItemSupplier_Id",
                                        selectFieldValue="Supplier.Id",
                                        selectTableFieldValue=[{"field": "Inactive", "value": False},
                                                               {"field": "AllowSupplies", "value": True}]
                                        ))
    SupplierStore = relationship("SupplierStore",
                                 primaryjoin="SupplierStore.Id==POHeader.SupplierStore_Id")

    # Many2One
    Event_Id = Column(Integer, ForeignKey("POEventHeaders.Id"), nullable=False,
                      info=dict(label="Event Format",
                                depth=1,
                                selectId="Id",
                                selectKey="Format",
                                selectFormat=["Format", "Description"]
                                ))
    Event = relationship("POEventHeader",
                         primaryjoin="POEventHeader.Id==POHeader.Event_Id")

    # Many2One
    Warehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                          nullable=True,
                          info=dict(label="Deliver To Warehouse",
                                    requiredIf="Customer == null",
                                    selectId="Id", selectKey="Name", depth=1))
    Warehouse = relationship("Warehouse",
                             primaryjoin="Warehouse.Id==POHeader.Warehouse_Id")

    # Many2One
    Customer_Id = Column(Integer, ForeignKey("Customers.Id"), nullable=True,
                         info=dict(label="OR Deliver To Customer",
                                   depth=1,
                                   selectId="Id",
                                   selectKey="Name",
                                   selectFormat=["Account", "Name"],
                                   selectTableFieldValue=[{"field": "Inactive", "value": False}]
                                   ))
    Customer = relationship("Customer",
                            primaryjoin="Customer.Id==POHeader.Customer_Id")

    # Many2One
    DeliverVia_Id = Column(Integer, ForeignKey("CustomerWarehouses.Id"),
                           nullable=True,
                           info=dict(label="Deliver To Customer Warehouse",
                                     depth=1,
                                     selectId="Id",
                                     selectKey="Name",
                                     selectFormat=["ItemCustomer.Account",
                                                   "Warehouse",
                                                   "Name"],
                                     selectField="ItemCustomer_Id",
                                     selectFieldValue="Customer.Id",
                                     selectTableFieldValue=[{"field": "Inactive", "value": False}],
                                     ))
    DeliverVia = relationship("CustomerWarehouse",
                              primaryjoin="CustomerWarehouse.Id==POHeader.DeliverVia_Id")

    # Many2One
    Store_Id = Column(Integer, ForeignKey("CustomerStores.Id"), nullable=True,
                      info=dict(label="Deliver To Customer Store",
                                depth=1,
                                requiredIf="Customer != null and Customer.AllowDeliveries == false",
                                selectId="Id",
                                selectKey="Name",
                                selectFormat=["ItemCustomer.Account",
                                              "Store",
                                              "Name"],
                                selectField="ItemCustomer_Id",
                                selectFieldValue="Customer.Id",
                                selectTableFieldValue=[{"field": "Inactive", "value": False},
                                                       {"field": "AllowDeliveries", "value": True}],
                                ))
    Store = relationship("CustomerStore",
                         primaryjoin="CustomerStore.Id==POHeader.Store_Id")

    # Many2One
    Type_Id = Column(Integer, ForeignKey("POTypes.Id"),
                     nullable=False, info=dict(label="Order Type", selectId="Id",
                                               selectKey="Description",
                                               depth=1))
    Type = relationship("POType", primaryjoin="POType.Id==POHeader.Type_Id")

    Confirmed = Column(Boolean, default=True, info=dict(label="Confirmed"))
    ConfirmedOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                              info=dict(label="Confirmed By", modifiable=False))
    ConfirmedOpId = relationship("User", remote_side="User.Id",
                                 primaryjoin="User.Id==POHeader.ConfirmedOpId_Id",
                                 info=dict(modifiable=False))
    ConfirmedTimeStamp = Column(DateTime, default=None, nullable=True,
                                info=dict(label="Confirmed Timestamp",
                                          modifiable=False))

    PODate = Column(Date(), nullable=False, default=datetime.utcnow,
                    info=dict(label="PO Date"))

    StartDate = Column(Date(), nullable=True,
                       info=dict(label="Start Events Date"))

    EarlyDate = Column(Date(), nullable=True,
                       info=dict(label="Early Delivery Date",
                                 modifiable=False))

    LatestDate = Column(Date(), nullable=True,
                        info=dict(label="Latest Delivery Date",
                                  modifiable=False))

    RequisitionNumber = Column(String(22), nullable=True,
                               info=dict(label="Requisition Number",
                                         case="uppercase"))

    Department = Column(String(32), nullable=True, info=dict(label="Department",
                                                             case="uppercase"))

    # Many2One
    Season_Id = Column(Integer, ForeignKey("ProductSeasons.Id"),
                       nullable=False, info=dict(label="Order Season", selectId="Id",
                                                 selectKey="Description",
                                                 depth=1))
    Season = relationship("ProductSeason",
                          primaryjoin="ProductSeason.Id==POHeader.Season_Id")

    # Many2One
    TradingTerms_Id = Column(Integer, ForeignKey("TradingTerms.Id"), nullable=False,
                             info=dict(label="Trading Terms", selectId="Id",
                                       selectKey="Description",
                                       depth=1))
    TradingTerms = relationship("TradingTerm",
                                primaryjoin="TradingTerm.Id==POHeader.TradingTerms_Id")

    Currency = Column(String(3), nullable=False, default="AUD",
                      info=dict(label="Currency",
                                modifiable=False,
                                choices=get_currency_choices,
                                choices_getter="getCurrencyList"))

    # Exchange Rate From Base Currency
    CurrencyRate = Column(Numeric(19, 4), nullable=True, default=1,
                          info=dict(label="Exchange Rate",
                                    modifiable=False))

    # One2Many
    Details = relationship("PODetail", uselist=True,
                           backref="ItemPOHeader",
                           cascade="all, delete-orphan",
                           info=dict(dumpFields=["Id"]))

    # One2Many
    Addresses = relationship("POAddress", uselist=True,
                             backref="ItemPOHeader",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"]))

    # One2Many
    Comments = relationship("POComment", uselist=True,
                            backref="ItemPOHeader",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==POHeader.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==POHeader.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    @hybrid_property
    def number_of_lines(self):
        return len(self.Details)

    @number_of_lines.expression
    def number_of_lines(cls):
        from .PODetails import PODetail

        return select([func.count()]).\
            where(PODetail.ItemPOHeader_Id == cls.Id).as_scalar()

    @hybrid_property
    def total_ordered_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status not in ["Returned", "Cancelled"])

    @total_ordered_qty.expression
    def total_ordered_qty(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_qty)]).\
            where(PODetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(PODetail.Status.notin_(["Returned", "Cancelled"])).\
            as_scalar()

    @hybrid_property
    def total_open_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Open")

    @total_open_qty.expression
    def total_open_qty(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_qty)]).\
            where(PODetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(PODetail.Status == "Open").\
            as_scalar()

    @hybrid_property
    def total_received_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Received")

    @total_received_qty.expression
    def total_received_qty(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_qty)]).\
            where(PODetail.ItemPOHeader_Id == cls.Id).\
            where(PODetail.Status == "Received").\
            as_scalar()

    @hybrid_property
    def total_returned_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Returned")

    @total_returned_qty.expression
    def total_returned_qty(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_qty)]).\
            where(PODetail.ItemPOHeader_Id == cls.Id).\
            where(PODetail.Status == "Returned").\
            as_scalar()

    @hybrid_property
    def total_cancelled_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Cancelled")

    @total_cancelled_qty.expression
    def total_cancelled_qty(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_qty)]).\
            where(PODetail.ItemPOHeader_Id == cls.Id).\
            where(PODetail.Status == "Cancelled").\
            as_scalar()

    @hybrid_property
    def total_ordered_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status not in ["Returned", "Cancelled"])

    @total_ordered_value.expression
    def total_ordered_value(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_value)]).\
            where(PODetail.ItemPOHeader_Id == cls.Id).\
            where(PODetail.Status.notin_(["Returned", "Cancelled"])).\
            as_scalar()

    @hybrid_property
    def total_ordered_valueinc(self):
        return sum(line.total_valueinc for line in self.Details
                   if line.Status not in ["Returned", "Cancelled"])

    @total_ordered_valueinc.expression
    def total_ordered_valueinc(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_valueinc)]).\
            where(PODetail.ItemPOHeader_Id == cls.Id).\
            where(PODetail.Status.notin_(["Returned", "Cancelled"])).\
            as_scalar()

    @hybrid_property
    def total_open_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Open")

    @total_open_value.expression
    def total_open_value(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_value)]).\
            where(PODetail.ItemPOHeader_Id == cls.Id).\
            where(PODetail.Status == "Open").\
            as_scalar()

    @hybrid_property
    def total_received_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Received")

    @total_received_value.expression
    def total_received_value(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_value)]).\
            where(PODetail.ItemPOHeader_Id == cls.Id).\
            where(PODetail.Status == "Received").\
            as_scalar()

    @hybrid_property
    def total_returned_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Returned")

    @total_returned_value.expression
    def total_returned_value(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_value)]).\
            where(PODetail.ItemPOHeader_Id == cls.Id).\
            where(PODetail.Status == "Returned").\
            as_scalar()

    @hybrid_property
    def total_cancelled_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Cancelled")

    @total_cancelled_value.expression
    def total_cancelled_value(cls):
        from .PODetails import PODetail

        return select([func.sum(PODetail.total_value)]).\
            where(PODetail.ItemPOHeader_Id == cls.Id).\
            where(PODetail.Status == "Cancelled").\
            as_scalar()

    @hybrid_property
    def total_tax(self):
        return self.total_ordered_valueinc - self.total_ordered_value

    @total_tax.expression
    def total_tax(cls):
        return cls.total_ordered_valueinc - cls.total_ordered_value


Index("POHeader_Index1", POHeader.Company_Id, POHeader.PONumber, unique=True)

Index("POHeader_Index2", POHeader.Company_Id,
      POHeader.Supplier_Id, POHeader.SupplierStore_Id,
      POHeader.PONumber, unique=True)

Index("POHeader_Index3", POHeader.Company_Id, POHeader.Confirmed,
      POHeader.PONumber, unique=True)


def on_po_header_insert(mapper, connection, target):
    supplier = getattr(target, "Supplier")
    setattr(target, "Currency", supplier.SupplierAccount.Currency)

    confirmed = getattr(target, "Confirmed")
    if confirmed and getattr(target, "ConfirmedTimeStamp") is None:
        setattr(target, "ConfirmedTimeStamp", datetime.utcnow())
        setattr(target, "ConfirmedOpId_Id", get_current_uid())
    elif not confirmed and getattr(target, "ConfirmedTimeStamp") is not None:
        setattr(target, "ConfirmedTimeStamp", None)
        setattr(target, "ConfirmedOpId_Id", None)


def on_po_header_update(mapper, connection, target):
    confirmed = getattr(target, "Confirmed")
    if confirmed and getattr(target, "ConfirmedTimeStamp") is None:
        setattr(target, "ConfirmedTimeStamp", datetime.utcnow())
        setattr(target, "ConfirmedOpId_Id", get_current_uid())
    elif not confirmed and getattr(target, "ConfirmedTimeStamp") is not None:
        setattr(target, "ConfirmedTimeStamp", None)
        setattr(target, "ConfirmedOpId_Id", None)


def on_po_header_delete(mapper, connection, target):
    pass


event.listen(POHeader, "before_insert", on_po_header_insert)  # Mapper Event
event.listen(POHeader, "before_update", on_po_header_update)  # Mapper Event
event.listen(POHeader, "after_delete", on_po_header_delete)  # Mapper Event

from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, String, DateTime, Date, Boolean,
                        Index, Numeric, Text, event, func, select)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import get_currency_choices


class SalesOrderHeader(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderHeaders"
    __table_args__ = dict(info=dict(label="Sales Order Header", desc="Header",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="OrderNumber",
                                    crud_constraint=dict(
                                        delete=dict(condition=(f"total_allocated_qty + total_picked_qty + "
                                                               f"total_packed_qty + total_despatched_qty + "
                                                               f"total_returned_qty > 0"),
                                                    message="Cannot Delete Order. ALL Lines must be Open or Cancelled")
                                    ),
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
                                             dict(name="total_allocated_qty",
                                                  label="Total Allocated Qty",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_picked_qty",
                                                  label="Total Picked Qty",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_packed_qty",
                                                  label="Total Packed Qty",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_despatched_qty",
                                                  label="Total Despatched Qty",
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
                                             dict(name="total_allocated_value",
                                                  label="Total Allocated Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_picked_value",
                                                  label="Total Picked Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_packed_value",
                                                  label="Total Packed Value",
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
                                             dict(name="total_extras_value",
                                                  label="Total Extras Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_extras_valueinc",
                                                  label="Total Extras ValueInc",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_value",
                                                  label="Total Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_valueinc",
                                                  label="Total ValueInc",
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
    Company = relationship("Company", primaryjoin="Company.Id==SalesOrderHeader.Company_Id")

    OrderNumber = Column(String(22), nullable=False,
                         info=dict(label="Order Number", case="uppercase",
                                   documents=[dict(program="DocumentSalesOrder",
                                                  params=dict(orderNumber="."))
                                             ]
                                   ))
    # Many2One
    Customer_Id = Column(Integer, ForeignKey("Customers.Id"), nullable=False,
                         info=dict(label="Account",
                                   depth=1,
                                   selectId="Id",
                                   selectKey="Name",
                                   selectFormat=["Account", "Name"],
                                   selectTableFieldValue=[{"field": "Inactive", "value": False}]
                                   ))
    Customer = relationship("Customer", primaryjoin="Customer.Id==SalesOrderHeader.Customer_Id")

    # Many2One
    DeliverVia_Id = Column(Integer, ForeignKey("CustomerWarehouses.Id"),
                           nullable=True,
                           info=dict(label="Deliver Via",
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
    DeliverVia = relationship("CustomerWarehouse", primaryjoin="CustomerWarehouse.Id==SalesOrderHeader.DeliverVia_Id")

    # Many2One
    Store_Id = Column(Integer, ForeignKey("CustomerStores.Id"), nullable=True,
                      info=dict(label="Store",
                                depth=1,
                                requiredIf="Customer.AllowDeliveries == false",
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
    Store = relationship("CustomerStore", primaryjoin="CustomerStore.Id==SalesOrderHeader.Store_Id")

    PurchaseOrder = Column(String(22), nullable=True, info=dict(label="Customer PO Number",
                                                                case="uppercase"))

    Contract = Column(String(32), nullable=True, info=dict(label="Contract",
                                                           case="uppercase"))

    Department = Column(String(32), nullable=True, info=dict(label="Department",
                                                             case="uppercase"))

    Confirmed = Column(Boolean, default=True, info=dict(label="Confirmed"))
    ConfirmedOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                              info=dict(label="Confirmed By", modifiable=False))
    ConfirmedOpId = relationship("User", remote_side="User.Id",
                                 primaryjoin="User.Id==SalesOrderHeader.ConfirmedOpId_Id",
                                 info=dict(modifiable=False))
    ConfirmedTimeStamp = Column(DateTime, default=None, nullable=True,
                                info=dict(label="Confirmed Timestamp",
                                          modifiable=False))

    OrderDate = Column(Date(), nullable=False, default=datetime.utcnow,
                       info=dict(label="Order Date"))

    AsOfDate = Column(Date(), nullable=True, info=dict(label="Invoice As-of Date"))

    StartDate = Column(Date(), nullable=True,
                       info=dict(label="Start Delivery Date"))
    CancelDate = Column(Date(), nullable=True,
                        info=dict(label="Cancel Delivery Date"))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SalesOrderTypes.Id"),
                     nullable=False, info=dict(label="Order Type", selectId="Id",
                                               selectKey="Description",
                                               depth=1))
    Type = relationship("SalesOrderType", primaryjoin="SalesOrderType.Id==SalesOrderHeader.Type_Id")

    # Many2One
    Source_Id = Column(Integer, ForeignKey("SalesOrderSources.Id"),
                       nullable=False, info=dict(label="Order Source", selectId="Id",
                                                 selectKey="Description",
                                                 depth=1))
    Source = relationship("SalesOrderSource", primaryjoin="SalesOrderSource.Id==SalesOrderHeader.Source_Id")

    # Many2One
    Season_Id = Column(Integer, ForeignKey("ProductSeasons.Id"),
                       nullable=False, info=dict(label="Order Season", selectId="Id",
                                                 selectKey="Description",
                                                 depth=1))
    Season = relationship("ProductSeason",
                          primaryjoin="ProductSeason.Id==SalesOrderHeader.Season_Id")

    # Many2One
    Priority_Id = Column(Integer, ForeignKey("CustomerPriorities.Id"), nullable=False,
                         info=dict(label="Priority", selectId="Id",
                                   selectKey="Description",
                                   selectFormat=["Description", "Priority"],
                                   depth=1))
    Priority = relationship("CustomerPriority",
                            primaryjoin="CustomerPriority.Id==SalesOrderHeader.Priority_Id")

    # Many2One
    Carrier_Id = Column(Integer, ForeignKey("Carriers.Id"), nullable=False,
                        info=dict(label="Carrier", selectId="Id",
                                  selectKey="Name", depth=1))
    Carrier = relationship("Carrier",
                           primaryjoin="Carrier.Id==SalesOrderHeader.Carrier_Id")

    # Many2One
    TradingTerms_Id = Column(Integer, ForeignKey("TradingTerms.Id"), nullable=False,
                             info=dict(label="Trading Terms", selectId="Id",
                                       selectKey="Description",
                                       depth=1))
    TradingTerms = relationship("TradingTerm",
                                primaryjoin="TradingTerm.Id==SalesOrderHeader.TradingTerms_Id")

    TradeDiscount = Column(Numeric(8, 4), default=0, nullable=True,
                           info=dict(label="Trade Discount Percentage",
                                     numberType="percent",  # number, currency, percent, string
                                     validator=["ZeroPositive"]))

    Currency = Column(String(3), nullable=False, default="AUD",
                      info=dict(label="Currency",
                                modifiable=False,
                                choices=get_currency_choices,
                                choices_getter="getCurrencyList"))

    # Exchange Rate From Base Currency
    CurrencyRate = Column(Numeric(19, 4), nullable=True, default=1,
                          info=dict(label="Exchange Rate", modifiable=False))

    AcknowledgeOrder = Column(Boolean, default=False,
                              info=dict(label="Acknowledge Order",
                                        actionOn="{" +
                                           "\"baseFieldName\": \"Calculated\"," +
                                           "\"true\": {\"onFields\":[\"Email\", \"EmailCC\", \"EmailBCC\", \"EmailSubject\"],\"offFields\":[]}," +
                                           "\"false\": {\"onFields\": [], \"offFields\": [\"Email\", \"EmailCC\", \"EmailBCC\", \"EmailSubject\"]}," +
                                           "}"
                                        ))

    Email = Column(Text, nullable=True,
                   info=dict(label="List of Emails",
                             listFormat=True,
                             requiredIf="AcknowledgeOrder == true",
                             validator=["Email"]))
    EmailCC = Column(Text, info=dict(label="List of CC Emails",
                                     listFormat=True, validator=["Email"]))
    EmailBCC = Column(Text, info=dict(label="List of BCC Emails",
                                      listFormat=True, validator=["Email"]))

    # RFC 2822 - max of 78 characters
    EmailSubject = Column(String(78),
                          info=dict(label="Email Subject",
                                    requiredIf="AcknowledgeOrder == true",
                                    ))

    # One2Many
    Details = relationship("SalesOrderDetail", uselist=True,
                           backref="ItemSalesOrderHeader",
                           cascade="all, delete-orphan",
                           info=dict(dumpFields=["Id"]))

    # One2Many
    Extras = relationship("SalesOrderExtra", uselist=True,
                          backref="ItemSalesOrderHeader",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Addresses = relationship("SalesOrderAddress", uselist=True,
                             backref="ItemSalesOrderHeader",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"]))

    # One2Many
    Comments = relationship("SalesOrderComment", uselist=True,
                            backref="ItemSalesOrderHeader",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Payment Value is Currency Value and Inc GST and Net of Discount
    TotalPaymentValue = Column(Numeric(19, 4), default=0, nullable=True,
                               info=dict(label="Total Payment Value",
                                         numberType="currency",  # number, currency, percent, string
                                         currencyCodeField="Currency",
                                         modifiable=False))
    TotalSubsidizedValue = Column(Numeric(19, 4), default=0, nullable=True,
                                  info=dict(label="Total Subsidized Value",
                                            numberType="currency",  # number, currency, percent, string
                                            currencyCodeField="Currency",
                                            modifiable=False))
    TotalContributionValue = Column(Numeric(19, 4), default=0, nullable=True,
                                    info=dict(label="Total Contribution Value",
                                              numberType="currency",  # number, currency, percent, string
                                              currencyCodeField="Currency",
                                              modifiable=False))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderHeader.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderHeader.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    @hybrid_property
    def number_of_lines(self):
        return len(self.Details)

    @number_of_lines.expression
    def number_of_lines(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.count()]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).as_scalar()

    @hybrid_property
    def total_ordered_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status not in ["Returned", "Cancelled"])

    @total_ordered_qty.expression
    def total_ordered_qty(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_qty)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status.notin_(["Returned", "Cancelled"])).\
            as_scalar()

    @hybrid_property
    def total_open_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Open")

    @total_open_qty.expression
    def total_open_qty(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_qty)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Open").\
            as_scalar()

    @hybrid_property
    def total_allocated_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Allocated")

    @total_allocated_qty.expression
    def total_allocated_qty(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_qty)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Allocated").\
            as_scalar()

    @hybrid_property
    def total_picked_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Picked")

    @total_picked_qty.expression
    def total_picked_qty(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_qty)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Picked").\
            as_scalar()

    @hybrid_property
    def total_packed_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Packed")

    @total_packed_qty.expression
    def total_packed_qty(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_qty)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Packed").\
            as_scalar()

    @hybrid_property
    def total_despatched_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Despatched")

    @total_despatched_qty.expression
    def total_despatched_qty(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_qty)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Despatched").\
            as_scalar()

    @hybrid_property
    def total_returned_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Returned")

    @total_returned_qty.expression
    def total_returned_qty(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_qty)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Returned").\
            as_scalar()

    @hybrid_property
    def total_cancelled_qty(self):
        return sum(line.total_qty for line in self.Details
                   if line.Status == "Cancelled")

    @total_cancelled_qty.expression
    def total_cancelled_qty(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_qty)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Cancelled").\
            as_scalar()

    @hybrid_property
    def total_ordered_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status not in ["Returned", "Cancelled"])

    @total_ordered_value.expression
    def total_ordered_value(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_value)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status.notin_(["Returned", "Cancelled"])).\
            as_scalar()

    @hybrid_property
    def total_ordered_valueinc(self):
        return sum(line.total_valueinc for line in self.Details
                   if line.Status not in ["Returned", "Cancelled"])

    @total_ordered_valueinc.expression
    def total_ordered_valueinc(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_valueinc)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status.notin_(["Returned", "Cancelled"])).\
            as_scalar()

    @hybrid_property
    def total_open_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Open")

    @total_open_value.expression
    def total_open_value(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_value)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Open").\
            as_scalar()

    @hybrid_property
    def total_allocated_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Allocated")

    @total_allocated_value.expression
    def total_allocated_value(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_value)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Allocated").\
            as_scalar()

    @hybrid_property
    def total_picked_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Picked")

    @total_picked_value.expression
    def total_picked_value(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_value)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Picked").\
            as_scalar()

    @hybrid_property
    def total_packed_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Packed")

    @total_packed_value.expression
    def total_packed_value(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_value)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Packed").\
            as_scalar()

    @hybrid_property
    def total_despatched_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Despatched")

    @total_despatched_value.expression
    def total_despatched_value(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_value)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Despatched").\
            as_scalar()

    @hybrid_property
    def total_returned_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Returned")

    @total_returned_value.expression
    def total_returned_value(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_value)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Returned").\
            as_scalar()

    @hybrid_property
    def total_cancelled_value(self):
        return sum(line.total_value for line in self.Details
                   if line.Status == "Cancelled")

    @total_cancelled_value.expression
    def total_cancelled_value(cls):
        from .SalesOrderDetails import SalesOrderDetail

        return select([func.sum(SalesOrderDetail.total_value)]).\
            where(SalesOrderDetail.ItemSalesOrderHeader_Id == cls.Id).\
            where(SalesOrderDetail.Status == "Cancelled").\
            as_scalar()

    @hybrid_property
    def total_extras_value(self):
        return sum(extra.Value for extra in self.Extras)

    @total_extras_value.expression
    def total_extras_value(cls):
        from .SalesOrderExtras import SalesOrderExtra

        return select([func.sum(SalesOrderExtra.Value)]).\
            where(SalesOrderExtra.ItemSalesOrderHeader_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def total_extras_valueinc(self):
        return sum(extra.ValueInc for extra in self.Extras)

    @total_extras_valueinc.expression
    def total_extras_valueinc(cls):
        from .SalesOrderExtras import SalesOrderExtra

        return select([func.sum(SalesOrderExtra.ValueInc)]).\
            where(SalesOrderExtra.ItemSalesOrderHeader_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def total_value(self):
        return self.total_ordered_value + self.total_extras_value

    @total_value.expression
    def total_value(cls):
        return cls.total_ordered_value + cls.total_extras_value

    @hybrid_property
    def total_valueinc(self):
        return self.total_ordered_valueinc + self.total_extras_valueinc

    @total_valueinc.expression
    def total_valueinc(cls):
        return cls.total_ordered_valueinc + cls.total_extras_valueinc

    @hybrid_property
    def total_tax(self):
        return self.total_valueinc - self.total_value

    @total_tax.expression
    def total_tax(cls):
        return cls.total_valueinc - cls.total_value


Index("SalesOrderHeader_Index1", SalesOrderHeader.Company_Id,
      SalesOrderHeader.OrderNumber, unique=True)

Index("SalesOrderHeader_Index2", SalesOrderHeader.Company_Id,
      SalesOrderHeader.Customer_Id, SalesOrderHeader.DeliverVia_Id,
      SalesOrderHeader.Store_Id, unique=False)

Index("SalesOrderHeader_Index3", SalesOrderHeader.Company_Id,
      SalesOrderHeader.Customer_Id,
      SalesOrderHeader.Store_Id, unique=False)

Index("SalesOrderHeader_Index4", SalesOrderHeader.Company_Id,
      SalesOrderHeader.Customer_Id, SalesOrderHeader.PurchaseOrder, unique=False)


def on_order_header_insert(mapper, connection, target):
    cust = getattr(target, "Customer")
    setattr(target, "Currency", cust.CustomerAccount.Currency)
    
    confirmed = getattr(target, "Confirmed")
    if confirmed and getattr(target, "ConfirmedTimeStamp") is None:
        setattr(target, "ConfirmedTimeStamp", datetime.utcnow())
        setattr(target, "ConfirmedOpId_Id", get_current_uid())
    elif not confirmed and getattr(target, "ConfirmedTimeStamp") is not None:
        setattr(target, "ConfirmedTimeStamp", None)
        setattr(target, "ConfirmedOpId_Id", None)


def on_order_header_update(mapper, connection, target):
    confirmed = getattr(target, "Confirmed")
    if confirmed and getattr(target, "ConfirmedTimeStamp") is None:
        setattr(target, "ConfirmedTimeStamp", datetime.utcnow())
        setattr(target, "ConfirmedOpId_Id", get_current_uid())
    elif not confirmed and getattr(target, "ConfirmedTimeStamp") is not None:
        setattr(target, "ConfirmedTimeStamp", None)
        setattr(target, "ConfirmedOpId_Id", None)


def on_order_header_delete(mapper, connection, target):
    pass


event.listen(SalesOrderHeader, "before_insert", on_order_header_insert)  # Mapper Event
event.listen(SalesOrderHeader, "before_update", on_order_header_update)  # Mapper Event
#event.listen(SalesOrderHeader, "after_delete", on_order_header_delete)  # Mapper Event

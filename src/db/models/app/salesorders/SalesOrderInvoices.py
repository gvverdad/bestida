from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Boolean, Date, String,
                        Text, Numeric, Index, select, func)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import get_currency_choices


class SalesOrderInvoice(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderInvoices"
    __table_args__ = dict(info=dict(label="Sales Order Invoice",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="InvoiceNumber",
                                    hybrids=[dict(name="number_of_lines",
                                                  label="Lines",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_qty",
                                                  label="Total Invoiced Qty",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_qty_value",
                                                  label="Total Goods Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_qty_valueinc",
                                                  label="Total Goods ValueInc",
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
    Company = relationship("Company", primaryjoin="Company.Id==SalesOrderInvoice.Company_Id")

    InvoiceNumber = Column(Integer, nullable=False,
                           info=dict(label="Invoice Number",
                                     numberType="string",  # number, currency, percent, string
                                     documents=[dict(program="DocumentInvoice",
                                                    params=dict(invoiceNumber="."))
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
    Customer = relationship("Customer", primaryjoin="Customer.Id==SalesOrderInvoice.Customer_Id")

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
    DeliverVia = relationship("CustomerWarehouse", primaryjoin="CustomerWarehouse.Id==SalesOrderInvoice.DeliverVia_Id")

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
    Store = relationship("CustomerStore", primaryjoin="CustomerStore.Id==SalesOrderInvoice.Store_Id")

    InvoiceDate = Column(Date, nullable=False, default=datetime.utcnow,
                         info=dict(label="Invoice Date"))

    Currency = Column(String(3), nullable=False, default="AUD",
                      info=dict(label="Currency",
                                modifiable=False,
                                choices=get_currency_choices,
                                choices_getter="getCurrencyList"))

    # Many2One
    Carrier_Id = Column(Integer, ForeignKey("Carriers.Id"), nullable=False,
                        info=dict(label="Carrier", selectId="Id",
                                  selectKey="Name", depth=1))
    Carrier = relationship("Carrier",
                           primaryjoin="Carrier.Id==SalesOrderInvoice.Carrier_Id")

    ConsignmentNote = Column(String(22), nullable=True,
                             info=dict(label="Consignment Note",
                                       case="uppercase"))

    Manifest = Column(String(22), nullable=True,
                      info=dict(label="Manifest Number",
                                case="uppercase"))

    CarrierReference = Column(Text, info=dict(label="Carrier Reference"))

    Weight = Column(Numeric(9, 4), default=0, nullable=True,
                    info=dict(label="Despatched Weight in Kilos"))

    Volume = Column(Numeric(9, 4), default=0, nullable=True,
                    info=dict(label="Despatched Volume in Cubic Metres"))

    Containers = Column(Integer, default=0, nullable=True,
                        info=dict(label="Number of Containers"))

    FromPT = Column(Boolean, default=True, nullable=False,
                    info=dict(label="Invoiced From PT", modifiable=False))

    # One2Many
    Details = relationship("SalesOrderInvoiceDetail", uselist=True,
                           backref="ItemSalesOrderInvoice",
                           cascade="all, delete-orphan",
                           info=dict(dumpFields=["Id"]))

    # One2Many
    Extras = relationship("SalesOrderInvoiceExtra", uselist=True,
                          backref="ItemSalesOrderInvoice",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Addresses = relationship("SalesOrderInvoiceAddress", uselist=True,
                             backref="ItemSalesOrderInvoice",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"]))

    # One2Many
    Comments = relationship("SalesOrderInvoiceComment", uselist=True,
                            backref="ItemSalesOrderInvoice",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderInvoice.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderInvoice.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of SalesOrderDetails
    SalesOrderLines = relationship("SalesOrderDetail", uselist=True,
                                   back_populates="Invoice",
                                   info=dict(hidden=True, dump=False))

    @hybrid_property
    def number_of_lines(self):
        return len(self.Details)

    @number_of_lines.expression
    def number_of_lines(cls):
        from .SalesOrderInvoiceDetails import SalesOrderInvoiceDetail

        return select([func.count()]).\
            where(SalesOrderInvoiceDetail.ItemSalesOrderInvoice_Id == cls.Id).as_scalar()

    @hybrid_property
    def total_qty(self):
        return sum(line.ItemSalesOrderSize.Units for line in self.Details)

    @total_qty.expression
    def total_qty(cls):
        from .SalesOrderInvoiceDetails import SalesOrderInvoiceDetail
        from .SalesOrderSizes import SalesOrderSize

        return select([func.sum(SalesOrderSize.Units)]).\
            where(SalesOrderInvoiceDetail.ItemSalesOrderInvoice_Id == cls.Id).\
            where(SalesOrderSize.Id == SalesOrderInvoiceDetail.ItemSalesOrderSize_Id).\
            as_scalar()

    @hybrid_property
    def total_qty_value(self):
        return sum(line.ItemSalesOrderSize.NetValue for line in self.Details)

    @total_qty_value.expression
    def total_qty_value(cls):
        from .SalesOrderInvoiceDetails import SalesOrderInvoiceDetail
        from .SalesOrderSizes import SalesOrderSize

        return select([func.sum(SalesOrderSize.NetValue)]).\
            where(SalesOrderInvoiceDetail.ItemSalesOrderInvoice_Id == cls.Id).\
            where(SalesOrderSize.Id == SalesOrderInvoiceDetail.ItemSalesOrderSize_Id).\
            as_scalar()

    @hybrid_property
    def total_qty_valueinc(self):
        return sum(line.ItemSalesOrderSize.NetValueInc for line in self.Details)

    @total_qty_valueinc.expression
    def total_qty_valueinc(cls):
        from .SalesOrderInvoiceDetails import SalesOrderInvoiceDetail
        from .SalesOrderSizes import SalesOrderSize

        return select([func.sum(SalesOrderSize.NetValueInc)]).\
            where(SalesOrderInvoiceDetail.ItemSalesOrderInvoice_Id == cls.Id).\
            where(SalesOrderSize.Id == SalesOrderInvoiceDetail.ItemSalesOrderSize_Id).\
            as_scalar()

    @hybrid_property
    def total_extras_value(self):
        return sum(extra.Value for extra in self.Extras)

    @total_extras_value.expression
    def total_extras_value(cls):
        from .SalesOrderInvoiceExtras import SalesOrderInvoiceExtra

        return select([func.sum(SalesOrderInvoiceExtra.Value)]).\
            where(SalesOrderInvoiceExtra.ItemSalesOrderInvoice_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def total_extras_valueinc(self):
        return sum(extra.ValueInc for extra in self.Extras)

    @total_extras_valueinc.expression
    def total_extras_valueinc(cls):
        from .SalesOrderInvoiceExtras import SalesOrderInvoiceExtra

        return select([func.sum(SalesOrderInvoiceExtra.ValueInc)]).\
            where(SalesOrderInvoiceExtra.ItemSalesOrderInvoice_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def total_value(self):
        return self.total_qty_value + self.total_extras_value

    @total_value.expression
    def total_value(cls):
        return cls.total_qty_value + cls.total_extras_value

    @hybrid_property
    def total_valueinc(self):
        return self.total_qty_valueinc + self.total_extras_valueinc

    @total_valueinc.expression
    def total_valueinc(cls):
        return cls.total_qty_valueinc + cls.total_extras_valueinc

    @hybrid_property
    def total_tax(self):
        return self.total_valueinc - self.total_value

    @total_tax.expression
    def total_tax(cls):
        return cls.total_valueinc - cls.total_value


Index("SalesOrderInvoice_Index1", SalesOrderInvoice.Company_Id,
      SalesOrderInvoice.InvoiceNumber, unique=True)

Index("SalesOrderInvoice_Index2", SalesOrderInvoice.Company_Id,
      SalesOrderInvoice.InvoiceNumber,
      SalesOrderInvoice.Customer_Id, SalesOrderInvoice.DeliverVia_Id,
      SalesOrderInvoice.Store_Id, unique=True)

Index("SalesOrderInvoice_Index3", SalesOrderInvoice.Company_Id,
      SalesOrderInvoice.Carrier_Id, SalesOrderInvoice.ConsignmentNote,
      unique=False)

Index("SalesOrderInvoice_Index4", SalesOrderInvoice.Company_Id,
      SalesOrderInvoice.Carrier_Id, SalesOrderInvoice.Manifest,
      unique=False)


def on_invoice_insert(mapper, connection, target):
    pass


def on_invoice_update(mapper, connection, target):
    pass


def on_invoice_delete(mapper, connection, target):
    pass

#event.listen(SalesOrderInvoice, "before_insert", on_invoice_insert)  # Mapper Event
#event.listen(SalesOrderInvoice, "before_update", on_invoice_update)  # Mapper Event
#event.listen(SalesOrderInvoice, "after_delete", on_invoice_delete)  # Mapper Event

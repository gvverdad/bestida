from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Numeric, Integer, DateTime)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid


class SalesOrderExtra(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderExtras"
    __table_args__ = dict(info=dict(label="Sales Order Extras", desc="Extras",
                                    crud_constraint=dict(
                                        new=dict(condition="ItemSalesOrderHeader.total_despatched_qty > 0",
                                                 message="Some/All Lines have been Shipped. Cannot Add New Extras"),
                                        copy=dict(condition="ItemSalesOrderHeader.total_despatched_qty > 0",
                                                  message="Some/All Lines have been Shipped. Cannot Copy New Extras"),
                                        edit=dict(condition="ItemSalesOrderHeader.total_despatched_qty > 0",
                                                  message="Some/All Lines have been Shipped. Cannot Edit Extras"),
                                        delete=dict(condition="ItemSalesOrderHeader.total_despatched_qty > 0",
                                                    message="Some/All Lines have been Shipped. Cannot Delete Extras")
                                    ),
                                    hybrids=[dict(name="total_tax",
                                                  label="Total Tax",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemSalesOrderHeader.Currency",
                                                  sortable=True,
                                                  searchable=True)
                                             ]
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True,
                nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One side of SalesOrderHeader
    ItemSalesOrderHeader_Id = Column(Integer, ForeignKey("SalesOrderHeaders.Id"),
                                     info=dict(label="Order Number",
                                               selectId="Id",
                                               selectKey="OrderNumber",
                                               selectFormat=["OrderNumber", "Customer.Account", "PurchaseOrder"],
                                               exceptSchemaFields=["Extras",
                                                                   "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                   "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                   "versions"],
                                               depth=1))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SalesOrderExtraTypes.Id"),
                     nullable=False,
                     info=dict(label="Type", selectId="Id",
                               selectFormat=["Description", "Currency"],
                               selectKey="Description", depth=1))
    Type = relationship("SalesOrderExtraType",
                        primaryjoin="SalesOrderExtraType.Id==SalesOrderExtra.Type_Id")

    # Value is Currency Value and Ex GST
    Value = Column(Numeric(19, 4), default=0, nullable=False,
                   info=dict(label="Value",
                             numberType="currency",  # number, currency, percent, string
                             currencyCodeField="ItemSalesOrderHeader.Currency",
                             validator=["NotZero"]))

    ValueInc = Column(Numeric(19, 4), default=0, nullable=False,
                      info=dict(label="Value Inc Tax",
                                numberType="currency",  # number, currency, percent, string
                                currencyCodeField="ItemSalesOrderHeader.Currency",
                                validator=["NotZero"]))

    # Value has already been charged in one of this Order's Invoice
    # One2One side of SalesOrderInvoiceExtras
    Charged = relationship("SalesOrderInvoiceExtra", uselist=False,
                           back_populates="ItemSalesOrderExtra",
                           primaryjoin="SalesOrderInvoiceExtra.ItemSalesOrderExtra_Id==SalesOrderExtra.Id",
                           cascade="all, delete-orphan",
                           info=dict(label="Charged",
                                     modifiable=False, depth=1))


    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderExtra.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderExtra.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    @hybrid_property
    def total_tax(self):
        return self.ValueInc - self.Value

    @total_tax.expression
    def total_tax(cls):
        return cls.ValueInc - cls.Value

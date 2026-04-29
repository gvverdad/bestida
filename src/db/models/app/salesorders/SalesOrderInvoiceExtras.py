from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Numeric, Integer, DateTime)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid


class SalesOrderInvoiceExtra(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderInvoiceExtras"
    __table_args__ = dict(info=dict(label="Sales Order Invoice Extras",
                                    desc="Extras",
                                    hybrids=[dict(name="total_tax",
                                                  label="Total Tax",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemSalesOrderInvoice.Currency",
                                                  sortable=True,
                                                  searchable=True)
                                             ]
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True,
                nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One side of SalesOrderInvoice
    ItemSalesOrderInvoice_Id = Column(Integer, ForeignKey("SalesOrderInvoices.Id"),
                                      info=dict(label="Invoice",
                                                exceptSchemaFields=["Extras",
                                                                    "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                    "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                    "versions"],
                                                depth=1))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SalesOrderExtraTypes.Id"),
                     nullable=False,
                     info=dict(label="Type", selectId="Id",
                               selectFormat=["Description", "Currency[0]"],
                               selectKey="Description", depth=1))
    Type = relationship("SalesOrderExtraType",
                        primaryjoin="SalesOrderExtraType.Id==SalesOrderInvoiceExtra.Type_Id")

    # Value is Currency Value and Ex GST
    Value = Column(Numeric(19, 4), default=0, nullable=False,
                   info=dict(label="Value",
                             numberType="currency",  # number, currency, percent, string
                             currencyCodeField="ItemSalesOrderInvoice.Currency",
                             validator=["NotZero"]))

    ValueInc = Column(Numeric(19, 4), default=0, nullable=False,
                      info=dict(label="Value Inc Tax",
                                numberType="currency",  # number, currency, percent, string
                                currencyCodeField="ItemSalesOrderInvoice.Currency",
                                validator=["NotZero"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderInvoiceExtra.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderInvoiceExtra.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # OneToOne side of SalesOrderExtra
    ItemSalesOrderExtra_Id = Column(Integer, ForeignKey("SalesOrderExtras.Id"),
                                    info=dict(label="Charged"))
    ItemSalesOrderExtra = relationship("SalesOrderExtra", back_populates="Charged",
                                       primaryjoin="SalesOrderExtra.Id==SalesOrderInvoiceExtra.ItemSalesOrderExtra_Id")

    @hybrid_property
    def total_tax(self):
        return self.ValueInc - self.Value

    @total_tax.expression
    def total_tax(cls):
        return cls.ValueInc - cls.Value

from datetime import datetime

from sqlalchemy import event
from sqlalchemy import (Column, ForeignKey, Integer, DateTime,
                        Numeric, Index)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .... import sqa
from .....security.policy import get_current_uid


class POSize(Model):
    __versioned__ = {}
    __tablename__ = "POSizes"
    __table_args__ = dict(info=dict(label="PO Line Sizes",
                                    desc="Sizes",
                                    companyField="Company_Id",
                                    stepperTitleFields=["SKU.Size.Size"],
                                    keyPaths=["ItemPODetail_Id"],
                                    key="SKU_Id",
                                    parentTables=[
                                        dict(column="ItemPODetail",
                                             table="PODetails")
                                    ],
                                    hybrids=[
                                        dict(name="total_tax",
                                             label="Total Tax",
                                             type="Numeric",
                                             length=19,
                                             decimals=4,
                                             numberType="currency",  # number, currency, percent, string
                                             currencyCodeField="ItemPODetail.ItemPOHeader.Currency",
                                             sortable=True,
                                             searchable=True),
                                    ]
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company",
                           primaryjoin="Company.Id==POSize.Company_Id")

    # Many2One side of PODetail
    ItemPODetail_Id = Column(Integer, ForeignKey("PODetails.Id"),
                             info=dict(label="PO Line",
                                       selectId="Id",
                                       selectKey="order_line",
                                       exceptSchemaFields=["Company_Id", "Company",
                                                           "Sizes",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id",
                                                           "ModifiedOpId", "versions"],
                                       depth=1))

    # Many2One
    SKU_Id = Column(Integer, ForeignKey("ProductSKUs.Id"),
                    nullable=False,
                    info=dict(label="Size",
                              selectId="Id",
                              selectKey="size",
                              selectFormat=["style_col_fit_dim_size"],
                              selectTableFieldValue=[{"field": "Status", "value": "Valid"}],
                              depth=1
                              ))
    SKU = relationship("ProductSKU",
                       primaryjoin="ProductSKU.Id==POSize.SKU_Id")

    Line = Column(Integer, nullable=False, default=1,
                  info=dict(label="Line Number"))

    Units = Column(Integer, default=0, nullable=False,
                   info=dict(label="Qty",
                             validator=["NotZero", "Positive"]))

    # UnitCost is Currency Value and Ex GST and Net of Discount
    UnitCost = Column(Numeric(19, 4), default=0, nullable=True,
                      info=dict(label="Unit Cost",
                                numberType="currency",  # number, currency, percent, string
                                currencyCodeField="ItemPODetail.ItemPOHeader.Currency",
                                validator=["ZeroPositive"]))

    UnitCostInc = Column(Numeric(19, 4), default=0, nullable=True,
                         info=dict(label="Unit Cost Inc Tax",
                                   numberType="currency",  # number, currency, percent, string
                                   currencyCodeField="ItemPODetail.ItemPOHeader.Currency",
                                   validator=["ZeroPositive"]))

    # Net Currency Value is Total Ordered Cost Net of Discount
    NetValue = Column(Numeric(19, 4), default=0, nullable=True,
                      info=dict(label="Net Value",
                                numberType="currency",  # number, currency, percent, string
                                currencyCodeField="ItemPODetail.ItemPOHeader.Currency",
                                modifiable=False))

    NetValueInc = Column(Numeric(19, 4), default=0, nullable=True,
                         info=dict(label="Value Inc Tax",
                                   numberType="currency",  # number, currency, percent, string
                                   currencyCodeField="ItemPODetail.ItemPOHeader.Currency",
                                   modifiable=False))

    Discount = Column(Numeric(8, 4), default=0, nullable=True,
                      info=dict(label="Discount Percentage",
                                numberType="percent",  # number, currency, percent, string
                                validator=["ZeroPositive"]))

    TaxRate = Column(Numeric(8, 4), default=0, nullable=True,
                     info=dict(label="Tax Rate Percentage",
                               numberType="percent",  # number, currency, percent, string
                               validator=["ZeroPositive"]))

    # Gross Value is Total Ordered Cost without Discount
    GrossUnitCost = Column(Numeric(19, 4), default=0, nullable=True,
                           info=dict(label="Gross Unit Cost",
                                     numberType="currency",  # number, currency, percent, string
                                     currencyCodeField="ItemPODetail.ItemPOHeader.Currency",
                                     modifiable=False))

    GrossValue = Column(Numeric(19, 4), default=0, nullable=True,
                        info=dict(label="Gross Total Cost",
                                  numberType="currency",  # number, currency, percent, string
                                  currencyCodeField="ItemPODetail.ItemPOHeader.Currency",
                                  modifiable=False))

    GrossUnitCostInc = Column(Numeric(19, 4), default=0, nullable=True,
                              info=dict(label="Gross Unit Price Inc Tax",
                                        numberType="currency",  # number, currency, percent, string
                                        currencyCodeField="ItemPODetail.ItemPOHeader.Currency",
                                        modifiable=False))

    GrossValueInc = Column(Numeric(19, 4), default=0, nullable=True,
                           info=dict(label="Gross Value Inc Tax",
                                     numberType="currency",  # number, currency, percent, string
                                     currencyCodeField="ItemPODetail.ItemPOHeader.Currency",
                                     modifiable=False))

    # One2Many
    Comments = relationship("POSizeComment", uselist=True,
                            backref="ItemPOSize",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==POSize.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==POSize.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    @hybrid_property
    def total_tax(self):
        return self.NetValueInc - self.NetValue

    @total_tax.expression
    def total_tax(cls):
        return cls.NetValueInc - cls.NetValue


Index("POSize_Index1", POSize.Company_Id,
      POSize.ItemPODetail_Id,
      POSize.SKU_Id,
      POSize.Line, unique=True)


def on_po_size_insert(mapper, connection, target):

    db_session = object_session(target)
    where = (f"Company_Id == {target.Company_Id} and "
             f"ItemPODetail_Id == {target.ItemPODetail_Id} and "
             f"SKU_Id == {target.SKU_Id}")
    last_line = db_session.query(sqa.get_model("POSizes")). \
        order_by(sqa.get_column("POSizes.Line").desc()). \
        filter(sqa.where(where)).first()

    line_number = 1
    if last_line is not None:
        line_number = last_line.Line + 1
    setattr(target, "Line", line_number)

    on_po_size_update(mapper, connection, target)


def on_po_size_update(mapper, connection, target):

    qty = getattr(target, "Units")
    cost = getattr(target, "UnitCost")
    discount = getattr(target, "Discount")
    net_value = qty * cost

    cost_inc = getattr(target, "UnitCostInc")
    net_value_inc = qty * cost_inc

    setattr(target, "NetValue", net_value)
    setattr(target, "GrossValue", net_value / (1 - (discount / 100)))
    setattr(target, "GrossUnitPrice", (net_value / (1 - (discount / 100))) / qty)

    setattr(target, "NetValueInc", net_value_inc)
    setattr(target, "GrossValueInc", net_value_inc / (1 - (discount / 100)))
    setattr(target, "GrossUnitPriceInc", (net_value_inc / (1 - (discount / 100))) / qty)


def on_po_size_delete(mapper, connection, target):
    from .PODetails import PODetail

    line = getattr(target, "ItemPODetail")

    # delete PODetail if no more Sizes
    if len(line.Sizes) == 0:
        connection.execute(
            PODetail.__table__.delete().
            where(PODetail.Id == line.Id)
        )


event.listen(POSize, "before_insert", on_po_size_insert)  # Mapper Event
event.listen(POSize, "before_update", on_po_size_update)  # Mapper Event
event.listen(POSize, "after_delete", on_po_size_delete)  # Mapper Event

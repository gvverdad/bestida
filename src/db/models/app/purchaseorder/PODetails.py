from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime,
                        Index, Enum, event, func, select)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .... import sqa
from .....security.policy import get_current_uid
from .POSizes import POSize


class PODetail(Model):
    __versioned__ = {}
    __tablename__ = "PODetails"
    __table_args__ = dict(info=dict(label="PO Lines", desc="Lines",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["ItemPOHeader_Id"],
                                    key="Line",
                                    parentTables=[
                                        dict(column="ItemPOHeader",
                                             table="POHeaders")
                                    ],
                                    hybrids=[dict(name="number_of_sizes",
                                                  label="Sizes",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="order_line",
                                                  label="Order/Line",
                                                  type="String",
                                                  length=27,
                                                  decimals=0,
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_qty",
                                                  label="Total Line Qty",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_value",
                                                  label="Total Line Value",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemPOHeader.Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_valueinc",
                                                  label="Total Line ValueInc",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemPOHeader.Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_tax",
                                                  label="Total Tax",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemPOHeader.Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="unit_cost",
                                                  label="Ave Line UnitCost",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemPOHeader.Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="unit_costinc",
                                                  label="Ave Line UnitCostInc",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemPOHeader.Currency",
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
    Company = relationship("Company", primaryjoin="Company.Id==PODetail.Company_Id")

    # Many2One side of POHeader
    ItemPOHeader_Id = Column(Integer, ForeignKey("POHeaders.Id"),
                             info=dict(label="Order Number",
                                       selectId="Id",
                                       selectKey="PONumber",
                                       selectFormat=["PONumber", "Supplier.Account"],
                                       exceptSchemaFields=["Company_Id", "Company", "Details",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       depth=1))

    Line = Column(Integer, nullable=False,
                  info=dict(label="Line Number",
                            numberType="string"  # number, currency, percent, string
                            ))

    # POLine is the original PODetails.Line
    POLine = Column(Integer, nullable=False,
                    info=dict(label="PO Line Number",
                              numberType="string",  # number, currency, percent, string
                              modifiable=False))

    Status = Column(Enum("Open", "Received", "Returned", "Cancelled",
                         name="PODetail_Status"),
                    nullable=False, default="Open",
                    info=dict(label="Status", modifiable=False)
                    )

    # Many2One
    Product_Id = Column(Integer, ForeignKey("ProductColourFitDims.Id"),
                        nullable=True,
                        info=dict(label="Product - Style/Col/Fit/Dim",
                                  selectTable="ProductColourFitDims",  # used for server update
                                  selectObject="ProductColourFitDims",  # used for client selection list
                                  selectId="Id",
                                  selectKey="style_col_fit_dim",
                                  selectFormat=["style_col_fit_dim"],
                                  selectTableFieldValue=[{"field": "AllowPurchase", "value": True}],
                                  depth=1))
    Product = relationship("ProductColourFitDim",
                           primaryjoin="ProductColourFitDim.Id==PODetail.Product_Id")

    # One2Many
    Sizes = relationship("POSize", uselist=True,
                         backref="ItemPODetail",
                         cascade="all, delete-orphan",
                         info=dict(dumpFields=["Id"]))

    # One2Many
    Comments = relationship("PODetailComment", uselist=True,
                            backref="ItemPODetail",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==PODetail.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==PODetail.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    @hybrid_property
    def number_of_sizes(self):
        return len(self.Sizes)

    @number_of_sizes.expression
    def number_of_sizes(cls):
        return select([func.count()]).\
            where(POSize.ItemPODetail_Id == cls.Id).as_scalar()

    @hybrid_property
    def order_line(self):
        return self.ItemPOHeader.OrderNumber + " " + str(self.Line)

    @order_line.expression
    def order_line(cls):
        from .POHeaders import POHeader

        return select([POHeader.OrderNumber + " " + str(PODetail.Line)]).\
            where(POHeader.Id == cls.ItemPOHeader_Id).as_scalar()

    @hybrid_property
    def total_qty(self):
        return sum(size.Units for size in self.Sizes)

    @total_qty.expression
    def total_qty(cls):
        from .POSizes import POSize

        return select([func.sum(POSize.Units)]).\
            where(POSize.ItemPODetail_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def total_value(self):
        return sum(size.NetValue for size in self.Sizes)

    @total_value.expression
    def total_value(cls):
        from .POSizes import POSize

        return select([func.sum(POSize.NetValue)]).\
            where(POSize.ItemPODetail_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def total_valueinc(self):
        return sum(size.NetValueInc for size in self.Sizes)

    @total_valueinc.expression
    def total_valueinc(cls):
        from .POSizes import POSize

        return select([func.sum(POSize.NetValueInc)]).\
            where(POSize.ItemSalesOrderDetail_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def total_tax(self):
        return self.total_valueinc - self.total_value

    @total_tax.expression
    def total_tax(cls):
        return cls.total_valueinc - cls.total_value

    @hybrid_property
    def unit_cost(self):
        return self.total_value / self.total_qty

    @unit_cost.expression
    def unit_cost(cls):
        return cls.total_value / cls.total_qty

    @hybrid_property
    def unit_costinc(self):
        return self.total_valueinc / self.total_qty

    @unit_costinc.expression
    def unit_costinc(cls):
        return cls.total_valueinc / cls.total_qty


Index("PODetail_Index1", PODetail.Company_Id,
      PODetail.ItemPOHeader_Id,
      PODetail.Line, unique=True)

Index("PODetail_Index2", PODetail.Company_Id,
      PODetail.ItemPOHeader_Id,
      PODetail.POLine, unique=False)

Index("PODetail_Index3", PODetail.Company_Id,
      PODetail.Product_Id, unique=False)

Index("PODetail_Index4", PODetail.Company_Id,
      PODetail.Status, unique=False)


def on_po_detail_insert(mapper, connection, target):
    on_po_detail_update(mapper, connection, target)

    head = getattr(target, "ItemPOHeader")

    db_session = object_session(target)
    last_line = db_session.query(sqa.get_model("PODetails")). \
        order_by(sqa.get_column("PODetails.Line").desc()). \
        filter(sqa.where("ItemPOHeader_Id = {}".format(head.Id))).first()

    line_number = 1
    if last_line is not None:
        line_number = last_line.Line + 1

    setattr(target, "Line", line_number)
    po_line = getattr(target, "POLine", None)
    if po_line is None or po_line == 0:
        setattr(target, "POLine", line_number)


def on_po_detail_update(mapper, connection, target):
    pass


def on_po_detail_delete(mapper, connection, target):
    from .POHeaders import POHeader
    from .POAddresses import POAddress
    from .POComments import POComment

    # delete POHeader when no more Details
    if len(target.ItemPOHeader.Details) == 0:
        connection.execute(
            POAddress.__table__.delete().
            where(POAddress.ItemPOHeader_Id == target.ItemPOHeader_Id)
        )
        connection.execute(
            POComment.__table__.delete().
            where(POComment.ItemPOHeader_Id == target.ItemPOHeader_Id)
        )
        connection.execute(
            POHeader.__table__.delete().
            where(POHeader.Id == target.ItemPOHeader_Id)
        )


event.listen(PODetail, "before_insert", on_po_detail_insert)  # Mapper Event
event.listen(PODetail, "before_update", on_po_detail_update)  # Mapper Event
event.listen(PODetail, "after_delete", on_po_detail_delete)  # Mapper Event

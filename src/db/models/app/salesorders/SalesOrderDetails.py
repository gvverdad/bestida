from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Date,
                        Index, Enum, event, func, select, inspect)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .SalesOrderSizes import SalesOrderSize
from .... import sqa
from .....security.policy import get_current_uid


class SalesOrderDetail(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderDetails"
    __table_args__ = dict(info=dict(label="Sales Order Lines", desc="Lines",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["ItemSalesOrderHeader_Id"],
                                    key="Line",
                                    parentTables=[
                                        dict(column="ItemSalesOrderHeader",
                                             table="SalesOrderHeaders")
                                    ],
                                    crud_constraint=dict(
                                        copy=dict(condition="Status !== \"Open\"",
                                                  message="Order Line must be Open to Copy"),
                                        edit=dict(condition="Status !== \"Open\"",
                                                  message="Order Line must be Open to Edit"),
                                        delete=dict(condition="Status !== \"Open\"",
                                                    message="Order Line must be Open to Delete")
                                    ),
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
                                                  currencyCodeField="ItemSalesOrderHeader.Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_valueinc",
                                                  label="Total Line ValueInc",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemSalesOrderHeader.Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_tax",
                                                  label="Total Tax",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemSalesOrderHeader.Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="unit_price",
                                                  label="Ave Line UnitPrice",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemSalesOrderHeader.Currency",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="unit_priceinc",
                                                  label="Ave Line UnitPriceInc",
                                                  type="Numeric",
                                                  length=19,
                                                  decimals=4,
                                                  numberType="currency",  # number, currency, percent, string
                                                  currencyCodeField="ItemSalesOrderHeader.Currency",
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
    Company = relationship("Company", primaryjoin="Company.Id==SalesOrderDetail.Company_Id")

    # Many2One side of SalesOrderHeader
    ItemSalesOrderHeader_Id = Column(Integer, ForeignKey("SalesOrderHeaders.Id"),
                                     info=dict(label="Order Number",
                                               selectId="Id",
                                               selectKey="OrderNumber",
                                               selectFormat=["OrderNumber", "Customer.Account", "PurchaseOrder"],
                                               exceptSchemaFields=["Company_Id", "Company", "Details",
                                                                   "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                   "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                   "versions"],
                                               depth=1))

    Line = Column(Integer, nullable=False,
                  info=dict(label="Line Number",
                            numberType="string"  # number, currency, percent, string
                            ))

    # POLine is the original SalesOrderDetails.Line
    POLine = Column(Integer, nullable=False,
                    info=dict(label="PO Line Number",
                              numberType="string",  # number, currency, percent, string
                              modifiable=False))

    Status = Column(Enum("Open", "Allocated", "Picked", "Packed", "Despatched",
                         "Returned", "Cancelled", name="SalesOrderDetail_Status"),
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
                                  selectTableFieldValue=[{"field": "AllowSales", "value": True}],
                                  depth=1))
    Product = relationship("ProductColourFitDim",
                           primaryjoin="ProductColourFitDim.Id==SalesOrderDetail.Product_Id")

    StartDate = Column(Date(), nullable=False,
                       info=dict(label="Start Delivery Date"))
    CancelDate = Column(Date(), nullable=False,
                        info=dict(label="Cancel Delivery Date"))

    # Many2One
    Warehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                          nullable=False,
                          info=dict(label="Warehouse",
                                    selectId="Id", selectKey="Name", depth=1))
    Warehouse = relationship("Warehouse",
                             primaryjoin="Warehouse.Id==SalesOrderDetail.Warehouse_Id")

    # One2Many
    Sizes = relationship("SalesOrderSize", uselist=True,
                         backref="ItemSalesOrderDetail",
                         cascade="all, delete-orphan",
                         info=dict(dumpFields=["Id"]))

    # One2Many
    Comments = relationship("SalesOrderDetailComment", uselist=True,
                            backref="ItemSalesOrderDetail",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    OpenedOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                           info=dict(label="Opened By", modifiable=False))
    OpenedOpId = relationship("User", primaryjoin="User.Id==SalesOrderDetail.OpenedOpId_Id")
    OpenedTimeStamp = Column(DateTime, nullable=True,
                             info=dict(label="Opened Timestamp", modifiable=False))

    # Many2One
    AllocatedOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                              info=dict(label="Allocated By", modifiable=False))
    AllocatedOpId = relationship("User", primaryjoin="User.Id==SalesOrderDetail.AllocatedOpId_Id")
    AllocatedTimeStamp = Column(DateTime, nullable=True,
                                info=dict(label="Allocated Timestamp", modifiable=False))

    # Many2One
    PickTicket_Id = Column(Integer, ForeignKey("SalesOrderPickTickets.Id"),
                           nullable=True,
                           info=dict(label="Pick Ticket", modifiable=False,
                                     depth=1))
    PickTicket = relationship("SalesOrderPickTicket",
                              primaryjoin="SalesOrderPickTicket.Id==SalesOrderDetail.PickTicket_Id")
    # Many2One
    PickedOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                           info=dict(label="Picked By", modifiable=False))
    PickedOpId = relationship("User", primaryjoin="User.Id==SalesOrderDetail.PickedOpId_Id")
    PickedTimeStamp = Column(DateTime, nullable=True,
                             info=dict(label="Picked Timestamp", modifiable=False))

    # Many2One
    Container_Id = Column(Integer, ForeignKey("SalesOrderContainers.Id"),
                          nullable=True,
                          info=dict(label="SSCC", modifiable=False,
                                    depth=1))
    Container = relationship("SalesOrderContainer",
                             primaryjoin="SalesOrderContainer.Id==SalesOrderDetail.Container_Id")
    # Many2One
    PackedOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                           info=dict(label="Packed By", modifiable=False))
    PackedOpId = relationship("User", primaryjoin="User.Id==SalesOrderDetail.PackedOpId_Id")
    PackedTimeStamp = Column(DateTime, nullable=True,
                             info=dict(label="Packed Timestamp", modifiable=False))

    # Many2One
    Invoice_Id = Column(Integer, ForeignKey("SalesOrderInvoices.Id"),
                        nullable=True,
                        info=dict(label="Invoice", modifiable=False,
                                  depth=1))
    Invoice = relationship("SalesOrderInvoice",
                           primaryjoin="SalesOrderInvoice.Id==SalesOrderDetail.Invoice_Id")
    # Many2One
    DespatchedOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                               info=dict(label="Despatched By", modifiable=False))
    DespatchedOpId = relationship("User", primaryjoin="User.Id==SalesOrderDetail.DespatchedOpId_Id")
    DespatchedTimeStamp = Column(DateTime, nullable=True,
                                 info=dict(label="Despatched Timestamp", modifiable=False))

    # Many2One
    CreditNote_Id = Column(Integer, ForeignKey("SalesOrderCreditNotes.Id"),
                           nullable=True,
                           info=dict(label="CreditNote", modifiable=False,
                                     depth=1))
    CreditNote = relationship("SalesOrderCreditNote",
                              primaryjoin="SalesOrderCreditNote.Id==SalesOrderDetail.CreditNote_Id")
    # Many2One
    ReturnedOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                             info=dict(label="Returned By", modifiable=False))
    ReturnedOpId = relationship("User", primaryjoin="User.Id==SalesOrderDetail.ReturnedOpId_Id")
    ReturnedTimeStamp = Column(DateTime, nullable=True,
                               info=dict(label="Returned Timestamp", modifiable=False))

    # Many2One
    CancelReason_Id = Column(Integer, ForeignKey("SalesOrderCancelReasons.Id"),
                             nullable=True,
                             info=dict(label="Cancel Reason", modifiable=False,
                                       depth=1))
    CancelReason = relationship("SalesOrderCancelReason",
                                primaryjoin="SalesOrderCancelReason.Id==SalesOrderDetail.CancelReason_Id")
    # Many2One
    CancelledOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                              info=dict(label="Cancelled By", modifiable=False))
    CancelledOpId = relationship("User", primaryjoin="User.Id==SalesOrderDetail.CancelledOpId_Id")
    CancelledTimeStamp = Column(DateTime, nullable=True,
                                info=dict(label="Cancelled Timestamp", modifiable=False))
    # Many2One
    ReinstatedOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                              info=dict(label="Reinstated By", modifiable=False))
    ReinstatedOpId = relationship("User", primaryjoin="User.Id==SalesOrderDetail.ReinstatedOpId_Id")
    ReinstatedTimeStamp = Column(DateTime, nullable=True,
                                info=dict(label="Reinstated Timestamp", modifiable=False))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderDetail.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderDetail.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    @hybrid_property
    def number_of_sizes(self):
        return len(self.Sizes)

    @number_of_sizes.expression
    def number_of_sizes(cls):
        return select([func.count()]).\
            where(SalesOrderSize.ItemSalesOrderDetail_Id == cls.Id).as_scalar()

    @hybrid_property
    def order_line(self):
        return self.ItemSalesOrderHeader.OrderNumber + " " + str(self.Line)

    @order_line.expression
    def order_line(cls):
        from .SalesOrderHeaders import SalesOrderHeader

        return select([SalesOrderHeader.OrderNumber + " " + str(SalesOrderDetail.Line)]).\
            where(SalesOrderHeader.Id == cls.ItemSalesOrderHeader_Id).as_scalar()

    @hybrid_property
    def total_qty(self):
        return sum(size.Units for size in self.Sizes)

    @total_qty.expression
    def total_qty(cls):
        from .SalesOrderSizes import SalesOrderSize

        return select([func.sum(SalesOrderSize.Units)]).\
            where(SalesOrderSize.ItemSalesOrderDetail_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def total_value(self):
        return sum(size.NetValue for size in self.Sizes)

    @total_value.expression
    def total_value(cls):
        from .SalesOrderSizes import SalesOrderSize

        return select([func.sum(SalesOrderSize.NetValue)]).\
            where(SalesOrderSize.ItemSalesOrderDetail_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def total_valueinc(self):
        return sum(size.NetValueInc for size in self.Sizes)

    @total_valueinc.expression
    def total_valueinc(cls):
        from .SalesOrderSizes import SalesOrderSize

        return select([func.sum(SalesOrderSize.NetValueInc)]).\
            where(SalesOrderSize.ItemSalesOrderDetail_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def total_tax(self):
        return self.total_valueinc - self.total_value

    @total_tax.expression
    def total_tax(cls):
        return cls.total_valueinc - cls.total_value

    @hybrid_property
    def unit_price(self):
        return self.total_value / self.total_qty

    @unit_price.expression
    def unit_price(cls):
        return cls.total_value / cls.total_qty

    @hybrid_property
    def unit_priceinc(self):
        return self.total_valueinc / self.total_qty

    @unit_priceinc.expression
    def unit_priceinc(cls):
        return cls.total_valueinc / cls.total_qty


Index("SalesOrderDetail_Index1", SalesOrderDetail.Company_Id,
      SalesOrderDetail.ItemSalesOrderHeader_Id,
      SalesOrderDetail.Line, unique=True)

Index("SalesOrderDetail_Index2", SalesOrderDetail.Company_Id,
      SalesOrderDetail.ItemSalesOrderHeader_Id,
      SalesOrderDetail.POLine, unique=False)

Index("SalesOrderDetail_Index3", SalesOrderDetail.Company_Id,
      SalesOrderDetail.Product_Id, unique=False)

Index("SalesOrderDetail_Index4", SalesOrderDetail.Company_Id,
      SalesOrderDetail.Warehouse_Id, unique=False)

Index("SalesOrderDetail_Index5", SalesOrderDetail.Company_Id,
      SalesOrderDetail.Status, unique=False)

Index("SalesOrderDetail_Index6", SalesOrderDetail.Company_Id,
      SalesOrderDetail.StartDate,
      SalesOrderDetail.Status, unique=False)

Index("SalesOrderDetail_Index7", SalesOrderDetail.Company_Id,
      SalesOrderDetail.CancelDate,
      SalesOrderDetail.Status, unique=False)

Index("SalesOrderDetail_Index8", SalesOrderDetail.Company_Id,
      SalesOrderDetail.AllocatedTimeStamp, unique=False)

Index("SalesOrderDetail_Index9", SalesOrderDetail.Company_Id,
      SalesOrderDetail.PickedTimeStamp, unique=False)

Index("SalesOrderDetail_Index10", SalesOrderDetail.Company_Id,
      SalesOrderDetail.PickTicket_Id, unique=False)

Index("SalesOrderDetail_Index11", SalesOrderDetail.Company_Id,
      SalesOrderDetail.PackedTimeStamp, unique=False)

Index("SalesOrderDetail_Index12", SalesOrderDetail.Company_Id,
      SalesOrderDetail.Container_Id, unique=False)

Index("SalesOrderDetail_Index13", SalesOrderDetail.Company_Id,
      SalesOrderDetail.DespatchedTimeStamp, unique=False)

Index("SalesOrderDetail_Index14", SalesOrderDetail.Company_Id,
      SalesOrderDetail.Invoice_Id, unique=False)

Index("SalesOrderDetail_Index15", SalesOrderDetail.Company_Id,
      SalesOrderDetail.ReturnedTimeStamp, unique=False)

Index("SalesOrderDetail_Index16", SalesOrderDetail.Company_Id,
      SalesOrderDetail.CreditNote_Id, unique=False)

Index("SalesOrderDetail_Index17", SalesOrderDetail.Company_Id,
      SalesOrderDetail.CancelledTimeStamp, unique=False)

Index("SalesOrderDetail_Index18", SalesOrderDetail.Company_Id,
      SalesOrderDetail.CancelReason_Id, unique=False)


def on_order_detail_insert(mapper, connection, target):
    on_order_detail_update(mapper, connection, target)

    head = getattr(target, "ItemSalesOrderHeader")

    db_session = object_session(target)
    last_line = db_session.query(sqa.get_model("SalesOrderDetails")). \
        order_by(sqa.get_column("SalesOrderDetails.Line").desc()). \
        filter(sqa.where("ItemSalesOrderHeader_Id = {}".format(head.Id))).first()

    line_number = 1
    if last_line is not None:
        line_number = last_line.Line + 1

    setattr(target, "Line", line_number)
    po_line = getattr(target, "POLine", None)
    if po_line is None or po_line == 0:
        setattr(target, "POLine", line_number)


def on_order_detail_update(mapper, connection, target):
    from .SalesOrderHeaders import SalesOrderHeader
    from src.db.models.app.salesorders.SalesOrders import SalesOrder
    from src.db.models.app.salesorders.SalesAllocations import SalesAllocation
    from src.db.models.app.salesorders.SalesPickings import SalesPicking

    head = getattr(target, "ItemSalesOrderHeader")
    head_start = head.StartDate
    head_cancel = head.CancelDate

    hist_status = inspect(target).attrs.Status.history
    hist_warehouse = inspect(target).attrs.Warehouse_Id.history

    status = getattr(target, "Status")
    start_date = getattr(target, "StartDate")
    cancel_date = getattr(target, "CancelDate")

    if head_start is None or start_date < head_start:
        head_start = start_date
    if head_cancel is None or cancel_date > head_cancel:
        head_cancel = cancel_date

    # new record  History(added=['Open'], unchanged=(), deleted=())
    # no status change History(added=(), unchanged=['Open'], deleted=())
    # status change History(added=['Allocated'], unchanged=(), deleted=['Open'])
    if isinstance(hist_status.deleted, list):
        # Line Status Change From/To
        if hist_status.deleted[0] == "Open":
            if hist_status.added[0] == "Allocated":
                for size in target.Sizes:
                    # add to SalesAllocations
                    sales_allo = connection.execute(
                        SalesAllocation.__table__.select().
                        where(SalesAllocation.Company_Id == target.Company_Id).
                        where(SalesAllocation.Warehouse_Id == target.Warehouse_Id).
                        where(SalesAllocation.SKU_Id == size.SKU_Id)
                    ).first()
                    if sales_allo:
                        units = sales_allo.Allocations + size.Units
                        connection.execute(
                            SalesAllocation.__table__.update().
                            values(Allocations=units).
                            where(SalesAllocation.Company_Id == target.Company_Id).
                            where(SalesAllocation.Warehouse_Id == target.Warehouse_Id).
                            where(SalesAllocation.SKU_Id == size.SKU_Id)
                        )
                    else:
                        connection.execute(
                            SalesAllocation.__table__.insert().
                            values(Company_Id=target.Company_Id,
                                   Warehouse_Id=target.Warehouse_Id,
                                   SKU_Id=size.SKU_Id,
                                   Allocations=size.Units)
                        )
            elif hist_status.added[0] == "Picked":
                # see SalesOrderPickTicketDetails event
                pass
            elif hist_status.added[0] == "Despatched":
                pass
            elif hist_status.added[0] == "Cancelled":
                for size in target.Sizes:
                    # remove from SalesOrders
                    sales_order = connection.execute(
                        SalesOrder.__table__.select().
                        where(SalesOrder.Company_Id == target.Company_Id).
                        where(SalesOrder.Warehouse_Id == target.Warehouse_Id).
                        where(SalesOrder.SKU_Id == size.SKU_Id)
                    ).first()
                    if sales_order:
                        units = max(0, sales_order.Orders - size.Units)
                        if units > 0:
                            connection.execute(
                                SalesOrder.__table__.update().
                                values(Orders=units).
                                where(SalesOrder.Company_Id == target.Company_Id).
                                where(SalesOrder.Warehouse_Id == target.Warehouse_Id).
                                where(SalesOrder.SKU_Id == size.SKU_Id)
                            )
                        else:
                            connection.execute(
                                SalesOrder.__table__.delete().
                                where(SalesOrder.Company_Id == target.Company_Id).
                                where(SalesOrder.Warehouse_Id == target.Warehouse_Id).
                                where(SalesOrder.SKU_Id == size.SKU_Id)
                            )
        elif hist_status.deleted[0] == "Allocated":
            if hist_status.added[0] == "Open":
                for size in target.Sizes:
                    # remove from SalesAllocations
                    sales_allo = connection.execute(
                        SalesAllocation.__table__.select().
                        where(SalesAllocation.Company_Id == target.Company_Id).
                        where(SalesAllocation.Warehouse_Id == target.Warehouse_Id).
                        where(SalesAllocation.SKU_Id == size.SKU_Id)
                    ).first()
                    if sales_allo:
                        units = max(0, sales_allo.Allocations - size.Units)
                        if units > 0:
                            connection.execute(
                                SalesAllocation.__table__.update().
                                values(Allocations=units).
                                where(SalesAllocation.Company_Id == target.Company_Id).
                                where(SalesAllocation.Warehouse_Id == target.Warehouse_Id).
                                where(SalesAllocation.SKU_Id == size.SKU_Id)
                            )
                        else:
                            connection.execute(
                                SalesAllocation.__table__.delete().
                                where(SalesAllocation.Company_Id == target.Company_Id).
                                where(SalesAllocation.Warehouse_Id == target.Warehouse_Id).
                                where(SalesAllocation.SKU_Id == size.SKU_Id)
                            )
            elif hist_status.added[0] == "Picked":
                for size in target.Sizes:
                    # remove from SalesAllocations
                    sales_allo = connection.execute(
                        SalesAllocation.__table__.select().
                        where(SalesAllocation.Company_Id == target.Company_Id).
                        where(SalesAllocation.Warehouse_Id == target.Warehouse_Id).
                        where(SalesAllocation.SKU_Id == size.SKU_Id)
                    ).first()
                    if sales_allo:
                        units = max(0, sales_allo.Allocations - size.Units)
                        if units > 0:
                            connection.execute(
                                SalesAllocation.__table__.update().
                                values(Allocations=units).
                                where(SalesAllocation.Company_Id == target.Company_Id).
                                where(SalesAllocation.Warehouse_Id == target.Warehouse_Id).
                                where(SalesAllocation.SKU_Id == size.SKU_Id)
                            )
                        else:
                            connection.execute(
                                SalesAllocation.__table__.delete().
                                where(SalesAllocation.Company_Id == target.Company_Id).
                                where(SalesAllocation.Warehouse_Id == target.Warehouse_Id).
                                where(SalesAllocation.SKU_Id == size.SKU_Id)
                            )
                    # add to SalesPickings
                    # see SalesOrderPickTicketDetails event
        elif hist_status.deleted[0] == "Picked":
            if hist_status.added[0] == "Open":
                pass
            elif hist_status.added[0] == "Allocated":
                pass
            elif hist_status.added[0] == "Packed":
                pass
            elif hist_status.added[0] == "Despatched":
                for size in target.Sizes:
                    # add to SalesInvoices
                    # see SalesOrderInvoiceDetails event
                    # remove from SalesPicking
                    sales_pick = connection.execute(
                        SalesPicking.__table__.select().
                        where(SalesPicking.Company_Id == target.Company_Id).
                        where(SalesPicking.Location_Id == size.PickTicket.Location_Id).
                        where(SalesPicking.SKU_Id == size.SKU_Id)
                    ).first()
                    if sales_pick:
                        units = max(0, sales_pick.Pickings - size.Units)
                        if units > 0:
                            connection.execute(
                                SalesPicking.__table__.update().
                                values(Pickings=units).
                                where(SalesPicking.Company_Id == target.Company_Id).
                                where(SalesPicking.Location_Id == size.PickTicket.Location_Id).
                                where(SalesPicking.SKU_Id == size.SKU_Id)
                            )
                        else:
                            connection.execute(
                                SalesPicking.__table__.delete().
                                where(SalesPicking.Company_Id == target.Company_Id).
                                where(SalesPicking.Location_Id == size.PickTicket.Location_Id).
                                where(SalesPicking.SKU_Id == size.SKU_Id)
                            )
        elif hist_status.deleted[0] == "Packed":
            if hist_status.added[0] == "Open":
                pass
            elif hist_status.added[0] == "Allocated":
                pass
            elif hist_status.added[0] == "Picked":
                pass
            elif hist_status.added[0] == "Despatched":
                pass
        elif hist_status.deleted[0] == "Despatched":
            if hist_status.added[0] == "Open":
                pass
            elif hist_status.added[0] == "Allocated":
                pass
            elif hist_status.added[0] == "Picked":
                # add to SalesPickings
                # see SalesOrderPickTicketDetails event
                # remove from SalesInvoices
                # see SalesOrderInvoiceDetails event
                pass
        elif hist_status.deleted[0] == "Cancelled":
            # Reinstate order
            if hist_status.added[0] == "Open":
                for size in target.Sizes:
                    # add to SalesOrders
                    sales_order = connection.execute(
                        SalesOrder.__table__.select().
                        where(SalesOrder.Company_Id == target.Company_Id).
                        where(SalesOrder.Warehouse_Id == target.Warehouse_Id).
                        where(SalesOrder.SKU_Id == size.SKU_Id)
                    ).first()
                    if sales_order:
                        units = sales_order.Orders + size.Units
                        connection.execute(
                            SalesOrder.__table__.update().
                            values(Orders=units).
                            where(SalesOrder.Company_Id == target.Company_Id).
                            where(SalesOrder.Warehouse_Id == target.Warehouse_Id).
                            where(SalesOrder.SKU_Id == size.SKU_Id)
                        )
                    else:
                        connection.execute(
                            SalesOrder.__table__.insert().
                            values(Company_Id=target.Company_Id,
                                   Warehouse_Id=target.Warehouse_Id,
                                   SKU_Id=size.SKU_Id,
                                   Orders=size.Units)
                        )
    else:
        # No Status Change but Change in Warehouse
        if isinstance(hist_warehouse.deleted, list):
            old_warehouse_id = hist_warehouse.deleted[0]
            for size in target.Sizes:
                # remove from old warehouse orders
                sales_order = connection.execute(
                    SalesOrder.__table__.select().
                    where(SalesOrder.Company_Id == target.Company_Id).
                    where(SalesOrder.Warehouse_Id == old_warehouse_id).
                    where(SalesOrder.SKU_Id == size.SKU_Id)
                ).first()
                if sales_order:
                    units = max(0, sales_order.Orders - size.Units)
                    if units > 0:
                        connection.execute(
                            SalesOrder.__table__.update().
                            values(Orders=units).
                            where(SalesOrder.Company_Id == target.Company_Id).
                            where(SalesOrder.Warehouse_Id == old_warehouse_id).
                            where(SalesOrder.SKU_Id == size.SKU_Id)
                        )
                    else:
                        connection.execute(
                            SalesOrder.__table__.delete().
                            where(SalesOrder.Company_Id == target.Company_Id).
                            where(SalesOrder.Warehouse_Id == old_warehouse_id).
                            where(SalesOrder.SKU_Id == size.SKU_Id)
                        )
                # add to new warehouse orders
                sales_order = connection.execute(
                    SalesOrder.__table__.select().
                    where(SalesOrder.Company_Id == target.Company_Id).
                    where(SalesOrder.Warehouse_Id == target.Warehouse_Id).
                    where(SalesOrder.SKU_Id == size.SKU_Id)
                ).first()
                if sales_order:
                    units = sales_order.Orders + size.Units
                    connection.execute(
                        SalesOrder.__table__.update().
                        values(Orders=units).
                        where(SalesOrder.Company_Id == target.Company_Id).
                        where(SalesOrder.Warehouse_Id == target.Warehouse_Id).
                        where(SalesOrder.SKU_Id == size.SKU_Id)
                    )
                else:
                    connection.execute(
                        SalesOrder.__table__.insert().
                        values(Company_Id=target.Company_Id,
                               Warehouse_Id=target.Warehouse_Id,
                               SKU_Id=size.SKU_Id,
                               Orders=size.Units
                               )
                    )

    if status == "Open" and getattr(target, "OpenedTimeStamp") is None:
        setattr(target, "OpenedTimeStamp", datetime.utcnow())
        setattr(target, "OpenedOpId_Id", get_current_uid())
    elif status == "Allocated" and getattr(target, "AllocatedTimeStamp") is None:
        setattr(target, "AllocatedTimeStamp", datetime.utcnow())
        setattr(target, "AllocatedOpId_Id", get_current_uid())
    elif status == "Picked" and getattr(target, "PickedTimeStamp") is None:
        setattr(target, "PickedTimeStamp", datetime.utcnow())
        setattr(target, "PickedOpId_Id", get_current_uid())
    elif status == "Packed" and getattr(target, "PackedTimeStamp") is None:
        setattr(target, "PackedTimeStamp", datetime.utcnow())
        setattr(target, "PackedOpId_Id", get_current_uid())
    elif status == "Despatched" and getattr(target, "DespatchedTimeStamp") is None:
        setattr(target, "DespatchedTimeStamp", datetime.utcnow())
        setattr(target, "DespatchedOpId_Id", get_current_uid())
    elif status == "Returned" and getattr(target, "ReturnedTimeStamp") is None:
        setattr(target, "ReturnedTimeStamp", datetime.utcnow())
        setattr(target, "ReturnedOpId_Id", get_current_uid())

    if status == "Cancelled" and getattr(target, "CancelledTimeStamp") is None:
        setattr(target, "CancelledTimeStamp", datetime.utcnow())
        setattr(target, "CancelOpId_Id", get_current_uid())
    elif status != "Cancelled" and getattr(target, "CancelledTimeStamp") is not None:
        setattr(target, "CancelledTimeStamp", None)
        setattr(target, "CancelOpId_Id", None)
        setattr(target, "ReinstatedTimeStamp", datetime.utcnow())
        setattr(target, "ReinstatedOpId_Id", get_current_uid())


    # https://stackoverflow.com/questions/38074244/modify-other-objects-on-update-insert
    connection.execute(
        SalesOrderHeader.__table__.update().
        values(StartDate=head_start,
               CancelDate=head_cancel
               ).
        where(SalesOrderHeader.Id == target.ItemSalesOrderHeader_Id)
    )


def on_order_detail_delete(mapper, connection, target):
    from .SalesOrderHeaders import SalesOrderHeader
    from .SalesOrderExtras import SalesOrderExtra
    from .SalesOrderAddresses import SalesOrderAddress
    from .SalesOrderComments import SalesOrderComment

    # delete SalesOrderHeader when no more Details
    if len(target.ItemSalesOrderHeader.Details) == 0:
        connection.execute(
            SalesOrderExtra.__table__.delete().
            where(SalesOrderExtra.ItemSalesOrderHeader_Id == target.ItemSalesOrderHeader_Id)
        )
        connection.execute(
            SalesOrderAddress.__table__.delete().
            where(SalesOrderAddress.ItemSalesOrderHeader_Id == target.ItemSalesOrderHeader_Id)
        )
        connection.execute(
            SalesOrderComment.__table__.delete().
            where(SalesOrderComment.ItemSalesOrderHeader_Id == target.ItemSalesOrderHeader_Id)
        )
        connection.execute(
            SalesOrderHeader.__table__.delete().
            where(SalesOrderHeader.Id == target.ItemSalesOrderHeader_Id)
        )


event.listen(SalesOrderDetail, "before_insert", on_order_detail_insert)  # Mapper Event
event.listen(SalesOrderDetail, "before_update", on_order_detail_update)  # Mapper Event
event.listen(SalesOrderDetail, "after_delete", on_order_detail_delete)  # Mapper Event

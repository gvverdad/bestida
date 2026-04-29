from datetime import datetime

from sqlalchemy import event, inspect
from sqlalchemy import (Column, ForeignKey, Integer, DateTime, String, Text,
                        Numeric, Index)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .... import sqa
from .....security.policy import get_current_uid


class SalesOrderSize(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderSizes"
    __table_args__ = dict(info=dict(label="Order Line Sizes",
                                    desc="Sizes",
                                    companyField="Company_Id",
                                    stepperTitleFields=["SKU.Size.Size"],
                                    keyPaths=["ItemSalesOrderDetail_Id"],
                                    key="SKU_Id",
                                    parentTables=[
                                        dict(column="ItemSalesOrderDetail",
                                             table="SalesOrderDetails")
                                    ],
                                    crud_constraint=dict(
                                        new=dict(condition="ItemSalesOrderDetail.Status !== \"Open\"",
                                                 message="Order Line must be Open to Add New Size"),
                                        copy=dict(condition="ItemSalesOrderDetail.Status !== \"Open\"",
                                                  message="Order Line must be Open to Copy New Size"),
                                        edit=dict(condition="ItemSalesOrderDetail.Status !== \"Open\"",
                                                  message="Order Line must be Open to Edit Size"),
                                        delete=dict(condition="ItemSalesOrderDetail.Status !== \"Open\"",
                                                    message="Order Line must be Open to Delete Size")
                                    ),
                                    hybrids=[
                                        dict(name="total_tax",
                                             label="Total Tax",
                                             type="Numeric",
                                             length=19,
                                             decimals=4,
                                             numberType="currency",  # number, currency, percent, string
                                             currencyCodeField="ItemSalesOrderDetail.ItemSalesOrderHeader.Currency",
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
                           primaryjoin="Company.Id==SalesOrderSize.Company_Id")

    # Many2One side of SalesOrderDetail
    ItemSalesOrderDetail_Id = Column(Integer, ForeignKey("SalesOrderDetails.Id"),
                                     info=dict(label="Order Line",
                                               selectId="Id",
                                               selectKey="order_line",
                                               exceptSchemaFields=["Company_Id", "Company",
                                                                   "Sizes",
                                                                   "PickTicket_Id", "PickTicket",
                                                                   "Invoice_Id", "Invoice",
                                                                   "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                   "ModifiedTimeStamp", "ModifiedOpId_Id",
                                                                   "ModifiedOpId",
                                                                   "versions"],
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
                       primaryjoin="ProductSKU.Id==SalesOrderSize.SKU_Id")

    Line = Column(Integer, nullable=False, default=1,
                  info=dict(label="Line Number"))

    Units = Column(Integer, default=0, nullable=False,
                   info=dict(label="Qty",
                             validator=["NotZero", "Positive"]))

    # UnitPrice is Currency Value and Ex GST and Net of Discount
    UnitPrice = Column(Numeric(19, 4), default=0, nullable=True,
                       info=dict(label="Unit Price",
                                 numberType="currency",  # number, currency, percent, string
                                 currencyCodeField="ItemSalesOrderDetail.ItemSalesOrderHeader.Currency",
                                 validator=["ZeroPositive"]))

    UnitPriceInc = Column(Numeric(19, 4), default=0, nullable=True,
                          info=dict(label="Unit Price Inc Tax",
                                    numberType="currency",  # number, currency, percent, string
                                    currencyCodeField="ItemSalesOrderDetail.ItemSalesOrderHeader.Currency",
                                    validator=["ZeroPositive"]))

    # Net Currency Value is Total Ordered Value Net of Discount
    NetValue = Column(Numeric(19, 4), default=0, nullable=True,
                      info=dict(label="Net Value",
                                numberType="currency",  # number, currency, percent, string
                                currencyCodeField="ItemSalesOrderDetail.ItemSalesOrderHeader.Currency",
                                modifiable=False))

    NetValueInc = Column(Numeric(19, 4), default=0, nullable=True,
                         info=dict(label="Net Value Inc Tax",
                                   numberType="currency",  # number, currency, percent, string
                                   currencyCodeField="ItemSalesOrderDetail.ItemSalesOrderHeader.Currency",
                                   modifiable=False))

    Discount = Column(Numeric(8, 4), default=0, nullable=True,
                      info=dict(label="Discount Percentage",
                                numberType="percent",  # number, currency, percent, string
                                validator=["ZeroPositive"]))

    TaxRate = Column(Numeric(8, 4), default=0, nullable=True,
                     info=dict(label="Tax Rate Percentage",
                               numberType="percent",  # number, currency, percent, string
                               validator=["ZeroPositive"]))

    # Gross Value is Total Ordered Value without Discount
    GrossUnitPrice = Column(Numeric(19, 4), default=0, nullable=True,
                            info=dict(label="Gross Unit Price",
                                      numberType="currency",  # number, currency, percent, string
                                      currencyCodeField="ItemSalesOrderDetail.ItemSalesOrderHeader.Currency",
                                      modifiable=False))

    GrossValue = Column(Numeric(19, 4), default=0, nullable=True,
                        info=dict(label="Gross Value",
                                  numberType="currency",  # number, currency, percent, string
                                  currencyCodeField="ItemSalesOrderDetail.ItemSalesOrderHeader.Currency",
                                  modifiable=False))

    GrossUnitPriceInc = Column(Numeric(19, 4), default=0, nullable=True,
                               info=dict(label="Gross Unit Price Inc Tax",
                                         numberType="currency",  # number, currency, percent, string
                                         currencyCodeField="ItemSalesOrderDetail.ItemSalesOrderHeader.Currency",
                                         modifiable=False))

    GrossValueInc = Column(Numeric(19, 4), default=0, nullable=True,
                           info=dict(label="Gross Value Inc Tax",
                                     numberType="currency",  # number, currency, percent, string
                                     currencyCodeField="ItemSalesOrderDetail.ItemSalesOrderHeader.Currency",
                                     modifiable=False))

    UnitCost = Column(Numeric(19, 4), default=0, nullable=True,
                      info=dict(label="Unit Cost",
                                numberType="currency",  # number, currency, percent, string
                                currencyCodeField="Company.Currency",  # Base Currency
                                modifiable=False))

    TotalCost = Column(Numeric(19, 4), default=0, nullable=True,
                       info=dict(label="Total Cost",
                                 numberType="currency",  # number, currency, percent, string
                                 currencyCodeField="Company.Currency",  # Base Currency
                                 modifiable=False))

    PriceSource = Column(String(64), nullable=True,
                         info=dict(label="Price Source", modifiable=False))

    SystemUnitPrice = Column(Numeric(19, 4), default=0, nullable=True,
                             info=dict(label="System Unit Price Found",
                                       numberType="currency",  # number, currency, percent, string
                                       currencyCodeField="ItemSalesOrderDetail.ItemSalesOrderHeader.Currency",
                                       validator=["ZeroPositive"]))

    PriceParams = Column(Text, nullable=True,
                         info=dict(label="Price Params", modifiable=False))

    PriceSourceKey = Column(Text, nullable=True,
                            info=dict(label="Price Source Key", modifiable=False))

    SystemDiscount = Column(Numeric(8, 4), default=0, nullable=True,
                            info=dict(label="System Discount Found",
                                      numberType="percent",  # number, currency, percent, string
                                      validator=["ZeroPositive"]))

    DiscountSourceKey = Column(Text, nullable=True,
                               info=dict(label="Discount Source Key",
                                         modifiable=False))

    # One2Many
    Comments = relationship("SalesOrderSizeComment", uselist=True,
                            backref="ItemSalesOrderSize",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # One2One side of SalesOrderPickTicketDetails
    PickTicket = relationship("SalesOrderPickTicketDetail", uselist=False,
                              back_populates="ItemSalesOrderSize",
                              primaryjoin="SalesOrderPickTicketDetail.ItemSalesOrderSize_Id==SalesOrderSize.Id",
                              cascade="all, delete-orphan",
                              info=dict(label="Pick Ticket",
                                        exceptSchemaFields=["Company_Id", "Company",
                                                            "ItemSalesOrderSize_Id", "ItemSalesOrderSize",
                                                            "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                            "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                            "versions"],
                                        modifiable=False, depth=1))

    # One2One side of SalesOrderInvoiceDetails
    Invoice = relationship("SalesOrderInvoiceDetail", uselist=False,
                           back_populates="ItemSalesOrderSize",
                           primaryjoin="SalesOrderInvoiceDetail.ItemSalesOrderSize_Id==SalesOrderSize.Id",
                           cascade="all, delete-orphan",
                           info=dict(label="Invoice",
                                     exceptSchemaFields=["Company_Id", "Company",
                                                         "ItemSalesOrderSize_Id", "ItemSalesOrderSize",
                                                         "Location_Id", "Location",
                                                         "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                         "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                         "versions"],
                                     modifiable=False, depth=1))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderSize.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderSize.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    @hybrid_property
    def total_tax(self):
        return self.NetValueInc - self.NetValue

    @total_tax.expression
    def total_tax(cls):
        return cls.NetValueInc - cls.NetValue


Index("SalesOrderSize_Index1", SalesOrderSize.Company_Id,
      SalesOrderSize.ItemSalesOrderDetail_Id,
      SalesOrderSize.SKU_Id,
      SalesOrderSize.Line, unique=True)


def on_order_size_insert(mapper, connection, target):
    from src.db.models.app.salesorders.SalesOrders import SalesOrder

    db_session = object_session(target)
    where = (f"Company_Id == {target.Company_Id} and "
             f"ItemSalesOrderDetail_Id == {target.ItemSalesOrderDetail_Id} and "
             f"SKU_Id == {target.SKU_Id}")
    last_line = db_session.query(sqa.get_model("SalesOrderSizes")). \
        order_by(sqa.get_column("SalesOrderSizes.Line").desc()). \
        filter(sqa.where(where)).first()

    line_number = 1
    if last_line is not None:
        line_number = last_line.Line + 1
    setattr(target, "Line", line_number)

    qty = getattr(target, "Units")
    price = getattr(target, "UnitPrice")
    discount = getattr(target, "Discount")
    net_value = qty * price

    price_inc = getattr(target, "UnitPriceInc")
    net_value_inc = qty * price_inc

    setattr(target, "NetValue", net_value)
    setattr(target, "GrossValue", net_value / (1 - (discount / 100)))
    setattr(target, "GrossUnitPrice", (net_value / (1 - (discount / 100))) / qty)

    setattr(target, "NetValueInc", net_value_inc)
    setattr(target, "GrossValueInc", net_value_inc / (1 - (discount / 100)))
    setattr(target, "GrossUnitPriceInc", (net_value_inc / (1 - (discount / 100))) / qty)

    cost = getattr(target, "UnitCost")
    if cost is None:
        cost = 0
    total_cost = qty * cost
    setattr(target, "TotalCost", total_cost)

    company = getattr(target, "Company")
    line = getattr(target, "ItemSalesOrderDetail")

    sales_order = connection.execute(
        SalesOrder.__table__.select().
        where(SalesOrder.Company_Id == company.Id).
        where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
        where(SalesOrder.SKU_Id == target.SKU_Id)
    ).first()
    if sales_order is None:
        connection.execute(
            SalesOrder.__table__.insert().
            values(Company_Id=company.Id,
                   Warehouse_Id=line.Warehouse_Id,
                   SKU_Id=target.SKU_Id,
                   Orders=qty)
        )
    else:
        total_orders = sales_order.Orders + qty
        connection.execute(
            SalesOrder.__table__.update().
            values(Orders=total_orders).
            where(SalesOrder.Company_Id == company.Id).
            where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
            where(SalesOrder.SKU_Id == target.SKU_Id)
        )


def on_order_size_update(mapper, connection, target):
    from src.db.models.app.salesorders.SalesOrders import SalesOrder

    qty = getattr(target, "Units")
    price = getattr(target, "UnitPrice")
    discount = getattr(target, "Discount")
    net_value = qty * price

    price_inc = getattr(target, "UnitPriceInc")
    net_value_inc = qty * price_inc

    setattr(target, "NetValue", net_value)
    setattr(target, "GrossValue", net_value / (1 - (discount / 100)))
    setattr(target, "GrossUnitPrice", (net_value / (1 - (discount / 100))) / qty)

    setattr(target, "NetValueInc", net_value_inc)
    setattr(target, "GrossValueInc", net_value_inc / (1 - (discount / 100)))
    setattr(target, "GrossUnitPriceInc", (net_value_inc / (1 - (discount / 100))) / qty)

    cost = getattr(target, "UnitCost")
    if cost is None:
        cost = 0
    total_cost = qty * cost
    setattr(target, "TotalCost", total_cost)

    line = getattr(target, "ItemSalesOrderDetail")

    hist_qty = inspect(target).attrs.Units.history
    hist_sku_id = inspect(target).attrs.SKU_Id.history
    # new record  History(added=[1], unchanged=(), deleted=())
    # no qty change History(added=(), unchanged=[1], deleted=())
    # sku_id change History(added=[2], unchanged=(), deleted=[1])
    if isinstance(hist_sku_id.deleted, list):
        old_sku_id = hist_sku_id.deleted[0]
        old_qty = qty
        if isinstance(hist_qty.deleted, list):
            old_qty = hist_qty.deleted[0]
        # remove old sku orders
        sales_order = connection.execute(
            SalesOrder.__table__.select().
            where(SalesOrder.Company_Id == target.Company_Id).
            where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
            where(SalesOrder.SKU_Id == old_sku_id)
        ).first()
        if sales_order:
            units = max(0, sales_order.Orders - old_qty)
            if units > 0:
                connection.execute(
                    SalesOrder.__table__.update().
                    values(Orders=units).
                    where(SalesOrder.Company_Id == target.Company_Id).
                    where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
                    where(SalesOrder.SKU_Id == old_sku_id)
                )
            else:
                connection.execute(
                    SalesOrder.__table__.delete().
                    where(SalesOrder.Company_Id == target.Company_Id).
                    where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
                    where(SalesOrder.SKU_Id == old_sku_id)
                )
        # add new sku orders
        sales_order = connection.execute(
            SalesOrder.__table__.select().
            where(SalesOrder.Company_Id == target.Company_Id).
            where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
            where(SalesOrder.SKU_Id == target.SKU_Id)
        ).first()
        if sales_order:
            units = sales_order.Orders + qty
            connection.execute(
                SalesOrder.__table__.update().
                values(Orders=units).
                where(SalesOrder.Company_Id == target.Company_Id).
                where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
                where(SalesOrder.SKU_Id == target.SKU_Id)
            )
        else:
            connection.execute(
                SalesOrder.__table__.insert().
                values(Company_Id=target.Company_Id,
                       Warehouse_Id=line.Warehouse_Id,
                       SKU_Id=target.SKU_Id,
                       Orders=qty)
            )

    # new record  History(added=[1], unchanged=(), deleted=())
    # no qty change History(added=(), unchanged=[1], deleted=())
    # qty change History(added=[2], unchanged=(), deleted=[1])
    if isinstance(hist_qty.deleted, list):
        sales_order = connection.execute(
            SalesOrder.__table__.select().
            where(SalesOrder.Company_Id == target.Company_Id).
            where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
            where(SalesOrder.SKU_Id == target.SKU_Id)
        ).first()
        if sales_order is None:
            connection.execute(
                SalesOrder.__table__.insert().
                values(Company_Id=target.Company_Id,
                       Warehouse_Id=line.Warehouse_Id,
                       SKU_Id=target.SKU_Id,
                       Orders=qty)
            )
        else:
            total_orders = max(0, sales_order.Orders - hist_qty.deleted[0]) + qty
            connection.execute(
                SalesOrder.__table__.update().
                values(Orders=total_orders).
                where(SalesOrder.Company_Id == target.Company_Id).
                where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
                where(SalesOrder.SKU_Id == target.SKU_Id)
            )


def on_order_size_delete(mapper, connection, target):
    from src.db.models.app.salesorders.SalesOrders import SalesOrder
    from .SalesOrderDetails import SalesOrderDetail

    hist_qty = inspect(target).attrs.Units.history
    qty = getattr(target, "Units")
    # new record  History(added=[1], unchanged=(), deleted=())
    # no qty change History(added=(), unchanged=[1], deleted=())
    # qty change History(added=[2], unchanged=(), deleted=[1])
    if isinstance(hist_qty.unchanged, list):
        qty = hist_qty.unchanged[0]

    line = getattr(target, "ItemSalesOrderDetail")

    if line.Status == "Cancelled":
        # see SalesOrderDetails event
        pass
    else:
        sales_order = connection.execute(
            SalesOrder.__table__.select().
            where(SalesOrder.Company_Id == target.Company_Id).
            where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
            where(SalesOrder.SKU_Id == target.SKU_Id)
        ).first()
        if sales_order:
            total_orders = max(0, sales_order.Orders - qty)
            if total_orders == 0:
                connection.execute(
                    SalesOrder.__table__.delete().
                    where(SalesOrder.Company_Id == target.Company_Id).
                    where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
                    where(SalesOrder.SKU_Id == target.SKU_Id)
                )
            else:
                connection.execute(
                    SalesOrder.__table__.update().
                    values(Orders=total_orders).
                    where(SalesOrder.Company_Id == target.Company_Id).
                    where(SalesOrder.Warehouse_Id == line.Warehouse_Id).
                    where(SalesOrder.SKU_Id == target.SKU_Id)
                )

    # delete SalesOrderDetail if no more Sizes
    if len(line.Sizes) == 0:
        connection.execute(
            SalesOrderDetail.__table__.delete().
            where(SalesOrderDetail.Id == line.Id)
        )


event.listen(SalesOrderSize, "before_insert", on_order_size_insert)  # Mapper Event
event.listen(SalesOrderSize, "before_update", on_order_size_update)  # Mapper Event
event.listen(SalesOrderSize, "after_delete", on_order_size_delete)  # Mapper Event

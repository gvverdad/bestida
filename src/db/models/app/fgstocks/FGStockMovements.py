from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, String, Text, Index,
                        Enum, Numeric, case, event)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid


class FGStockMovement(Model):
    __versioned__ = {}
    __tablename__ = "FGStockMovements"
    __table_args__ = dict(info=dict(label="Product Stock Reconciliation",
                                    desc="Product Reconciliation",
                                    companyField="Company_Id",
                                    runningBalance=["Qty", "TotalCost"],
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id",
                                              "FromLocation_Id"],
                                    key="SKU_Id",
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==FGStockMovement.Company_Id")

    # Many2One
    FromLocation_Id = Column(Integer, ForeignKey("WarehouseLocations.Id"),
                             nullable=False,
                             info=dict(label="From Location",
                                       selectId="Id",
                                       selectKey="warehouse_area_location",
                                       selectFormat=["warehouse_area_location"],
                                       depth=1
                                       ))
    FromLocation = relationship("WarehouseLocation",
                                primaryjoin="WarehouseLocation.Id==FGStockMovement.FromLocation_Id")

    # Many2One
    ToLocation_Id = Column(Integer, ForeignKey("WarehouseLocations.Id"),
                           nullable=True,
                           info=dict(label="To Location",
                                     selectId="Id",
                                     selectKey="warehouse_area_location",
                                     selectFormat=["warehouse_area_location"],
                                     depth=1
                                     ))
    ToLocation = relationship("WarehouseLocation",
                              primaryjoin="WarehouseLocation.Id==FGStockMovement.ToLocation_Id")

    # Many2One
    SKU_Id = Column(Integer, ForeignKey("ProductSKUs.Id"),
                    nullable=False,
                    info=dict(label="SKU",
                              selectId="Id",
                              selectKey="style_col_fit_dim_size",
                              selectFormat=["style_col_fit_dim_size"],
                              depth=1))
    SKU = relationship("ProductSKU",
                       primaryjoin="ProductSKU.Id==FGStockMovement.SKU_Id")

    Type = Column(Enum("Adjustment", "TransferIn", "TransferOut", "Receipt",
                       "Despatch", "Returns",
                       name="Movement_Type"),
                  nullable=False,
                  info=dict(label="Type"))

    AdjustmentType = Column(Enum("Adjustment", "Replacement",
                                 name="Adjustment_Type"),
                            nullable=True, default="Adjustment",
                            info=dict(label="Adjustment Type"))

    Qty = Column(Integer, nullable=False, default=0,
                 info=dict(label="Movement Qty"))
    TotalCost = Column(Numeric(19, 4), default=0, nullable=False,
                       info=dict(label="Total Cost",
                                 numberType="currency",  # number, currency, percent, string
                                 currencyCodeField="Company.Currency"
                                 ))

    # Many2One
    Reason_Id = Column(Integer, ForeignKey("FGStockAdjustmentReasons.Id"),
                       nullable=True,
                       info=dict(label="Product Stock Adjustment Reason",
                                 selectId="Id", selectKey="Description",
                                 requiredIf="Type == \"Adjustment\"",
                                 depth=1))
    Reason = relationship("FGStockAdjustmentReason",
                          primaryjoin="FGStockAdjustmentReason.Id==FGStockMovement.Reason_Id")

    Document = Column(String(128), nullable=True, info=dict(label="Document"))
    Reference = Column(String(256), nullable=True, info=dict(label="Reference"))
    Comments = Column(Text, nullable=True, info=dict(label="Comments"))

    OrderNumber = Column(String(22), nullable=True,
                         info=dict(label="Order Number", modifiable=False,
                                   documents=[dict(program="DocumentSalesOrder",
                                                  params=dict(orderNumber="."))
                                             ]
                                   ))

    PTNumber = Column(Integer, nullable=True,
                      info=dict(label="Pick Ticket Number", modifiable=False,
                                numberType="string",  # number, currency, percent, string
                                documents=[dict(program="DocumentPickTicket",
                                               params=dict(ptNumber="."))
                                          ]
                                ))

    InvoiceNumber = Column(Integer, nullable=True,
                           info=dict(label="Invoice Number", modifiable=False,
                                     numberType="string",  # number, currency, percent, string
                                     documents=[dict(program="DocumentInvoice",
                                                    params=dict(invoiceNumber="."))
                                               ]
                                     ))

    # TODO: add PO Number for Purchase Order
    # TODO: add PO Number for Production Order

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==FGStockMovement.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==FGStockMovement.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # calculated columns
    @hybrid_property
    def unit_cost(self):
        if self.TotalCost == 0:
            return 0
        return self.Qty / self.TotalCost

    @unit_cost.expression
    def unit_cost(cls):
        return case(
            [(cls.TotalCost == 0, 0)],
            else_=cls.Qty / cls.TotalCost
        )


Index("FGStockMovement_Index1", FGStockMovement.Company_Id, FGStockMovement.SKU_Id,
      FGStockMovement.CreateTimeStamp, unique=False)


def on_stock_movement_update(mapper, connection, target):
    from ..fgstocks.FGStocks import FGStock

    stock = connection.execute(
        FGStock.__table__.select().
        where(FGStock.Company_Id == target.Company_Id).
        where(FGStock.Location_Id == target.FromLocation_Id).
        where(FGStock.SKU_Id == target.SKU_Id)
    ).first()
    if stock:
        qty = target.Qty
        if target.Type == "Adjustment" and target.AdjustmentType == "Replacement":
            qty = qty - stock.OnHand
            setattr(target, "Qty", qty)
        units = stock.OnHand + qty
        if units == 0:
            connection.execute(
                FGStock.__table__.delete().
                where(FGStock.Company_Id == target.Company_Id).
                where(FGStock.Location_Id == target.FromLocation_Id).
                where(FGStock.SKU_Id == target.SKU_Id)
            )
        else:
            connection.execute(
                FGStock.__table__.update().
                values(OnHand=units).
                where(FGStock.Company_Id == target.Company_Id).
                where(FGStock.Location_Id == target.FromLocation_Id).
                where(FGStock.SKU_Id == target.SKU_Id)
            )
    else:
        connection.execute(
            FGStock.__table__.insert().
            values(Company_Id=target.Company_Id,
                   Location_Id=target.FromLocation_Id,
                   SKU_Id=target.SKU_Id,
                   OnHand=target.Qty)
        )


def on_stock_movement_delete(mapper, connection, target):
    pass

"""
    use after_insert/update instead of before_insert/update
    to prevent timing issues
    target.SKU is already updated but targer.SKU_Id isn't.
    otherwise use target.SKU.Id instead
"""
event.listen(FGStockMovement, "after_insert", on_stock_movement_update)  # Mapper Event
event.listen(FGStockMovement, "after_update", on_stock_movement_update)  # Mapper Event
event.listen(FGStockMovement, "after_delete", on_stock_movement_delete)  # Mapper Event

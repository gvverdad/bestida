from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime,
                        Index, event)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class SalesOrderInvoiceDetail(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderInvoiceDetails"
    __table_args__ = dict(info=dict(label="Sales Order Invoice Detail",
                                    desc="Lines",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="PTNumber"
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SalesOrderInvoiceDetail.Company_Id")

    # Many2One side of SalesOrderInvoice
    ItemSalesOrderInvoice_Id = Column(Integer, ForeignKey("SalesOrderInvoices.Id"),
                                      info=dict(label="Invoice Number",
                                                selectId="Id",
                                                selectKey="InvoiceNumber",
                                                exceptSchemaFields=["Company_Id", "Company", "Details",
                                                                    "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                    "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                    "versions"],
                                                depth=1))

    # OneToOne side of SalesOrderSizes
    ItemSalesOrderSize_Id = Column(Integer, ForeignKey("SalesOrderSizes.Id"),
                                   info=dict(label="Sales Order Size"))
    ItemSalesOrderSize = relationship("SalesOrderSize", back_populates="Invoice",
                                      primaryjoin="SalesOrderSize.Id==SalesOrderInvoiceDetail.ItemSalesOrderSize_Id")

    # Many2One
    Location_Id = Column(Integer, ForeignKey("WarehouseLocations.Id"),
                         nullable=False,
                         info=dict(label="Location",
                                   selectId="Id",
                                   selectKey="warehouse_area_location",
                                   selectFormat=["warehouse_area_location"],
                                   depth=1
                                   ))
    Location = relationship("WarehouseLocation",
                            primaryjoin="WarehouseLocation.Id==SalesOrderInvoiceDetail.Location_Id")

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderInvoiceDetail.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderInvoiceDetail.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("SalesOrderInvoiceDetail_Index1", SalesOrderInvoiceDetail.Company_Id,
      SalesOrderInvoiceDetail.ItemSalesOrderInvoice_Id,
      SalesOrderInvoiceDetail.ItemSalesOrderSize_Id, unique=True)


def on_invoice_detail_update(mapper, connection, target):
    from src.db.models.app.salesorders.SalesInvoices import SalesInvoice

    sales_invoice = connection.execute(
        SalesInvoice.__table__.select().
        where(SalesInvoice.Company_Id == target.Company_Id).
        where(SalesInvoice.Warehouse_Id == target.Location.ItemWarehouseArea.ItemWarehouse_Id).
        where(SalesInvoice.SKU_Id == target.ItemSalesOrderSize.SKU_Id)
    ).first()
    if sales_invoice:
        units = sales_invoice.Invoices + target.ItemSalesOrderSize.Units
        connection.execute(
            SalesInvoice.__table__.update().
            values(Invoices=units).
            where(SalesInvoice.Company_Id == target.Company_Id).
            where(SalesInvoice.Warehouse_Id == target.Location.ItemWarehouseArea.ItemWarehouse_Id).
            where(SalesInvoice.SKU_Id == target.ItemSalesOrderSize.SKU_Id)
        )
    else:
        connection.execute(
            SalesInvoice.__table__.insert().
            values(Company_Id=target.Company_Id,
                   Warehouse_Id=target.Location.ItemWarehouseArea.ItemWarehouse_Id,
                   SKU_Id=target.ItemSalesOrderSize.SKU_Id,
                   Invoices=target.ItemSalesOrderSize.Units)
        )


def on_invoice_detail_delete(mapper, connection, target):
    from src.db.models.app.salesorders.SalesInvoices import SalesInvoice
    from .SalesOrderInvoices import SalesOrderInvoice
    from .SalesOrderInvoiceExtras import SalesOrderInvoiceExtra
    from .SalesOrderInvoiceAddresses import SalesOrderInvoiceAddress
    from .SalesOrderInvoiceComments import SalesOrderInvoiceComment

    sales_invoice = connection.execute(
        SalesInvoice.__table__.select().
        where(SalesInvoice.Company_Id == target.Company_Id).
        where(SalesInvoice.Warehouse_Id == target.Location.ItemWarehouseArea.ItemWarehouse_Id).
        where(SalesInvoice.SKU_Id == target.ItemSalesOrderSize.SKU_Id)
    ).first()
    if sales_invoice:
        units = max(0, sales_invoice.Invoices - target.ItemSalesOrderSize.Units)
        if units > 0:
            connection.execute(
                SalesInvoice.__table__.update().
                values(Invoices=units).
                where(SalesInvoice.Company_Id == target.Company_Id).
                where(SalesInvoice.Warehouse_Id == target.Location.ItemWarehouseArea.ItemWarehouse_Id).
                where(SalesInvoice.SKU_Id == target.ItemSalesOrderSize.SKU_Id)
            )
        else:
            connection.execute(
                SalesInvoice.__table__.delete().
                where(SalesInvoice.Company_Id == target.Company_Id).
                where(SalesInvoice.Warehouse_Id == target.Location.ItemWarehouseArea.ItemWarehouse_Id).
                where(SalesInvoice.SKU_Id == target.ItemSalesOrderSize.SKU_Id)
            )

    # delete SalesOrderInvoice if no more Details
    if len(target.ItemSalesOrderInvoice.Details) == 0:
        connection.execute(
            SalesOrderInvoiceExtra.__table__.delete().
            where(SalesOrderInvoiceExtra.ItemSalesOrderInvoice_Id == target.ItemSalesOrderInvoice_Id)
        )
        connection.execute(
            SalesOrderInvoiceAddress.__table__.delete().
            where(SalesOrderInvoiceAddress.ItemSalesOrderInvoice_Id == target.ItemSalesOrderInvoice_Id)
        )
        connection.execute(
            SalesOrderInvoiceComment.__table__.delete().
            where(SalesOrderInvoiceComment.ItemSalesOrderInvoice_Id == target.ItemSalesOrderInvoice_Id)
        )
        connection.execute(
            SalesOrderInvoice.__table__.delete().
            where(SalesOrderInvoice.Id == target.ItemSalesOrderInvoice_Id)
        )


event.listen(SalesOrderInvoiceDetail, "before_insert", on_invoice_detail_update)  # Mapper Event
event.listen(SalesOrderInvoiceDetail, "before_update", on_invoice_detail_update)  # Mapper Event
event.listen(SalesOrderInvoiceDetail, "after_delete", on_invoice_detail_delete)  # Mapper Event

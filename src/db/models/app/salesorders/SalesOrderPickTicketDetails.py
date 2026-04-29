from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime,
                        Index, event)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class SalesOrderPickTicketDetail(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderPickTicketDetails"
    __table_args__ = dict(info=dict(label="Sales Order PickTicket Detail",
                                    desc="Lines",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id", "ItemSalesOrderPickTicket_Id"],
                                    key="ItemSalesOrderSize_Id"
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SalesOrderPickTicketDetail.Company_Id")

    # Many2One side of SalesOrderPickTicket
    ItemSalesOrderPickTicket_Id = Column(Integer, ForeignKey("SalesOrderPickTickets.Id"),
                                         info=dict(label="Pick Ticket Number",
                                                   selectId="Id",
                                                   selectKey="PTNumber",
                                                   selectFormat=["PTNumber", "Warehouse.Warehouse"],
                                                   exceptSchemaFields=["Company_Id", "Company", "Details",
                                                                       "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                       "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                       "versions"],
                                                   depth=1))

    # OneToOne side of SalesOrderSizes
    ItemSalesOrderSize_Id = Column(Integer, ForeignKey("SalesOrderSizes.Id"),
                                   info=dict(label="Sales Order Size",
                                             exceptSchemaFields=["Company_Id", "Company", "PickTicket",
                                                                 "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                 "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                 "versions"]
                                             ))
    ItemSalesOrderSize = relationship("SalesOrderSize", back_populates="PickTicket",
                                      primaryjoin="SalesOrderSize.Id==SalesOrderPickTicketDetail.ItemSalesOrderSize_Id")

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
                            primaryjoin="WarehouseLocation.Id==SalesOrderPickTicketDetail.Location_Id")

    AreaSequence = Column(Integer, default=1, nullable=True,
                          info=dict(label="Area Sequence", modifiable=False))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderPickTicketDetail.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderPickTicketDetail.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("SalesOrderPickTicketDetail_Index1", SalesOrderPickTicketDetail.Company_Id,
      SalesOrderPickTicketDetail.ItemSalesOrderPickTicket_Id,
      SalesOrderPickTicketDetail.ItemSalesOrderSize_Id, unique=True)


def on_pick_ticket_detail_update(mapper, connection, target):
    from src.db.models.app.salesorders.SalesPickings import SalesPicking

    if target.Location.Reserved_Id == target.ItemSalesOrderSize_Id:
        setattr(target, "AreaSequence", 0)
    elif target.Location.ItemWarehouseArea.Type == "Pick":
        setattr(target, "AreaSequence", 1)
    elif target.Location.ItemWarehouseArea.Type == "Bulk":
        setattr(target, "AreaSequence", 2)
    elif target.Location.ItemWarehouseArea.Type == "Receiving":
        setattr(target, "AreaSequence", 3)
    elif target.Location.ItemWarehouseArea.Type == "Pack":
        setattr(target, "AreaSequence", 4)
    else:
        setattr(target, "AreaSequence", 99)

    sales_pick = connection.execute(
        SalesPicking.__table__.select().
        where(SalesPicking.Company_Id == target.Company_Id).
        where(SalesPicking.Location_Id == target.Location_Id).
        where(SalesPicking.SKU_Id == target.ItemSalesOrderSize.SKU_Id)
    ).first()
    if sales_pick:
        units = sales_pick.Pickings + target.ItemSalesOrderSize.Units
        connection.execute(
            SalesPicking.__table__.update().
            values(Pickings=units).
            where(SalesPicking.Company_Id == target.Company_Id).
            where(SalesPicking.Location_Id == target.Location_Id).
            where(SalesPicking.SKU_Id == target.ItemSalesOrderSize.SKU_Id)
        )
    else:
        connection.execute(
            SalesPicking.__table__.insert().
            values(Company_Id=target.Company_Id,
                   Location_Id=target.Location_Id,
                   SKU_Id=target.ItemSalesOrderSize.SKU_Id,
                   Pickings=target.ItemSalesOrderSize.Units)
        )


def on_pick_ticket_detail_delete(mapper, connection, target):
    from src.db.models.app.salesorders.SalesPickings import SalesPicking
    from .SalesOrderPickTickets import SalesOrderPickTicket
    from .SalesOrderPickTicketAddresses import SalesOrderPickTicketAddress
    from .SalesOrderPickTicketComments import SalesOrderPickTicketComment

    sales_pick = connection.execute(
        SalesPicking.__table__.select().
        where(SalesPicking.Company_Id == target.Company_Id).
        where(SalesPicking.Location_Id == target.Location_Id).
        where(SalesPicking.SKU_Id == target.ItemSalesOrderSize.SKU_Id)
    ).first()
    if sales_pick:
        units = max(0, sales_pick.Pickings - target.ItemSalesOrderSize.Units)
        if units > 0:
            connection.execute(
                SalesPicking.__table__.update().
                values(Pickings=units).
                where(SalesPicking.Company_Id == target.Company_Id).
                where(SalesPicking.Location_Id == target.Location_Id).
                where(SalesPicking.SKU_Id == target.ItemSalesOrderSize.SKU_Id)
            )
        else:
            connection.execute(
                SalesPicking.__table__.delete().
                where(SalesPicking.Company_Id == target.Company_Id).
                where(SalesPicking.Location_Id == target.Location_Id).
                where(SalesPicking.SKU_Id == target.ItemSalesOrderSize.SKU_Id)
            )

    # delete SalesOrderPickTicket if no more Details
    if len(target.ItemSalesOrderPickTicket.Details) == 0:
        connection.execute(
            SalesOrderPickTicketAddress.__table__.delete().
            where(SalesOrderPickTicketAddress.ItemSalesOrderPickTicket_Id == target.ItemSalesOrderPickTicket_Id)
        )
        connection.execute(
            SalesOrderPickTicketComment.__table__.delete().
            where(SalesOrderPickTicketComment.ItemSalesOrderPickTicket_Id == target.ItemSalesOrderPickTicket_Id)
        )
        connection.execute(
            SalesOrderPickTicket.__table__.delete().
            where(SalesOrderPickTicket.Id == target.ItemSalesOrderPickTicket_Id)
        )


event.listen(SalesOrderPickTicketDetail, "before_insert", on_pick_ticket_detail_update)  # Mapper Event
event.listen(SalesOrderPickTicketDetail, "before_update", on_pick_ticket_detail_update)  # Mapper Event
event.listen(SalesOrderPickTicketDetail, "after_delete", on_pick_ticket_detail_delete)  # Mapper Event

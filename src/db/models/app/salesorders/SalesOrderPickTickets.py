from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, String,
                        Numeric, Index, select, func)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import get_currency_choices


class SalesOrderPickTicket(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderPickTickets"
    __table_args__ = dict(info=dict(label="Sales Order PickTicket",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id", "Warehouse_Id"],
                                    key="PTNumber",
                                    hybrids=[dict(name="number_of_lines",
                                                  label="Lines",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="total_qty",
                                                  label="Total Picked Qty",
                                                  type="Integer",
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
    Company = relationship("Company", primaryjoin="Company.Id==SalesOrderPickTicket.Company_Id")

    # Many2One
    Warehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                          nullable=False,
                          info=dict(label="Warehouse",
                                    selectId="Id", selectKey="Name", depth=1))
    Warehouse = relationship("Warehouse",
                             primaryjoin="Warehouse.Id==SalesOrderPickTicket.Warehouse_Id")

    PTNumber = Column(Integer, nullable=False,
                      info=dict(label="Pick Ticket Number",
                                numberType="string",  # number, currency, percent, string
                                documents=[dict(program="DocumentPickTicket",
                                               params=dict(ptNumber="."))
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
    Customer = relationship("Customer", primaryjoin="Customer.Id==SalesOrderPickTicket.Customer_Id")

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
    DeliverVia = relationship("CustomerWarehouse",
                              primaryjoin="CustomerWarehouse.Id==SalesOrderPickTicket.DeliverVia_Id")

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
    Store = relationship("CustomerStore",
                         primaryjoin="CustomerStore.Id==SalesOrderPickTicket.Store_Id")

    Currency = Column(String(3), nullable=False, default="AUD",
                      info=dict(label="Currency",
                                modifiable=False,
                                choices=get_currency_choices,
                                choices_getter="getCurrencyList"))

    Weight = Column(Numeric(9, 4), default=0, nullable=True,
                    info=dict(label="Picked Weight in Kilos"))

    Volume = Column(Numeric(9, 4), default=0, nullable=True,
                    info=dict(label="Picked Volume in Cubic Metres"))

    Containers = Column(Integer, default=0, nullable=True,
                        info=dict(label="Number of Containers"))

    # Many2One
    CheckedBy_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                          default=get_current_uid, info=dict(label="Checked By"))
    CheckedBy = relationship("User",
                             primaryjoin="User.Id==SalesOrderPickTicket.CheckedBy_Id")

    # Many2One
    PickedBy_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                         default=get_current_uid, info=dict(label="Picked By"))
    PickedBy = relationship("User",
                            primaryjoin="User.Id==SalesOrderPickTicket.PickedBy_Id")

    # Many2One
    PackedBy_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                         default=get_current_uid, info=dict(label="Packed By"))
    PackedBy = relationship("User",
                            primaryjoin="User.Id==SalesOrderPickTicket.PackedBy_Id")

    # One2Many
    Details = relationship("SalesOrderPickTicketDetail", uselist=True,
                           backref="ItemSalesOrderPickTicket",
                           cascade="all, delete-orphan",
                           info=dict(dumpFields=["Id"]))

    # One2Many
    Addresses = relationship("SalesOrderPickTicketAddress", uselist=True,
                             backref="ItemSalesOrderPickTicket",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"]))

    # One2Many
    Comments = relationship("SalesOrderPickTicketComment", uselist=True,
                            backref="ItemSalesOrderPickTicket",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User",
                              primaryjoin="User.Id==SalesOrderPickTicket.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User",
                                primaryjoin="User.Id==SalesOrderPickTicket.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of SalesOrderDetails
    SalesOrderLines = relationship("SalesOrderDetail", uselist=True,
                                   back_populates="PickTicket",
                                   info=dict(hidden=True, dump=False))

    @hybrid_property
    def number_of_lines(self):
        return len(self.Details)

    @number_of_lines.expression
    def number_of_lines(cls):
        from .SalesOrderPickTicketDetails import SalesOrderPickTicketDetail

        return select([func.count()]).\
            where(SalesOrderPickTicketDetail.ItemSalesOrderPickTicket_Id == cls.Id).as_scalar()

    @hybrid_property
    def total_qty(self):
        return sum(line.ItemSalesOrderSize.Units for line in self.Details)

    @total_qty.expression
    def total_qty(cls):
        from .SalesOrderPickTicketDetails import SalesOrderPickTicketDetail
        from .SalesOrderSizes import SalesOrderSize

        return select([func.sum(SalesOrderSize.Units)]).\
            where(SalesOrderPickTicketDetail.ItemSalesOrderPickTicket_Id == cls.Id).\
            where(SalesOrderSize.Id == SalesOrderPickTicketDetail.ItemSalesOrderSize_Id).\
            as_scalar()

    @hybrid_property
    def total_value(self):
        return sum(line.ItemSalesOrderSize.NetValue for line in self.Details)

    @total_value.expression
    def total_value(cls):
        from .SalesOrderPickTicketDetails import SalesOrderPickTicketDetail
        from .SalesOrderSizes import SalesOrderSize

        return select([func.sum(SalesOrderSize.NetValue)]).\
            where(SalesOrderPickTicketDetail.ItemSalesOrderPickTicket_Id == cls.Id).\
            where(SalesOrderSize.Id == SalesOrderPickTicketDetail.ItemSalesOrderSize_Id).\
            as_scalar()

    @hybrid_property
    def total_valueinc(self):
        return sum(line.ItemSalesOrderSize.NetValueInc for line in self.Details)

    @total_valueinc.expression
    def total_valueinc(cls):
        from .SalesOrderPickTicketDetails import SalesOrderPickTicketDetail
        from .SalesOrderSizes import SalesOrderSize

        return select([func.sum(SalesOrderSize.NetValueInc)]).\
            where(SalesOrderPickTicketDetail.ItemSalesOrderPickTicket_Id == cls.Id).\
            where(SalesOrderSize.Id == SalesOrderPickTicketDetail.ItemSalesOrderSize_Id).\
            as_scalar()

    @hybrid_property
    def total_tax(self):
        return self.total_valueinc - self.total_value

    @total_tax.expression
    def total_tax(cls):
        return cls.total_valueinc - cls.total_value


Index("SalesOrderPickTicket_Index1", SalesOrderPickTicket.Company_Id,
      SalesOrderPickTicket.PTNumber, unique=True)

Index("SalesOrderPickTicket_Index2", SalesOrderPickTicket.Company_Id,
      SalesOrderPickTicket.Warehouse_Id, SalesOrderPickTicket.PTNumber, unique=True)

Index("SalesOrderPickTicket_Index3", SalesOrderPickTicket.Company_Id,
      SalesOrderPickTicket.Warehouse_Id, SalesOrderPickTicket.PTNumber,
      SalesOrderPickTicket.Customer_Id, SalesOrderPickTicket.DeliverVia_Id,
      SalesOrderPickTicket.Store_Id, unique=True)


def on_pick_ticket_update(mapper, connection, target):
    pass


def on_pick_ticket_delete(mapper, connection, target):
    pass


#event.listen(SalesOrderPickTicket, "before_insert", on_pick_ticket_update)  # Mapper Event
#event.listen(SalesOrderPickTicket, "before_update", on_pick_ticket_update)  # Mapper Event
#event.listen(SalesOrderPickTicket, "after_delete", on_pick_ticket_delete)  # Mapper Event

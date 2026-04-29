from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, String, DateTime, Date, Boolean,
                        Index, Numeric, event, func, select)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class SalesOrderContainer(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderContainers"
    __table_args__ = dict(info=dict(label="Sales Order Invoice",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="SSCC"
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SalesOrderContainer.Company_Id")

    # https://www.morovia.com/kb/Serial-Shipping-Container-Code-SSCC18-10601.html
    # 0 1234567 123456789 1 - 0=Carton, 1...7=Company, 1...9=Number, 1=CheckDigit
    SSCC = Column(String(18), nullable=False,
                  info=dict(label="Serial Shipping Container Number"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderContainer.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderContainer.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of SalesOrderDetails
    SalesOrders = relationship("SalesOrderDetail", uselist=True,
                               back_populates="Container",
                               info=dict(hidden=True, dump=False))


Index("SalesOrderContainer_Index1", SalesOrderContainer.Company_Id,
      SalesOrderContainer.SSCC, unique=True)


def on_sscc_insert(mapper, connection, target):
    pass


def on_sscc_update(mapper, connection, target):
    pass


def on_sscc_delete(mapper, connection, target):
    pass


event.listen(SalesOrderContainer, "before_insert", on_sscc_insert)  # Mapper Event
event.listen(SalesOrderContainer, "before_update", on_sscc_update)  # Mapper Event
event.listen(SalesOrderContainer, "before_delete", on_sscc_delete)  # Mapper Event

from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime,
                        Index, event)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class SalesOrderCreditNote(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderCreditNotes"
    __table_args__ = dict(info=dict(label="Sales Order Invoice",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="CreditNoteNumber"
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SalesOrderCreditNote.Company_Id")

    CreditNoteNumber = Column(Integer, nullable=False,
                              info=dict(label="CreditNote Number"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderCreditNote.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderCreditNote.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of SalesOrderDetails
    SalesOrders = relationship("SalesOrderDetail", uselist=True,
                               back_populates="CreditNote",
                               info=dict(hidden=True, dump=False))


Index("SalesOrderCreditNote_Index1", SalesOrderCreditNote.Company_Id,
      SalesOrderCreditNote.CreditNoteNumber, unique=True)


def on_credit_note_insert(mapper, connection, target):
    pass


def on_credit_note_update(mapper, connection, target):
    pass


def on_credit_note_delete(mapper, connection, target):
    pass


event.listen(SalesOrderCreditNote, "before_insert", on_credit_note_insert)  # Mapper Event
event.listen(SalesOrderCreditNote, "before_update", on_credit_note_update)  # Mapper Event
event.listen(SalesOrderCreditNote, "before_delete", on_credit_note_delete)  # Mapper Event

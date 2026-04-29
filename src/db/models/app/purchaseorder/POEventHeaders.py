from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, String, DateTime, Date, Boolean,
                        Index, Enum, Numeric, Text, event, func, select)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import get_currency_choices


class POEventHeader(Model):
    __versioned__ = {}
    __tablename__ = "POEventHeaders"
    __table_args__ = dict(info=dict(label="PO Event Header", desc="PO Event Header",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Format",
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==POEventHeader.Company_Id")

    Format = Column(String(8), nullable=False,
                    info=dict(label="Format", case="uppercase"))

    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    # Many2One
    Warehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                          nullable=False,
                          info=dict(label="Ship-to Warehouse",
                                    selectId="Id", selectKey="Name", depth=1))
    Warehouse = relationship("Warehouse",
                             primaryjoin="Warehouse.Id==POEventHeader.Warehouse_Id")

    # One2Many
    Details = relationship("POEventDetail", uselist=True,
                           backref="ItemPOEventHeader",
                           cascade="all, delete-orphan",
                           info=dict(dumpFields=["Id"]))

    # One2Many
    Comments = relationship("POEventComment", uselist=True,
                            backref="ItemPOEventHeader",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==POEventHeader.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==POEventHeader.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


    # One2Many side of POHeaders
    # uselist=False - this is just used in validate_delete
    POHeaders = relationship("POHeader", uselist=False,
                             back_populates="Event",
                             info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.POHeaders is not None:
            is_ok = False
            tables = "POHeaders"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this PO Event Header"

        return is_ok, message


Index("POEventHeader_Index1", POEventHeader.Company_Id,
      POEventHeader.Format, unique=True)

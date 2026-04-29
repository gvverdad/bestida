from datetime import datetime

from sqlalchemy import (Column, ForeignKey, String, Integer, DateTime, Index, Date,
                        Numeric, Boolean)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import get_currency_choices


class TaxType(Model):
    __versioned__ = {}
    __tablename__ = "TaxTypes"
    __table_args__ = dict(info=dict(label="Tax Type",
                                    companyField="Company_Id"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==TaxType.Company_Id")

    Type = Column(String(8), nullable=False, info=dict(label="Type",
                                                       case="uppercase",
                                                       selectId="Id",
                                                       selectKey="Type",
                                                       selectColumn="Type",
                                                       selectFormat=["Type", "Description"],
                                                       selectTable="TaxTypes"
                                                       ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==TaxType.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==TaxType.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of ProductSKU
    # uselist=False - this is just used in validate_delete
    SKUs = relationship("ProductSKU", uselist=False,
                        back_populates="TaxType",
                        info=dict(hidden=True, dump=False))
    SOExtras = relationship("SalesOrderExtraType", uselist=False,
                            back_populates="TaxType",
                            info=dict(hidden=True, dump=False))
    SalesAccounts = relationship("SalesAccount", uselist=False,
                                 back_populates="TaxType",
                                 info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.SKUs is not None:
            is_ok = False
            tables = "ProductSKUs"
        if self.SOExtras is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "SalesOrderExtraTypes"
        if self.SalesAccounts is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "SalesAccounts"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Tax Type"

        return is_ok, message


Index("TaxType_Index1", TaxType.Company_Id, TaxType.Type, unique=True)

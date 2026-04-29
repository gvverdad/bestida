from datetime import datetime

from sqlalchemy import (Column, ForeignKey, String, Integer, DateTime, Index,
                        Numeric, Boolean)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import get_currency_choices


class SalesOrderExtraType(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderExtraTypes"
    __table_args__ = dict(info=dict(label="Sales Order Extra Types",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Type"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company",
                           primaryjoin="Company.Id==SalesOrderExtraType.Company_Id")

    Currency = Column(String(3), nullable=False, default="AUD",
                      info=dict(label="Currency",
                                choices=get_currency_choices,
                                choices_getter="getCurrencyList"))

    Type = Column(String(16), nullable=False, info=dict(label="Type",
                                                        case="uppercase"))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    Calculated = Column(Boolean, default=False,
                        info=dict(label="Calculated",
                                  actionOn="{" +
                                           "\"baseFieldName\": \"Calculated\"," +
                                           "\"true\": {\"onFields\":[],\"offFields\":[\"Value\", \"Percentage\"]}," +
                                           "\"false\": {\"onFields\": [\"Value\",\"Percentage\"], \"offFields\": []}," +
                                           "}"
                                  ))

    # if not percentage then value is ex GST
    Value = Column(Numeric(19, 4), default=0, nullable=True,
                   info=dict(label="Value",
                             requiredIf="Calculated = false")
                   )

    Percentage = Column(Boolean, default=False,
                        info=dict(label="Percentage"))

    # Many2One
    TaxType_Id = Column(Integer, ForeignKey("TaxTypes.Id"), nullable=False,
                        info=dict(label="Tax Type", selectId="Id",
                                  selectKey="Description", depth=1))
    TaxType = relationship("TaxType",
                           primaryjoin="TaxType.Id==SalesOrderExtraType.TaxType_Id")

    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderExtraType.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderExtraType.CreateOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of SalesOrderExtras
    # uselist=False - this is just used in validate_delete
    SalesOrderExtras = relationship("SalesOrderExtra", uselist=False,
                                    back_populates="Type",
                                    info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.SalesOrderExtras is not None:
            is_ok = False
            tables = "SalesOrderExtras"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this SalesOrder Extra Type"

        return is_ok, message


Index("SalesOrderExtraType_Index1", SalesOrderExtraType.Company_Id,
      SalesOrderExtraType.Currency, SalesOrderExtraType.Type, unique=True)

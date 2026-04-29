from datetime import datetime

from sqlalchemy import (Column, ForeignKey, String, Integer, DateTime, Index, Date,
                        Numeric)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import get_currency_choices


class CurrencyExchange(Model):
    __versioned__ = {}
    __tablename__ = "CurrencyExchanges"
    __table_args__ = dict(info=dict(label="Currency Exchange",
                                    companyField="Company_Id"
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==CurrencyExchange.Company_Id")

    Currency = Column(String(3), nullable=False,
                      info=dict(label="Currency",
                                choices=get_currency_choices,       # server getter
                                choices_getter="getCurrencyList"))  # client getter

    EffectiveFrom = Column(Date(), nullable=False, info=dict(label="Effective Date From"))
    EffectiveTo = Column(Date(), nullable=False, info=dict(label="Effective Date To"))

    Rate = Column(Numeric(20, 8), nullable=False,
                  default=1,
                  info=dict(label="Exchange Rate To Base Currency",
                            numberType="currency",  # number, currency, percent, string
                            currencyCodeField="Currency",
                            validator=["NotZero", "Positive"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==CurrencyExchange.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CurrencyExchange.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Currency Exchange"

        return is_ok, message


Index("CurrencyExchange_Index1", CurrencyExchange.Company_Id,
      CurrencyExchange.Currency,
      CurrencyExchange.EffectiveFrom, CurrencyExchange.EffectiveTo,
      unique=True)

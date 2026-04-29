from datetime import datetime

from sqlalchemy import (Column, ForeignKey, String, Integer, DateTime, Index, Date,
                        Numeric)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import get_country_choices, get_default_country


class TaxRate(Model):
    __versioned__ = {}
    __tablename__ = "TaxRates"
    __table_args__ = dict(info=dict(label="Tax Rates",
                                    companyField="Company_Id"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==TaxRate.Company_Id")

    Country = Column(String(2), nullable=False, default=get_default_country,
                     info=dict(label="Country",
                               choices=get_country_choices,
                               choices_getter="getCountriesList"))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("TaxTypes.Id"),
                     nullable=False,
                     info=dict(label="Type", selectId="Id",
                               selectKey="Description",
                               depth=1))
    Type = relationship("TaxType", primaryjoin="TaxType.Id==TaxRate.Type_Id")

    EffectiveFrom = Column(Date(), nullable=False, info=dict(label="Effective Date From"))
    EffectiveTo = Column(Date(), nullable=False, info=dict(label="Effective Date To"))

    Rate = Column(Numeric(10, 6), nullable=False, default=0,
                  info=dict(label="Tax Rate%",
                            numberType="percent",  # number, currency, percent, string
                            validator=["ZeroPositive"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==TaxRate.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==TaxRate.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""
        # TODO: validate delete
        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Tax Rate"

        return is_ok, message


Index("TaxRate_Index1", TaxRate.Company_Id,
      TaxRate.Country, TaxRate.Type_Id,
      TaxRate.EffectiveFrom, TaxRate.EffectiveTo,
      unique=True)

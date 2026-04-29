from datetime import datetime

from sqlalchemy import event
from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Numeric,
                        Index, String, Boolean)
from sqlalchemy.orm import relationship

from src.db.models.model import Model
from src.db.models.functions import (get_locale_choices, get_default_locale,
                                     get_timezone_choices, get_default_timezone,
                                     get_country_choices, get_default_country,
                                     get_currency_choices, get_default_currency)

from src.security.policy import get_current_uid


class SalesAccount(Model):
    __versioned__ = {}
    __tablename__ = "SalesAccounts"
    __table_args__ = dict(info=dict(label="SalesAccounts",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Account",
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SalesAccount.Company_Id")

    Account = Column(String(16), nullable=False, info=dict(label="Sales Account",
                                                           case="uppercase"))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))
    ShortName = Column(String(32), info=dict(label="Short Name"))
    TradeName = Column(String(32), info=dict(label="Trade Name"))

    CompanyNumber = Column(String(32), info=dict(label="Company Number"))
    RegistrationId = Column(String(32), info=dict(label="Registration Id"))
    TaxId = Column(String(32), info=dict(label="Tax Id"))

    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User", primaryjoin="User.Id==SalesAccount.InactiveOpId_Id")
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp", modifiable=False))

    Country = Column(String(2), nullable=False, default=get_default_country,
                     info=dict(label="Country",
                               choices=get_country_choices,   # server getter
                               choices_getter="getCountriesList"))  # client getter

    Currency = Column(String(3), nullable=False, default=get_default_currency,
                      info=dict(label="Currency",
                                choices=get_currency_choices,   # server getter
                                choices_getter="getCurrencyList")) # client getter

    Locale = Column(String(8), nullable=False, default=get_default_locale,
                    info=dict(label="Locale",
                              choices=get_locale_choices,  # server getter
                              choices_getter="getLocaleList")) # client getter

    Timezone = Column(String(32), nullable=False, default=get_default_timezone,
                      info=dict(label="Timezone",
                                choices=get_timezone_choices, # server getter
                                choices_getter="getTimezoneList")) # client getter

    Commission = Column(Numeric(19, 4), nullable=False, default=0,
                        info=dict(label="Commission %",
                                  numberType="percent",
                                  validator=["ZeroPositive"]))

    # Many2One
    TaxType_Id = Column(Integer, ForeignKey("TaxTypes.Id"), nullable=False,
                        info=dict(label="Tax Type", selectId="Id",
                                  selectKey="Description", depth=1))
    TaxType = relationship("TaxType",
                           primaryjoin="TaxType.Id==SalesAccount.TaxType_Id")

    # One2Many
    Addresses = relationship("SalesAccountAddress", uselist=True,
                             backref="ItemSalesAccount",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"]))

    # One2Many
    Phones = relationship("SalesAccountPhone", uselist=True,
                          backref="ItemSalesAccount",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Emails = relationship("SalesAccountEmail", uselist=True,
                          backref="ItemSalesAccount",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Contacts = relationship("SalesAccountContact", uselist=True,
                            backref="ItemSalesAccount",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User",
                              primaryjoin="User.Id==SalesAccount.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp",
                                       modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesAccount.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp",
                                         modifiable=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"

        # TODO: validate against Orders

        return is_ok, message


Index("SalesAccount_Index1", SalesAccount.Company_Id, SalesAccount.Account,
      unique=True)

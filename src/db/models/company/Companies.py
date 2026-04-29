from datetime import datetime

from sqlalchemy import event
from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship

from ..model import Model
from ..functions import (get_locale_choices, get_timezone_choices,
                         get_country_choices, get_currency_choices,
                         get_default_country, get_default_locale,
                         get_default_timezone, get_default_currency)
from ....security.policy import get_current_uid
from ..security.Groups import company_group_table


class Company(Model):
    __versioned__ = {}
    __tablename__ = "Companies"
    __table_args__ = dict(info=dict(label="Company", desc="Company",
                                    companyField="Id",
                                    stepperTitleFields=["CompanyId", "Name"],
                                    key="CompanyId"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    CompanyId = Column(String(16), index=True, unique=True, nullable=False,
                       info=dict(label="Company", case="uppercase",
                                 selectId="Id",
                                 selectKey="CompanyId",
                                 selectColumn="CompanyId",
                                 selectFormat=["CompanyId", "Name"],
                                 selectGetter="/getCompaniesList",
                                 selectTable="Companies"
                                 ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))
    ShortName = Column(String(32), info=dict(label="Short Name"))
    TradeName = Column(String(32), info=dict(label="Trade Name"))    

    CompanyNumber = Column(String(32), info=dict(label="GS1 Company Number"))
    RegistrationId = Column(String(32), info=dict(label="Registration Id"))
    TaxId = Column(String(32), info=dict(label="Tax Id"))
    
    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User", primaryjoin="User.Id==Company.InactiveOpId_Id")
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp",
                                         modifiable=False))

    Country = Column(String(2), nullable=False, default=get_default_country,
                     info=dict(label="Country",
                               choices=get_country_choices,         # server getter
                               choices_getter="getCountriesList"))  # client getter

    Currency = Column(String(3), nullable=False, default=get_default_currency,
                      info=dict(label="Base Currency",
                                choices=get_currency_choices,       # server getter
                                choices_getter="getCurrencyList"))  # client getter

    Locale = Column(String(8), nullable=False, default=get_default_locale,
                    info=dict(label="Locale",
                              choices=get_locale_choices,           # server getter
                              choices_getter="getLocaleList"))      # client getter

    Timezone = Column(String(32), nullable=False, default=get_default_timezone,
                      info=dict(label="Timezone",
                                choices=get_timezone_choices,
                                choices_getter="getTimezoneList"))

    SalesOrderPrefix = Column(String(3), nullable=True,
                              info=dict(label="Sales Order Number Prefix",
                                        min=3))

    PurchaseOrderPrefix = Column(String(3), nullable=True,
                                 info=dict(label="Purchase Order Number Prefix",
                                           min=3))

    ProductionOrderPrefix = Column(String(3), nullable=True,
                                   info=dict(label="Production Order Number Prefix",
                                             min=3))

    # One2Many    
    Addresses = relationship("CompanyAddress", uselist=True, backref="ItemCompany",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"]))

    # One2Many    
    Phones = relationship("CompanyPhone", uselist=True, backref="ItemCompany",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many    
    Emails = relationship("CompanyEmail", uselist=True, backref="ItemCompany",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Company.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Company.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # Many2Many
    Groups = relationship("Group",
                          secondary=company_group_table,
                          back_populates="Companies",
                          info=dict(hidden=True, dump=False))

    # One2Many side of User
    # uselist=False - this is just used in validate_delete
    Users = relationship("User", uselist=False, back_populates="Company",
                         primaryjoin="User.Company_Id==Company.Id",
                         info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"

        if company_rowid == self.Id:
            is_ok = False
            message = "Cannot Delete Current Company"
            return is_ok, message

        if self.Users is not None:
            is_ok = False
            message = "Cannot Delete. There are Users linked to this Company"

        return is_ok, message


def on_company_update(mapper, connection, target):
    inactive = getattr(target, "Inactive")
    if inactive and getattr(target, "InactiveTimeStamp") is None:
        setattr(target, "InactiveTimeStamp", datetime.utcnow())
        setattr(target, "InactiveOpId_Id", get_current_uid())
    elif not inactive and getattr(target, "InactiveTimeStamp") is not None:
        setattr(target, "InactiveTimeStamp", None)
        setattr(target, "InactiveOpId_Id", None)


event.listen(Company, "before_update", on_company_update)  # Mapper Event
event.listen(Company, "before_insert", on_company_update)  # mapper Event

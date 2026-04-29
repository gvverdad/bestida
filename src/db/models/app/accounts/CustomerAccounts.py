from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Numeric,
                        String, Boolean, event)
from sqlalchemy.orm import relationship

from ...model import Model
from ...functions import get_country_choices, get_currency_choices
from .....security.policy import get_current_uid


class CustomerAccount(Model):
    __versioned__ = {}
    __tablename__ = "CustomerAccounts"
    __table_args__ = dict(info=dict(label="Customer Accounts",
                                    desc="Accounts",
                                    parentTables=[
                                        dict(column="ItemCustomer",
                                             table="Customers")
                                    ],
                                    crud_options=dict(
                                        new=False,
                                        copy=False,
                                        edit=True,
                                        delete=False
                                    ))
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # OneToOne side of Customer
    ItemCustomer_Id = Column(Integer, ForeignKey("Customers.Id"),
                             info=dict(label="Customer Account",
                                       selectId="Id",
                                       selectKey="Name",
                                       selectFormat=["Account", "Name"],
                                       exceptSchemaFields=["CustomerAccount",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       depth=1))
    ItemCustomer = relationship("Customer", back_populates="CustomerAccount",
                                primaryjoin="Customer.Id==CustomerAccount.ItemCustomer_Id")

    RegistrationId = Column(String(32), info=dict(label="Registration Id"))
    TaxId = Column(String(32), info=dict(label="Tax Id"))

    Country = Column(String(2), nullable=False, default="AU",
                     info=dict(label="Country",
                               choices=get_country_choices,
                               choices_getter="getCountriesList"))

    Currency = Column(String(3), nullable=False, default="AUD",
                      info=dict(label="Currency",
                                choices=get_currency_choices,
                                choices_getter="getCurrencyList"))

    # Many2One
    TradingTerms_Id = Column(Integer, ForeignKey("TradingTerms.Id"), nullable=False,
                             info=dict(label="Trading Terms", selectId="Id",
                                       selectKey="Type",
                                       selectFormat=["Description"],
                                       depth=1))
    TradingTerms = relationship("TradingTerm",
                                primaryjoin="TradingTerm.Id==CustomerAccount.TradingTerms_Id")

    TradeDiscount = Column(Numeric(8, 4), default=0, nullable=True,
                           info=dict(label="Trade Discount Percentage",
                                     numberType="percent",
                                     validator=["ZeroPositive"]))

    CreditHold = Column(Boolean, default=False, nullable=False,
                        info=dict(label="Credit Hold"))
    # Many2One
    CreditHoldSetOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                                  info=dict(label="CreditHold Set By",
                                            modifiable=False))
    CreditHoldSetOpId = relationship("User",
                                     primaryjoin="User.Id==CustomerAccount.CreditHoldSetOpId_Id")
    CreditHoldSetTimeStamp = Column(DateTime, nullable=True,
                                    info=dict(label="CreditHold Set Timestamp",
                                              modifiable=False))

    AllocationHold = Column(Boolean, default=False, nullable=False,
                            info=dict(label="Allocation Hold"))
    # Many2One
    AllocationHoldSetOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                                      info=dict(label="AllocationHold Set By",
                                                modifiable=False))
    AllocationHoldSetOpId = relationship("User",
                                         primaryjoin="User.Id==CustomerAccount.AllocationHoldSetOpId_Id")
    AllocationHoldSetTimeStamp = Column(DateTime, nullable=True,
                                        info=dict(label="AllocationHold Set Timestamp",
                                                  modifiable=False))

    CheckCreditLimit = Column(Boolean, default=False, nullable=False,
                              info=dict(label="Check Credit Limit",
                                        actionOn="{" +
                                           "\"baseFieldName\": \"CheckCreditLimit\"," +
                                           "\"true\": {\"onFields\":[\"CreditLimit\"],\"offFields\":[]}," +
                                           "\"false\": {\"onFields\": [], \"offFields\": [\"CreditLimit\"]}," +
                                           "}"
                                        ))

    CreditLimit = Column(Numeric(19, 4), default=0, nullable=True,
                         info=dict(label="Credit Limit",
                                   numberType="currency",  # number, currency, percent, string
                                   currencyCodeField="Currency",
                                   requiredIf="CheckCreditLimit == true",
                                   validator=["ZeroPositive"])
                         )

    # Many2One
    CreditLimitSetOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                                   info=dict(label="CreditLimit Set By",
                                             modifiable=False))
    CreditLimitSetOpId = relationship("User",
                                      primaryjoin="User.Id==CustomerAccount.CreditLimitSetOpId_Id")
    CreditLimitSetTimeStamp = Column(DateTime, nullable=True,
                                     info=dict(label="CreditLimit Set Timestamp",
                                               modifiable=False))

    CheckExposureLimit = Column(Boolean, default=False, nullable=False,
                                info=dict(label="Check Exposure Limit",
                                          actionOn="{" +
                                           "\"baseFieldName\": \"CheckExposureLimit\"," +
                                           "\"true\": {\"onFields\":[\"ExposureLimit\"],\"offFields\":[]}," +
                                           "\"false\": {\"onFields\": [], \"offFields\": [\"ExposureLimit\"]}," +
                                           "}"
                                          ))

    ExposureLimit = Column(Numeric(19, 4), default=0, nullable=True,
                           info=dict(label="Exposure Limit",
                                     numberType="currency",  # number, currency, percent, string
                                     currencyCodeField="Currency",
                                     requiredIf="CheckExposureLimit == true",
                                     validator=["ZeroPositive"])
                           )

    # Many2One
    ExposureLimitSetOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=True,
                                     info=dict(label="ExposureLimit Set By",
                                               modifiable=False))
    ExposureLimitSetOpId = relationship("User",
                                        primaryjoin="User.Id==CustomerAccount.ExposureLimitSetOpId_Id")
    ExposureLimitSetTimeStamp = Column(DateTime, nullable=True,
                                       info=dict(label="ExposureLimit Set Timestamp",
                                                 modifiable=False))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User",
                              primaryjoin="User.Id==CustomerAccount.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp",
                                       modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CustomerAccount.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp",
                                         modifiable=False))


def on_customer_account_insert(mapper, connection, target):
    on_customer_account_update(mapper, connection, target)


def on_customer_account_update(mapper, connection, target):

    credit_hold = getattr(target, "CreditHold")
    if credit_hold and getattr(target, "CreditHoldSetTimeStamp") is None:
        setattr(target, "CreditHoldSetTimeStamp", datetime.utcnow())
        setattr(target, "CreditHoldSetOpId_Id", get_current_uid())
    elif not credit_hold and getattr(target, "CreditHoldSetTimeStamp") is not None:
        setattr(target, "CreditHoldSetTimeStamp", None)
        setattr(target, "CreditHoldSetOpId_Id", None)

    allocation_hold = getattr(target, "AllocationHold")
    if allocation_hold and getattr(target, "AllocationHoldSetTimeStamp") is None:
        setattr(target, "AllocationHoldSetTimeStamp", datetime.utcnow())
        setattr(target, "AllocationHoldSetOpId_Id", get_current_uid())
    elif not allocation_hold and getattr(target, "AllocationHoldSetTimeStamp") is not None:
        setattr(target, "AllocationHoldSetTimeStamp", None)
        setattr(target, "AllocationHoldSetOpId_Id", None)

    check_credit = getattr(target, "CheckCreditLimit")
    if check_credit and getattr(target, "CreditLimitSetTimeStamp") is None:
        setattr(target, "CreditLimitSetTimeStamp", datetime.utcnow())
        setattr(target, "CreditLimitSetOpId_Id", get_current_uid())
    elif not check_credit and getattr(target, "CreditLimitSetTimeStamp") is not None:
        setattr(target, "CreditLimitSetTimeStamp", None)
        setattr(target, "CreditLimitSetOpId_Id", None)

    check_exposure = getattr(target, "CheckExposureLimit")
    if check_exposure and getattr(target, "ExposureLimitSetTimeStamp") is None:
        setattr(target, "ExposureLimitSetTimeStamp", datetime.utcnow())
        setattr(target, "ExposureLimitSetOpId_Id", get_current_uid())
    elif not check_exposure and getattr(target, "CreditLimitSetTimeStamp") is not None:
        setattr(target, "ExposureLimitSetTimeStamp", None)
        setattr(target, "ExposureLimitSetOpId_Id", None)


event.listen(CustomerAccount, "before_insert", on_customer_account_insert)  # Mapper Event
event.listen(CustomerAccount, "before_update", on_customer_account_update)  # Mapper Event

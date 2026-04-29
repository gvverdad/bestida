from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Numeric,
                        String, Boolean, event)
from sqlalchemy.orm import relationship

from ...model import Model
from ...functions import get_country_choices, get_currency_choices
from .....security.policy import get_current_uid


class SupplierAccount(Model):
    __versioned__ = {}
    __tablename__ = "SupplierAccounts"
    __table_args__ = dict(info=dict(label="Supplier Accounts",
                                    desc="Accounts",
                                    parentTables=[
                                        dict(column="SupplierAccount",
                                             table="Suppliers")
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

    # OneToOne side of Supplier
    ItemSupplier_Id = Column(Integer, ForeignKey("Suppliers.Id"),
                             info=dict(label="Supplier Account",
                                       modifiable=False,
                                       selectId="Id",
                                       selectKey="Name",
                                       selectFormat=["Account", "Name"],
                                       exceptSchemaFields=["SupplierAccount",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       depth=1))
    ItemSupplier = relationship("Supplier", back_populates="SupplierAccount",
                                primaryjoin="Supplier.Id==SupplierAccount.ItemSupplier_Id")

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
                                       selectKey="Description",
                                       depth=1))
    TradingTerms = relationship("TradingTerm",
                                primaryjoin="TradingTerm.Id==SupplierAccount.TradingTerms_Id")

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User",
                              primaryjoin="User.Id==SupplierAccount.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp",
                                       modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SupplierAccount.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp",
                                         modifiable=False))


def on_supplier_account_insert(mapper, connection, target):
    pass


def on_supplier_account_update(mapper, connection, target):
    pass


event.listen(SupplierAccount, "before_insert", on_supplier_account_insert)  # Mapper Event
event.listen(SupplierAccount, "before_update", on_supplier_account_update)  # Mapper Event

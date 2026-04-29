from datetime import datetime

from sqlalchemy import event
from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Enum,
                        Index, String, Boolean)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid
from ...functions import (get_locale_choices, get_timezone_choices)


class SupplierStore(Model):
    __versioned__ = {}
    __tablename__ = "SupplierStores"
    __table_args__ = dict(info=dict(label="Supplier Stores", desc="Stores",
                                    companyField="Company_Id",
                                    stepperTitleFields=["Store", "Name"],
                                    keyPaths=["ItemSupplier_Id"],
                                    key="Store",
                                    parentTables=[
                                        dict(column="ItemSupplier")
                                    ]
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SupplierStore.Company_Id")

    # Many2One side of Supplier
    ItemSupplier_Id = Column(Integer, ForeignKey("Suppliers.Id"),
                             info=dict(label="Account",
                                       selectId="Id",
                                       selectKey="Name",
                                       exceptSchemaFields=["Company_Id", "Company", "Stores",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       depth=1))

    Store = Column(String(16), nullable=False, info=dict(label="Store Code",
                                                         case="uppercase"))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))

    InterchangeNumber = Column(String(32), info=dict(label="Interchange Number"))
    SupplierNumber = Column(String(32), info=dict(label="Supplier Number"))

    InterCompany = Column(Boolean, default=False, info=dict(label="InterCompany Account"))

    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User", primaryjoin="User.Id==SupplierStore.InactiveOpId_Id")
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp", modifiable=False))

    Locale = Column(String(8), nullable=True,
                    info=dict(label="Locale",
                              choices=get_locale_choices,
                              choices_getter="getLocaleList"))

    Timezone = Column(String(32), nullable=True,
                      info=dict(label="Timezone",
                                choices=get_timezone_choices,
                                choices_getter="getTimezoneList"))

    # Many2One
    Region_Id = Column(Integer, ForeignKey("SupplierRegions.Id"), nullable=True,
                       info=dict(label="Region", selectId="Id",
                                 selectKey="Description", depth=1))
    Region = relationship("SupplierRegion", primaryjoin="SupplierRegion.Id==SupplierStore.Region_Id")

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SupplierTypes.Id"), nullable=True,
                     info=dict(label="Type",
                               selectId="Id",
                               selectKey="Description",
                               depth=1))
    Type = relationship("SupplierType", primaryjoin="SupplierType.Id==SupplierStore.Type_Id")

    # Many2One
    Class_Id = Column(Integer, ForeignKey("SupplierClasses.Id"), nullable=True,
                      info=dict(label="Class", selectId="Id",
                                selectKey="Description", depth=1))
    Class = relationship("SupplierClass", primaryjoin="SupplierClass.Id==SupplierStore.Class_Id")

    # Many2One
    Group_Id = Column(Integer, ForeignKey("SupplierGroups.Id"), nullable=True,
                      info=dict(label="Group", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Group = relationship("SupplierGroup", primaryjoin="SupplierGroup.Id==SupplierStore.Group_Id")

    AllowSupplies = Column(Boolean, default=False, info=dict(label="Allow Supplies"))

    PODateInterval = Column(Integer, default=0, nullable=False,
                            info=dict(label="PO/Start Event Interval Days",
                                      validator=["ZeroPositive"]))

    # CMTInvoiced. RM will become the property of the Manufacturer upon despatched
    # and stock down dated. The Manufacturer will be invoiced
    # CMTStock. RM will be transferred to a virtual warehouse
    # and stock down dated.
    POType = Column(Enum("Goods", "CMTStock", "CMTInvoiced", "Sundry",
                         name="POType"),
                    nullable=False, default="Goods",
                    info=dict(label="PO Type")
                    )

    # One2One side of SupplierProcessingGroup
    ProcessingGroups = relationship("SupplierProcessingGroup", uselist=False,
                                    back_populates="ItemSupplierStore",
                                    primaryjoin="SupplierProcessingGroup.ItemSupplierStore_Id==SupplierStore.Id",
                                    cascade="all, delete-orphan",
                                    info=dict(label="Processing Groups",
                                              gridSubTable=True,
                                              dumpFields=["Id"]))

    # One2Many
    Addresses = relationship("SupplierStoreAddress", uselist=True,
                             backref="ItemSupplierStore",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"],
                                       requiredEntry=dict(type="AddressType.Type",
                                                          value=["MAIN"],
                                                          min=1),
                                       depth=1))

    # One2Many
    Phones = relationship("SupplierStorePhone", uselist=True,
                          backref="ItemSupplierStore",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Emails = relationship("SupplierStoreEmail", uselist=True,
                          backref="ItemSupplierStore",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Contacts = relationship("SupplierStoreContact", uselist=True,
                            backref="ItemSupplierStore",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SupplierStore.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SupplierStore.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"

        # TODO: validate against PO Orders

        return is_ok, message


Index("SupplierStore_Index1", SupplierStore.Company_Id,
      SupplierStore.ItemSupplier_Id,
      SupplierStore.Store, unique=True)
Index("SupplierStore_Index2", SupplierStore.Company_Id,
      SupplierStore.InterchangeNumber, unique=False)
Index("SupplierStore_Index3", SupplierStore.Company_Id,
      SupplierStore.SupplierNumber, unique=False)
Index("SupplierStore_Index4", SupplierStore.Company_Id,
      SupplierStore.Type_Id, unique=False)
Index("SupplierStore_Index5", SupplierStore.Company_Id,
      SupplierStore.Class_Id, unique=False)
Index("SupplierStore_Index6", SupplierStore.Company_Id,
      SupplierStore.Group_Id, unique=False)
Index("SupplierStore_Index7", SupplierStore.Company_Id,
      SupplierStore.Region_Id, unique=False)


def on_customer_store_update(mapper, connection, target):
    inactive = getattr(target, "Inactive")
    if inactive and getattr(target, "InactiveTimeStamp") is None:
        setattr(target, "InactiveTimeStamp", datetime.utcnow())
        setattr(target, "InactiveOpId_Id", get_current_uid())
    elif not inactive and getattr(target, "InactiveTimeStamp") is not None:
        setattr(target, "InactiveTimeStamp", None)
        setattr(target, "InactiveOpId_Id", None)


event.listen(SupplierStore, "before_update", on_customer_store_update)  # Mapper Event
event.listen(SupplierStore, "before_insert", on_customer_store_update)  # mapper Event

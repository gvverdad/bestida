from datetime import datetime

from sqlalchemy import event
from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Enum,
                        Index, String, Boolean, Table, func, select)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from ...functions import (get_locale_choices, get_timezone_choices)
from .....security.policy import get_current_uid

keyword_supplier_table = Table("keyword_supplier", Model.metadata,
                               Column("Id", Integer, autoincrement=True,
                                      primary_key=True, nullable=False),
                               Column("keyword_id", Integer, ForeignKey("SupplierKeywords.Id")),
                               Column("supplier_id", Integer, ForeignKey("Suppliers.Id"))
                               )
keyword_supplier_table.__versioned__ = {}  # Mark the secondary table for versioning

class Supplier(Model):
    __versioned__ = {}
    __tablename__ = "Suppliers"
    __table_args__ = dict(info=dict(label="Suppliers",
                                    companyField="Company_Id",
                                    stepperTitleFields=["Account", "Name"],
                                    keyPaths=["Company_Id"],
                                    key="Account",
                                    hybrids=[dict(name="number_of_stores",
                                                  label="Stores",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             ]
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==Supplier.Company_Id")

    Account = Column(String(16), nullable=False,
                     info=dict(label="Account Code", case="uppercase",
                               selectId="Id",
                               selectKey="Name",
                               documents=[dict(program="DocumentSupplier",
                                              params=dict(supplier="Account Code"))
                                         ]
                               ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))
    ShortName = Column(String(32), info=dict(label="Short Name"))
    TradeName = Column(String(32), info=dict(label="Trade Name"))

    # Many2Many
    Keywords = relationship("SupplierKeyword", secondary=keyword_supplier_table,
                            back_populates="Suppliers",
                            info=dict(label="Search Keywords",
                                      selectId="Id", selectKey="Keyword",
                                      depth=1))

    InterchangeNumber = Column(String(32), info=dict(label="Interchange Number"))
    SupplierNumber = Column(String(32), info=dict(label="Supplier Number"))

    InterCompany = Column(Boolean, default=False, info=dict(label="InterCompany Account"))

    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User", primaryjoin="User.Id==Supplier.InactiveOpId_Id")
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp", modifiable=False))

    Locale = Column(String(8), nullable=False, default="en-au",
                    info=dict(label="Locale",
                              choices=get_locale_choices,
                              choices_getter="getLocaleList"))

    Timezone = Column(String(32), nullable=False, default="Australia/Melbourne",
                      info=dict(label="Timezone",
                                choices=get_timezone_choices,
                                choices_getter="getTimezoneList"))

    # Many2One
    Region_Id = Column(Integer, ForeignKey("SupplierRegions.Id"),
                       nullable=False,
                       info=dict(label="Region", selectId="Id",
                                 selectKey="Description",
                                 depth=1))
    Region = relationship("SupplierRegion", primaryjoin="SupplierRegion.Id==Supplier.Region_Id")

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SupplierTypes.Id"),
                     nullable=False, info=dict(label="Type", selectId="Id",
                                               selectKey="Description",
                                               depth=1))
    Type = relationship("SupplierType", primaryjoin="SupplierType.Id==Supplier.Type_Id")

    # Many2One
    Class_Id = Column(Integer, ForeignKey("SupplierClasses.Id"), nullable=False,
                      info=dict(label="Class", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Class = relationship("SupplierClass", primaryjoin="SupplierClass.Id==Supplier.Class_Id")

    # Many2One
    Group_Id = Column(Integer, ForeignKey("SupplierGroups.Id"), nullable=False,
                      info=dict(label="Group", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Group = relationship("SupplierGroup", primaryjoin="SupplierGroup.Id==Supplier.Group_Id")

    AllowSupplies = Column(Boolean, default=False, info=dict(label="Allow Supplies"))

    # One2One side of Accounts
    SupplierAccount = relationship("SupplierAccount", uselist=False,
                                   back_populates="ItemSupplier",
                                   primaryjoin="SupplierAccount.ItemSupplier_Id==Supplier.Id",
                                   cascade="all, delete-orphan",
                                   info=dict(label="Supplier Account",
                                             gridSubTable=True,
                                             exceptSchemaFields=["Company", "ItemSupplier",
                                                                 "CreateTimeStamp", "CreateOpId",
                                                                 "ModifiedTimeStamp", "ModifiedOpId",
                                                                 "versions"],
                                             dumpFields=["Id"]))

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
                                    back_populates="ItemSupplier",
                                    primaryjoin="SupplierProcessingGroup.ItemSupplier_Id==Supplier.Id",
                                    cascade="all, delete-orphan",
                                    info=dict(label="Processing Groups",
                                              gridSubTable=True,
                                              dumpFields=["Id"]))

    # One2Many
    Addresses = relationship("SupplierAddress", uselist=True,
                             backref="ItemSupplier",
                             cascade="all, delete-orphan",
                             info=dict(dumpFields=["Id"],
                                       requiredEntry=dict(type="AddressType.Type",
                                                          value=["MAIN"],
                                                          min=1),
                                       depth=1))

    # One2Many
    Phones = relationship("SupplierPhone", uselist=True, backref="ItemSupplier",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Emails = relationship("SupplierEmail", uselist=True, backref="ItemSupplier",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # One2Many
    Contacts = relationship("SupplierContact", uselist=True,
                            backref="ItemSupplier",
                            cascade="all, delete-orphan",
                            info=dict(dumpFields=["Id"]))

    # One2Many
    Stores = relationship("SupplierStore", uselist=True, backref="ItemSupplier",
                          cascade="all, delete-orphan",
                          info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User",
                              primaryjoin="User.Id==Supplier.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp",
                                       modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User",
                                primaryjoin="User.Id==Supplier.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp",
                                         modifiable=False))

    # One2Many side of POHeader
    # uselist=False - this is just used in validate_delete
    PurchaseOrders = relationship("POHeader", uselist=False,
                                  back_populates="Supplier",
                                  primaryjoin="POHeader.Supplier_Id==Supplier.Id",
                                  info=dict(hidden=True, dump=False))

    @hybrid_property
    def number_of_stores(self):
        return len(self.Stores)

    @number_of_stores.expression
    def number_of_stores(cls):
        from .SupplierStores import SupplierStore

        return select([func.count()]).\
            where(SupplierStore.ItemSupplier_Id == cls.Id).as_scalar()

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"

        if self.PurchaseOrders is not None:
            is_ok = False
            tables = "PO Headers"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Supplier"

        return is_ok, message


Index("Supplier_Index1", Supplier.Company_Id, Supplier.Account, unique=True)
Index("Supplier_Index2", Supplier.Company_Id,
      Supplier.InterchangeNumber, unique=False)
Index("Supplier_Index3", Supplier.Company_Id,
      Supplier.SupplierNumber, unique=False)
Index("Supplier_Index4", Supplier.Company_Id, Supplier.Type_Id, unique=False)
Index("Supplier_Index5", Supplier.Company_Id, Supplier.Class_Id, unique=False)
Index("Supplier_Index6", Supplier.Company_Id, Supplier.Group_Id, unique=False)
Index("Supplier_Index7", Supplier.Company_Id, Supplier.Region_Id, unique=False)


def on_Supplier_update(mapper, connection, target):
    inactive = getattr(target, "Inactive")
    if inactive and getattr(target, "InactiveTimeStamp") is None:
        setattr(target, "InactiveTimeStamp", datetime.utcnow())
        setattr(target, "InactiveOpId_Id", get_current_uid())
    elif not inactive and getattr(target, "InactiveTimeStamp") is not None:
        setattr(target, "InactiveTimeStamp", None)
        setattr(target, "InactiveOpId_Id", None)


event.listen(Supplier, "before_update", on_Supplier_update)  # Mapper Event
event.listen(Supplier, "before_insert", on_Supplier_update)  # mapper Event

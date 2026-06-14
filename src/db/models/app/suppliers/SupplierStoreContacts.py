from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...person.Persons import Person


class SupplierStoreContact(Person):
    __versioned__ = {}
    __tablename__ = "SupplierStoreContacts"
    __table_args__ = dict(info=dict(label="Supplier Store Contacts",
                                    desc="Contacts",
                                    stepperTitleFields=["Type.Type", "LastName"],
                                    parentTables=[
                                        dict(column="ItemSupplierStore",
                                             table="SupplierStores")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Persons.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SupplierContactTypes.Id"),
                     nullable=False,
                     info=dict(label="Contact Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("SupplierContactType",
                        primaryjoin="SupplierContactType.Id==SupplierStoreContact.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "SupplierStoreContact"
    }    

    # ManyToOne side of SupplierStore
    ItemSupplierStore_Id = Column(Integer, ForeignKey("SupplierStores.Id"),
                                  info=dict(hidden=True,
                                            exceptSchemaFields=["Contacts",
                                                                "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                "versions"],
                                            ))

Index("SupplierStoreContact_Index1", SupplierStoreContact.ItemSupplierStore_Id,
      SupplierStoreContact.Type_Id, unique=True)

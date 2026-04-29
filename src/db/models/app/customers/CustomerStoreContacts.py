from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...person.Persons import Person


class CustomerStoreContact(Person):
    __versioned__ = {}
    __tablename__ = "CustomerStoreContacts"
    __table_args__ = dict(info=dict(label="Customer Store Contacts", desc="Contacts",
                                    stepperTitleFields=["Type.Type", "LastName"]))
        
    Id = Column(Integer, ForeignKey("Persons.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CustomerContactTypes.Id"),
                     nullable=False,
                     info=dict(label="Contact Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("CustomerContactType",
                        primaryjoin="CustomerContactType.Id==CustomerStoreContact.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "CustomerStoreContact"
    }    

    # ManyToOne side of CustomerStore
    ItemCustomerStore_Id = Column(Integer, ForeignKey("CustomerStores.Id"),
                                  info=dict(hidden=True,
                                            exceptSchemaFields=["Contacts",
                                                                "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                "versions"],
                                            ))


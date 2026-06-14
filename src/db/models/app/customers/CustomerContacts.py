from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...person.Persons import Person


class CustomerContact(Person):
    __versioned__ = {}
    __tablename__ = "CustomerContacts"
    __table_args__ = dict(info=dict(label="Customer Contacts",
                                    desc="Contacts",
                                    stepperTitleFields=["Type.Type", "LastName"],
                                    parentTables=[
                                        dict(column="ItemCustomer",
                                             table="Customers")
                                    ]
                                    ))
        
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
                        primaryjoin="CustomerContactType.Id==CustomerContact.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "CustomerContact"
    }    

    # ManyToOne side of Customer
    ItemCustomer_Id = Column(Integer, ForeignKey("Customers.Id"),
                             info=dict(hidden=True,
                                       exceptSchemaFields=["Contacts",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       ))

Index("CustomerContact_Index1", CustomerContact.ItemCustomer_Id,
      CustomerContact.Type_Id, unique=True)

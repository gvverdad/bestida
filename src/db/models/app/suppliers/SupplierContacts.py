from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...person.Persons import Person


class SupplierContact(Person):
    __versioned__ = {}
    __tablename__ = "SupplierContacts"
    __table_args__ = dict(info=dict(label="Supplier Contacts",
                                    desc="Contacts",
                                    stepperTitleFields=["Type.Type", "LastName"],
                                    parentTables=[
                                        dict(column="ItemSupplier",
                                             table="Suppliers")
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
                        primaryjoin="SupplierContactType.Id==SupplierContact.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "SupplierContact"
    }    

    # ManyToOne side of Supplier
    ItemSupplier_Id = Column(Integer, ForeignKey("Suppliers.Id"),
                             info=dict(hidden=True,
                                       exceptSchemaFields=["Contacts",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       ))

Index("SupplierContact_Index1", SupplierContact.ItemSupplier_Id,
      SupplierContact.Type_Id, unique=True)

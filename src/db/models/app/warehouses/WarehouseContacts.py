from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...person.Persons import Person


class WarehouseContact(Person):
    __versioned__ = {}
    __tablename__ = "WarehouseContacts"
    __table_args__ = dict(info=dict(label="Warehouse Contacts", desc="Contacts",
                                    stepperTitleFields=["Type.Type", "LastName"]))
        
    Id = Column(Integer, ForeignKey("Persons.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("WarehouseContactTypes.Id"),
                     nullable=False,
                     info=dict(label="Contact Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("WarehouseContactType",
                        primaryjoin="WarehouseContactType.Id==WarehouseContact.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "WarehouseContact"
    }    

    # ManyToOne side of Warehouse
    ItemWarehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                              info=dict(hidden=True,
                                        exceptSchemaFields=["Contacts",
                                                            "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                            "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                            "versions"],
                                        ))

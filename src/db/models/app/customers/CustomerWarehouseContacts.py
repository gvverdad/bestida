from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...person.Persons import Person


class CustomerWarehouseContact(Person):
    __versioned__ = {}
    __tablename__ = "CustomerWarehouseContacts"
    __table_args__ = dict(info=dict(label="Customer Warehouse Contacts",
                                    desc="Contacts",
                                    stepperTitleFields=["Type.Type", "LastName"],
                                    parentTables=[
                                        dict(column="ItemCustomerWarehouse",
                                             table="CustomerWarehouses")
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
                        primaryjoin="CustomerContactType.Id==CustomerWarehouseContact.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "CustomerWarehouseContact"
    }    

    # ManyToOne side of CustomerWarehouse
    ItemCustomerWarehouse_Id = Column(Integer, ForeignKey("CustomerWarehouses.Id"),
                                      info=dict(hidden=True,
                                                exceptSchemaFields=["Contacts",
                                                                    "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                    "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                    "versions"],
                                                ))

Index("CustomerWarehouseContact_Index1", CustomerWarehouseContact.ItemCustomerWarehouse_Id,
      CustomerWarehouseContact.Type_Id, unique=True)

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...address.Phones import Phone


class CustomerWarehousePhone(Phone):
    __versioned__ = {}
    __tablename__ = "CustomerWarehousePhones"
    __table_args__ = dict(info=dict(label="Customer Warehouse Phones", desc="Phones"))
        
    Id = Column(Integer, ForeignKey("Phones.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CustomerPhoneTypes.Id"),
                     nullable=False,
                     info=dict(label="Phone Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("CustomerPhoneType",
                        primaryjoin="CustomerPhoneType.Id==CustomerWarehousePhone.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "CustomerWarehouse"
    }        
                                              
    # ManyToOne side of CustomerWarehouse
    ItemCustomerWarehouse_Id = Column(Integer, ForeignKey("CustomerWarehouses.Id"),
                                      info=dict(hidden=True,
                                                exceptSchemaFields=["Phones",
                                                                    "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                    "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                    "versions"],
                                                ))

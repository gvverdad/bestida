from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...address.Addresses import Address


class CustomerWarehouseAddress(Address):
    __versioned__ = {}
    __tablename__ = "CustomerWarehouseAddresses"
    __table_args__ = dict(info=dict(label="Customer Warehouse Addresses", desc="Address"))
        
    Id = Column(Integer, ForeignKey("Addresses.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CustomerAddressTypes.Id"),
                     nullable=False,
                     info=dict(label="Address Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("CustomerAddressType",
                        primaryjoin="CustomerAddressType.Id==CustomerWarehouseAddress.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "CustomerWarehouse"
    }    
                                                  
    # ManyToOne side of CustomerWarehouse
    ItemCustomerWarehouse_Id = Column(Integer, ForeignKey("CustomerWarehouses.Id"),
                                      info=dict(hidden=True,
                                                exceptSchemaFields=["Addresses",
                                                                    "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                    "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                    "versions"],
                                                ))

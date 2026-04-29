from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...address.Addresses import Address


class WarehouseAddress(Address):
    __versioned__ = {}
    __tablename__ = "WarehouseAddresses"
    __table_args__ = dict(info=dict(label="Warehouse Addresses", desc="Addresses"))
        
    Id = Column(Integer, ForeignKey("Addresses.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("WarehouseAddressTypes.Id"),
                     nullable=False,
                     info=dict(label="Address Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("WarehouseAddressType",
                        primaryjoin="WarehouseAddressType.Id==WarehouseAddress.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Warehouse"
    }    
                                                  
    # ManyToOne side of Warehouse
    ItemWarehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                              info=dict(hidden=True,
                                        exceptSchemaFields=["Addresses",
                                                            "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                            "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                            "versions"],
                                        ))

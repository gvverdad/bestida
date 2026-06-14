from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...address.Addresses import Address


class SupplierStoreAddress(Address):
    __versioned__ = {}
    __tablename__ = "SupplierStoreAddresses"
    __table_args__ = dict(info=dict(label="Supplier Store Addresses",
                                    desc="Addresses",
                                    parentTables=[
                                        dict(column="ItemSupplierStore",
                                             table="SupplierStores")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Addresses.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SupplierAddressTypes.Id"),
                     nullable=False,
                     info=dict(label="Address Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("SupplierAddressType",
                        primaryjoin="SupplierAddressType.Id==SupplierStoreAddress.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "SupplierStore"
    }    
                                                  
    # ManyToOne side of SupplierStore
    ItemSupplierStore_Id = Column(Integer, ForeignKey("SupplierStores.Id"),
                                  info=dict(hidden=True,
                                            exceptSchemaFields=["Addresses",
                                                                "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                "versions"],
                                            ))

Index("SupplierStoreAddress_Index1", SupplierStoreAddress.ItemSupplierStore_Id,
      SupplierStoreAddress.Type_Id, unique=True)

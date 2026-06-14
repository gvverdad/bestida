from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...address.Addresses import Address


class SupplierAddress(Address):
    __versioned__ = {}
    __tablename__ = "SupplierAddresses"
    __table_args__ = dict(info=dict(label="Supplier Addresses",
                                    desc="Addresses",
                                    parentTables=[
                                        dict(column="ItemSupplier",
                                             table="Suppliers")
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
                        primaryjoin="SupplierAddressType.Id==SupplierAddress.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Supplier"
    }    
                                                  
    # ManyToOne side of Supplier
    ItemSupplier_Id = Column(Integer, ForeignKey("Suppliers.Id"),
                             info=dict(hidden=True,
                                       exceptSchemaFields=["Addresses",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       ))

Index("SupplierAddress_Index1", SupplierAddress.ItemSupplier_Id,
      SupplierAddress.Type_Id, unique=True)

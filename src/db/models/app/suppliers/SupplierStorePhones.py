from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...address.Phones import Phone


class SupplierStorePhone(Phone):
    __versioned__ = {}
    __tablename__ = "SupplierStorePhones"
    __table_args__ = dict(info=dict(label="Supplier Store Phones", desc="Phones"))
        
    Id = Column(Integer, ForeignKey("Phones.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SupplierPhoneTypes.Id"),
                     nullable=False,
                     info=dict(label="Phone Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("SupplierPhoneType",
                        primaryjoin="SupplierPhoneType.Id==SupplierStorePhone.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "SupplierStore"
    }        
                                              
    # ManyToOne side of SupplierStore
    ItemSupplierStore_Id = Column(Integer, ForeignKey("SupplierStores.Id"),
                                  info=dict(hidden=True,
                                            exceptSchemaFields=["Phones",
                                                                "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                "versions"],
                                            ))

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...address.Phones import Phone


class SupplierPhone(Phone):
    __versioned__ = {}
    __tablename__ = "SupplierPhones"
    __table_args__ = dict(info=dict(label="Supplier Phones", desc="Phones"))
        
    Id = Column(Integer, ForeignKey("Phones.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))
    
    # Many2One
    Type_Id = Column(Integer, ForeignKey("SupplierPhoneTypes.Id"),
                     nullable=False,
                     info=dict(label="Phone Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("SupplierPhoneType",
                        primaryjoin="SupplierPhoneType.Id==SupplierPhone.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Supplier"
    }        
                                              
    # ManyToOne side of Supplier 
    ItemSupplier_Id = Column(Integer, ForeignKey("Suppliers.Id"),
                             info=dict(hidden=True,
                                       exceptSchemaFields=["Phones",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       ))

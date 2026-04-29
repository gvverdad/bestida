from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...address.Emails import Email


class SupplierEmail(Email):
    __versioned__ = {}
    __tablename__ = "SupplierEmails"
    __table_args__ = dict(info=dict(label="Supplier Emails", desc="Emails"))
        
    Id = Column(Integer, ForeignKey("Emails.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))
    # Many2One
    Type_Id = Column(Integer, ForeignKey("SupplierEmailTypes.Id"),
                     nullable=False,
                     info=dict(label="Email Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("SupplierEmailType",
                        primaryjoin="SupplierEmailType.Id==SupplierEmail.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Supplier"
    }    

    # ManyToOne side of Supplier 
    ItemSupplier_Id = Column(Integer, ForeignKey("Suppliers.Id"),
                             info=dict(hidden=True,
                                       exceptSchemaFields=["Emails",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       ))

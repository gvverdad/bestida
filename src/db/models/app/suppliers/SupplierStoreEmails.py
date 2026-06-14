from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...address.Emails import Email


class SupplierStoreEmail(Email):
    __versioned__ = {}
    __tablename__ = "SupplierStoreEmails"
    __table_args__ = dict(info=dict(label="Supplier Store Emails",
                                    desc="Emails",
                                    parentTables=[
                                        dict(column="ItemSupplierStore",
                                             table="SupplierStores")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Emails.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SupplierEmailTypes.Id"),
                     nullable=False,
                     info=dict(label="Email Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("SupplierEmailType",
                        primaryjoin="SupplierEmailType.Id==SupplierStoreEmail.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "SupplierStore"
    }    

    # ManyToOne side of SupplierStore
    ItemSupplierStore_Id = Column(Integer, ForeignKey("SupplierStores.Id"),
                                  info=dict(hidden=True,
                                            exceptSchemaFields=["Emails",
                                                                "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                "versions"],
                                            ))

Index("SupplierStoreEmail_Index1", SupplierStoreEmail.ItemSupplierStore_Id,
      SupplierStoreEmail.Type_Id, unique=True)

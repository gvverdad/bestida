from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...address.Emails import Email


class CustomerStoreEmail(Email):
    __versioned__ = {}
    __tablename__ = "CustomerStoreEmails"
    __table_args__ = dict(info=dict(label="Customer Store Emails",
                                    desc="Emails",
                                    parentTables=[
                                        dict(column="ItemCustomerStore",
                                             table="CustomerStores")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Emails.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CustomerEmailTypes.Id"),
                     nullable=False,
                     info=dict(label="Email Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("CustomerEmailType",
                        primaryjoin="CustomerEmailType.Id==CustomerStoreEmail.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "CustomerStore"
    }    

    # ManyToOne side of CustomerStore
    ItemCustomerStore_Id = Column(Integer, ForeignKey("CustomerStores.Id"),
                                  info=dict(hidden=True,
                                            exceptSchemaFields=["Emails",
                                                                "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                "versions"],
                                            ))

Index("CustomerStoreEmail_Index1", CustomerStoreEmail.ItemCustomerStore_Id,
      CustomerStoreEmail.Type_Id, unique=True)

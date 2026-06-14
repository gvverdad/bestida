from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...address.Phones import Phone


class CustomerPhone(Phone):
    __versioned__ = {}
    __tablename__ = "CustomerPhones"
    __table_args__ = dict(info=dict(label="Customer Phones",
                                    desc="Phones",
                                    parentTables=[
                                        dict(column="ItemCustomer",
                                             table="Customers")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Phones.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CustomerPhoneTypes.Id"),
                     nullable=False,
                     info=dict(label="Phone Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("CustomerPhoneType",
                        primaryjoin="CustomerPhoneType.Id==CustomerPhone.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Customer"
    }        
                                              
    # ManyToOne side of Customer 
    ItemCustomer_Id = Column(Integer, ForeignKey("Customers.Id"),
                             info=dict(hidden=True,
                                       exceptSchemaFields=["Phones",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       ))

Index("CustomerPhone_Index1", CustomerPhone.ItemCustomer_Id,
      CustomerPhone.Type_Id, unique=True)

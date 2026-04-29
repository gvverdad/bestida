from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...address.Addresses import Address


class CustomerAddress(Address):
    __versioned__ = {}
    __tablename__ = "CustomerAddresses"
    __table_args__ = dict(info=dict(label="Customer Addresses", desc="Addresses"))
        
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
                        primaryjoin="CustomerAddressType.Id==CustomerAddress.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Customer"
    }    
                                                  
    # ManyToOne side of Customer
    ItemCustomer_Id = Column(Integer, ForeignKey("Customers.Id"),
                             info=dict(hidden=True,
                                       exceptSchemaFields=["Addresses",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       ))

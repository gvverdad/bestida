from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...address.Phones import Phone


class CustomerStorePhone(Phone):
    __versioned__ = {}
    __tablename__ = "CustomerStorePhones"
    __table_args__ = dict(info=dict(label="Customer Store Phones",
                                    desc="Phones",
                                    parentTables=[
                                        dict(column="ItemCustomerStore",
                                             table="CustomerStores")
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
                        primaryjoin="CustomerPhoneType.Id==CustomerStorePhone.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "CustomerStore"
    }        
                                              
    # ManyToOne side of CustomerStore
    ItemCustomerStore_Id = Column(Integer, ForeignKey("CustomerStores.Id"),
                                  info=dict(hidden=True,
                                            exceptSchemaFields=["Phones",
                                                                "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                "versions"],
                                            ))

Index("CustomerStorePhone_Index1", CustomerStorePhone.ItemCustomerStore_Id,
      CustomerStorePhone.Type_Id, unique=True)

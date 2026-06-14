from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from src.db.models.address.Addresses import Address


class SalesAccountAddress(Address):
    __versioned__ = {}
    __tablename__ = "SalesAccountAddresses"
    __table_args__ = dict(info=dict(label="SalesAccount Addresses",
                                    desc="Addresses",
                                    parentTables=[
                                        dict(column="ItemSalesAccount",
                                             table="SalesAccounts")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Addresses.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SalesAccountAddressTypes.Id"),
                     nullable=False,
                     info=dict(label="Address Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("SalesAccountAddressType",
                        primaryjoin="SalesAccountAddressType.Id==SalesAccountAddress.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "SalesAccount"
    }    
                                                  
    # ManyToOne side of SalesAccount
    ItemSalesAccount_Id = Column(Integer, ForeignKey("SalesAccounts.Id"),
                                 info=dict(hidden=True))

Index("SalesAccountAddress_Index1", SalesAccountAddress.ItemSalesAccount_Id,
      SalesAccountAddress.Type_Id, unique=True)

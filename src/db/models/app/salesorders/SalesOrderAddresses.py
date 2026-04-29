from sqlalchemy import Column, ForeignKey, Integer

from ...address.Addresses import Address


class SalesOrderAddress(Address):
    __versioned__ = {}
    __tablename__ = "SalesOrderAddresses"
    __table_args__ = dict(info=dict(label="Sales Order Addresses", desc="Addresses"))
        
    Id = Column(Integer, ForeignKey("Addresses.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "SalesOrder"
    }    
                                                  
    # ManyToOne side of SalesOrderHeader
    ItemSalesOrderHeader_Id = Column(Integer, ForeignKey("SalesOrderHeaders.Id"),
                                     info=dict(hidden=True,
                                               exceptSchemaFields=["Addresses",
                                                                   "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                   "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                   "versions"],
                                               ))

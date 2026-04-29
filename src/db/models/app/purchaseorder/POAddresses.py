from sqlalchemy import Column, ForeignKey, Integer

from ...address.Addresses import Address


class POAddress(Address):
    __versioned__ = {}
    __tablename__ = "POAddresses"
    __table_args__ = dict(info=dict(label="PO Addresses", desc="Addresses"))
        
    Id = Column(Integer, ForeignKey("Addresses.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "PO"
    }    
                                                  
    # ManyToOne side of POHeader
    ItemPOHeader_Id = Column(Integer, ForeignKey("POHeaders.Id"),
                             info=dict(hidden=True,
                                       exceptSchemaFields=["Addresses",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       ))

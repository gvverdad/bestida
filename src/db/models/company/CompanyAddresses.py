from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ..address.Addresses import Address


class CompanyAddress(Address):
    __versioned__ = {}
    __tablename__ = "CompanyAddresses"
    __table_args__ = dict(info=dict(label="Company Addresses",
                                    desc="Addresses",
                                    parentTables=[
                                        dict(column="ItemCompany",
                                             table="Companies")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Addresses.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))
    
    # Many2One
    Type_Id = Column(Integer, ForeignKey("CompanyAddressTypes.Id"),
                     nullable=False,
                     info=dict(label="Address Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("CompanyAddressType",
                        primaryjoin="CompanyAddressType.Id==CompanyAddress.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Company"
    }    
                                                  
    # ManyToOne side of Company 
    ItemCompany_Id = Column(Integer, ForeignKey("Companies.Id"),
                            info=dict(hidden=True))

Index("CompanyAddress_Index1", CompanyAddress.ItemCompany_Id,
      CompanyAddress.Type_Id, unique=True)

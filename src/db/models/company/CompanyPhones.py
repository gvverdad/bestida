from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ..address.Phones import Phone


class CompanyPhone(Phone):
    __versioned__ = {}
    __tablename__ = "CompanyPhones"
    __table_args__ = dict(info=dict(label="Company Phones",
                                    desc="Phones",
                                    parentTables=[
                                        dict(column="ItemCompany",
                                             table="Companies")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Phones.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))
    
    # Many2One
    Type_Id = Column(Integer, ForeignKey("CompanyPhoneTypes.Id"),
                     nullable=False,
                     info=dict(label="Phone Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("CompanyPhoneType",
                        primaryjoin="CompanyPhoneType.Id==CompanyPhone.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Company"
    }        
                                              
    # ManyToOne side of Company 
    ItemCompany_Id = Column(Integer, ForeignKey("Companies.Id"),
                            info=dict(hidden=True))

Index("CompanyPhone_Index1", CompanyPhone.ItemCompany_Id,
      CompanyPhone.Type_Id, unique=True)

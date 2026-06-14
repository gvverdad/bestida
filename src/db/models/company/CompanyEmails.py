from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ..address.Emails import Email


class CompanyEmail(Email):
    __versioned__ = {}
    __tablename__ = "CompanyEmails"
    __table_args__ = dict(info=dict(label="Company Emails",
                                    desc="Emails",
                                    parentTables=[
                                        dict(column="ItemCompany",
                                             table="Companies")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Emails.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CompanyEmailTypes.Id"),
                     nullable=False,
                     info=dict(label="Email Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("CompanyEmailType",
                        primaryjoin="CompanyEmailType.Id==CompanyEmail.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Company"
    }    

    # ManyToOne side of Company 
    ItemCompany_Id = Column(Integer, ForeignKey("Companies.Id"),
                            info=dict(hidden=True))

Index("CompanyEmail_Index1", CompanyEmail.ItemCompany_Id,
      CompanyEmail.Type_Id, unique=True)

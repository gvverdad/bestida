from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from src.db.models.address.Emails import Email


class SalesAccountEmail(Email):
    __versioned__ = {}
    __tablename__ = "SalesAccountEmails"
    __table_args__ = dict(info=dict(label="SalesAccount Emails",
                                    desc="Emails",
                                    parentTables=[
                                        dict(column="ItemSalesAccount",
                                             table="SalesAccounts")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Emails.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SalesAccountEmailTypes.Id"),
                     nullable=False,
                     info=dict(label="Email Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("SalesAccountEmailType",
                        primaryjoin="SalesAccountEmailType.Id==SalesAccountEmail.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "SalesAccount"
    }    

    # ManyToOne side of SalesAccount 
    ItemSalesAccount_Id = Column(Integer, ForeignKey("SalesAccounts.Id"),
                                 info=dict(hidden=True))

Index("SalesAccountEmail_Index1", SalesAccountEmail.ItemSalesAccount_Id,
      SalesAccountEmail.Type_Id, unique=True)

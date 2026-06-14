from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from src.db.models.address.Phones import Phone


class SalesAccountPhone(Phone):
    __versioned__ = {}
    __tablename__ = "SalesAccountPhones"
    __table_args__ = dict(info=dict(label="SalesAccount Phones",
                                    desc="Phones",
                                    parentTables=[
                                        dict(column="ItemSalesAccount",
                                             table="SalesAccounts")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Phones.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SalesAccountPhoneTypes.Id"),
                     nullable=False,
                     info=dict(label="Phone Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("SalesAccountPhoneType",
                        primaryjoin="SalesAccountPhoneType.Id==SalesAccountPhone.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "SalesAccount"
    }        
                                              
    # ManyToOne side of SalesAccount 
    ItemSalesAccount_Id = Column(Integer, ForeignKey("SalesAccounts.Id"),
                                 info=dict(hidden=True))

Index("SalesAccountPhone_Index1", SalesAccountPhone.ItemSalesAccount_Id,
      SalesAccountPhone.Type_Id, unique=True)

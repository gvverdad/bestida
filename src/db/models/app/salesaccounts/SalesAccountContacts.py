from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from src.db.models.person.Persons import Person


class SalesAccountContact(Person):
    __versioned__ = {}
    __tablename__ = "SalesAccountContacts"
    __table_args__ = dict(info=dict(label="SalesAccount Contacts",
                                    desc="Contacts",
                                    stepperTitleFields=["Type.Type", "LastName"],
                                    parentTables=[
                                        dict(column="ItemSalesAccount",
                                             table="SalesAccounts")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Persons.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("SalesAccountContactTypes.Id"),
                     nullable=False,
                     info=dict(label="Contact Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("SalesAccountContactType",
                        primaryjoin="SalesAccountContactType.Id==SalesAccountContact.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "SalesAccountContact"
    }    

    # ManyToOne side of SalesAccount
    ItemSalesAccount_Id = Column(Integer, ForeignKey("SalesAccounts.Id"),
                                 info=dict(hidden=True))

Index("SalesAccountContact_Index1", SalesAccountContact.ItemSalesAccount_Id,
      SalesAccountContact.Type_Id, unique=True)

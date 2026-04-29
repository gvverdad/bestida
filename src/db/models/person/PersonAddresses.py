from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..address.Addresses import Address


class PersonAddress(Address):
    __versioned__ = {}
    __tablename__ = "PersonAddresses"
    __table_args__ = dict(info=dict(label="Person Addresses", desc="Addresses"))
        
    Id = Column(Integer, ForeignKey("Addresses.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("PersonAddressTypes.Id"),
                     nullable=False,
                     info=dict(label="Address Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("PersonAddressType",
                        primaryjoin="PersonAddressType.Id==PersonAddress.Type_Id")

    __mapper_args__ = {"polymorphic_identity": "Person"}
                                                  
    # ManyToOne side of Person 
    ItemPerson_Id = Column(Integer, ForeignKey("Persons.Id"),
                           info=dict(hidden=True))

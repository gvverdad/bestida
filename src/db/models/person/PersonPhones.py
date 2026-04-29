from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..address.Phones import Phone


class PersonPhone(Phone):
    __versioned__ = {}
    __tablename__ = "PersonPhones"
    __table_args__ = dict(info=dict(label="Person Phones", desc="Phones"))
        
    Id = Column(Integer, ForeignKey("Phones.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("PersonPhoneTypes.Id"),
                     nullable=False,
                     info=dict(label="Phone Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("PersonPhoneType",
                        primaryjoin="PersonPhoneType.Id==PersonPhone.Type_Id")

    __mapper_args__ = {"polymorphic_identity": "Person"}
                                              
    # ManyToOne side of Person 
    ItemPerson_Id = Column(Integer, ForeignKey("Persons.Id"),
                           info=dict(hidden=True))

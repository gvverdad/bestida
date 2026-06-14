from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ..address.Emails import Email


class PersonEmail(Email):
    __versioned__ = {}
    __tablename__ = "PersonEmails"
    __table_args__ = dict(info=dict(label="Person Emails",
                                    desc="Emails",
                                    parentTables=[
                                        dict(column="ItemPerson",
                                             table="Persons")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Emails.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))
    
    # Many2One
    Type_Id = Column(Integer, ForeignKey("PersonEmailTypes.Id"),
                     nullable=False,
                     info=dict(label="Email Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("PersonEmailType",
                        primaryjoin="PersonEmailType.Id==PersonEmail.Type_Id")

    __mapper_args__ = {"polymorphic_identity": "Person"}

    # ManyToOne side of Person 
    ItemPerson_Id = Column(Integer, ForeignKey("Persons.Id"),
                           info=dict(hidden=True))

Index("PersonEmail_Index1", PersonEmail.ItemPerson_Id,
      PersonEmail.Type_Id, unique=True)

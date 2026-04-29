from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..person.Persons import Person


class UserPerson(Person):
    __versioned__ = {}
    __tablename__ = "UserPersons"
    __table_args__ = dict(info=dict(label="Personal", desc="Personal"))
        
    Id = Column(Integer, ForeignKey("Persons.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "User"
    }    
            
    # OneToOne side of User 
    ItemUser_Id = Column(Integer, ForeignKey("Users.Id"),
                         info=dict(hidden=True))
    ItemUser = relationship("User", back_populates="Personal",
                            primaryjoin="User.Id==UserPerson.ItemUser_Id")

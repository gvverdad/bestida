from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class Email(Model):
    __versioned__ = {}
    __tablename__ = "Emails"
    __table_args__ = dict(info=dict(label="Email"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    Email = Column(String(128), nullable=False,
                   info=dict(label="Email", validator=["Email"]))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"),  nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Email.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Email.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))
    
    TypeOfEmail = Column(String(32),
                         info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "Base",
        "polymorphic_on": TypeOfEmail
    }

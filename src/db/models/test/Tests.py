from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, String)
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class Test(Model):
    __tablename__ = "Tests"
    __table_args__ = dict(info=dict(label="Tests",
                                    stepperTitleFields=["Level", "Name"],
                                    key="Level"
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    Level = Column(String(8), nullable=False, index=True, unique=True,
                       info=dict(label="Level", case="uppercase",
                                 selectId="Id",
                                 selectKey="Name"
                                 ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))


    # One2Many
    Level1s = relationship("Test1", uselist=True,
                         backref="ItemLevel",
                         cascade="all, delete-orphan")

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Test.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Test.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

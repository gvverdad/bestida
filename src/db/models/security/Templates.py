from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class Template(Model):
    __versioned__ = {}
    __tablename__ = "Templates"
    __table_args__ = dict(info=dict(label="Templates", stepperTitleFields=[], key="File"))

    Id = Column(Integer, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    File = Column(String(512), index=True, unique=True, nullable=False,
                  info=dict(label="File"))
    Checksum = Column(String(128), nullable=False, info=dict(label="Checksum"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Template.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))

    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Template.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

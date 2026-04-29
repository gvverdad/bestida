from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Text, Integer, DateTime)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class POSizeComment(Model):
    __versioned__ = {}
    __tablename__ = "POSizeComments"
    __table_args__ = dict(info=dict(label="PO Size Comments"))

    Id = Column(Integer, autoincrement=True, primary_key=True,
                nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("POSizeCommentTypes.Id"),
                     nullable=False,
                     info=dict(label="Type", selectId="Id",
                               selectKey="Description", depth=1))
    Type = relationship("POSizeCommentType",
                        primaryjoin="POSizeCommentType.Id==POSizeComment.Type_Id")

    Comments = Column(Text, info=dict(label="Comments"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User",
                              primaryjoin="User.Id==POSizeComment.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User",
                                primaryjoin="User.Id==POSizeComment.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # Many2One side of POSize
    ItemPOSize_Id = Column(Integer, ForeignKey("POSizes.Id"),
                           info=dict(hidden=True))

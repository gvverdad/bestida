from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Text, Integer, DateTime)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class PODetailComment(Model):
    __versioned__ = {}
    __tablename__ = "PODetailComments"
    __table_args__ = dict(info=dict(label="PO Detail Comments"))

    Id = Column(Integer, autoincrement=True, primary_key=True,
                nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("PODetailCommentTypes.Id"),
                     nullable=False,
                     info=dict(label="Type", selectId="Id",
                               selectKey="Description", depth=1))
    Type = relationship("PODetailCommentType",
                        primaryjoin="PODetailCommentType.Id==PODetailComment.Type_Id")

    Comments = Column(Text, info=dict(label="Comments"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User",
                              primaryjoin="User.Id==PODetailComment.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User",
                                primaryjoin="User.Id==PODetailComment.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # Many2One side of PODetail
    ItemPODetail_Id = Column(Integer, ForeignKey("PODetails.Id"),
                             info=dict(hidden=True))

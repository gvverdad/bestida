from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Text, Integer, String, DateTime)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class ProductDescription(Model):
    __versioned__ = {}
    __tablename__ = "ProductDescriptions"
    __table_args__ = dict(info=dict(label="Product Descriptions",
                                    desc="Descriptions"))

    Id = Column(Integer, autoincrement=True, primary_key=True,
                nullable=False,
                info=dict(label="Product Description Id", modifiable=False))

    # Many2One
    DescriptionType_Id = Column(Integer, ForeignKey("ProductDescriptionTypes.Id"),
                                nullable=False,
                                info=dict(label="Type", selectId="Id",
                                          selectKey="Description", depth=1))
    DescriptionType = relationship("ProductDescriptionType",
                                   primaryjoin="ProductDescriptionType.Id==ProductDescription.DescriptionType_Id")

    Description = Column(Text, info=dict(label="Description"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==ProductDescription.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==ProductDescription.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    TypeOfDescription = Column(String(32),
                               info=dict(label="Record Type", modifiable=False))

    __mapper_args__ = {
        "polymorphic_identity": "Base",
        "polymorphic_on": TypeOfDescription
    }

from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Date, String,
                        Index, Enum, event, func, select, inspect)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .... import sqa
from .....security.policy import get_current_uid


class POEventDetail(Model):
    __versioned__ = {}
    __tablename__ = "POEventDetails"
    __table_args__ = dict(info=dict(label="PO Event Lines", desc="Lines",
                                    stepperTitleFields=[],
                                    keyPaths=["ItemPOEventHeader_Id"],
                                    key="Line",
                                    parentTables=[
                                        dict(column="ItemPOEventHeader",
                                             table="POEventHeaders")
                                    ])
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One side of POEventHeader
    ItemPOEventHeader_Id = Column(Integer, ForeignKey("POEventHeaders.Id"),
                                  info=dict(label="Format",
                                            selectId="Id",
                                            selectKey="Format",
                                            selectFormat=["Format", "Description"],
                                            exceptSchemaFields=["Company_Id", "Company", "Details",
                                                                "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                "versions"],
                                            depth=1))

    Stage = Column(Integer, nullable=False,
                   info=dict(label="Stage",
                             numberType="string"  # number, currency, percent, string
                             ))

    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    MinDays = Column(Integer, default=0,
                     info=dict(label="Minimum Days to Next Stage",
                               validator=["ZeroPositive"]))

    MaxDays = Column(Integer, default=0,
                     info=dict(label="Maximum Days to Next Stage",
                               validator=["ZeroPositive"]))

    # Many2One
    Location_Id = Column(Integer, ForeignKey("POEventLocations.Id"),
                         nullable=False, info=dict(label="Location", selectId="Id",
                                                   selectKey="Location",
                                                   selectFormat=["Location", "Description"],
                                                   depth=1))
    Location = relationship("POEventLocation",
                            primaryjoin="POEventLocation.Id==POEventDetail.Location_Id")

    StageType = Column(Enum("Materials Required", "Shipping",
                            "Receiving",
                            name="StageType"),
                       nullable=False, default="Materials Required",
                       info=dict(label="Stage Type")
                       )

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==POEventDetail.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==POEventDetail.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("POEventDetail_Index1", POEventDetail.ItemPOEventHeader_Id,
      POEventDetail.Stage, unique=True)

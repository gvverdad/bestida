from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Index)
from sqlalchemy.types import String
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class Test2(Model):
    __tablename__ = "Test2s"
    __table_args__ = dict(info=dict(label="Test2s",
                                    keyPaths=["ItemLevel1_Id"],
                                    key="Level2",
                                    parentTables=[
                                        dict(column="ItemLevel1",
                                             table="Test1s")
                                    ]
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One side of WarehouseArea
    ItemLevel1_Id = Column(Integer, ForeignKey("Test1s.Id"),
                                  info=dict(label="Level/Level1",
                                            selectId="Id",
                                            selectKey="level_level1",
                                            selectFormat=["level_level1"],
                                            exceptSchemaFields=["Level2s",
                                                                "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId"],
                                            depth=1))

    Level2 = Column(String(8), nullable=False,
                  info=dict(label="Level2", case="uppercase"
                            ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Test2.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Test2.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("Test2_Index1", Test2.ItemLevel1_Id,
      Test2.Level2, unique=True)

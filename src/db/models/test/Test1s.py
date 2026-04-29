from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Index,
                        String, select)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ..model import Model
from ....security.policy import get_current_uid


class Test1(Model):
    __tablename__ = "Test1s"
    __table_args__ = dict(info=dict(label="Test1s",
                                    key="Level1",
                                    parentTables=[
                                        dict(column="ItemLevel",
                                             table="Tests")
                                    ],
                                    hybrids=[
                                             dict(name="level_level1",
                                                  label="Level/Level1",
                                                  type="String",
                                                  length=17,
                                                  decimals=0,
                                                  sortable=True,
                                                  searchable=True)
                                             ]
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One side of Warehouse
    ItemLevel_Id = Column(Integer, ForeignKey("Tests.Id"),
                              info=dict(label="Level",
                                        selectId="Id", selectKey="Name",
                                        exceptSchemaFields=["Level1s",
                                                            "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                            "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId"],
                                        depth=1))

    Level1 = Column(String(8), nullable=False,
                  info=dict(label="Level1", case="uppercase",
                            selectId="Id",
                            selectKey="Name"
                            ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))

    # One2Many
    Level2s = relationship("Test2", uselist=True,
                             backref="ItemLevel1",
                             cascade="all, delete-orphan",
                             info=dict(label="Level3s", depth=1))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Test1.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Test1.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    @hybrid_property
    def level_level1(self):
        return self.ItemLevel.Level + " " + self.Level1

    @level_level1.expression
    def level_level1(cls):
        from .Tests import Test

        return (select([Test.Level + " " + Test1.Level1]).
                where(Test.Id == cls.ItemLevel_Id).
                as_scalar())


Index("Test1_Index1", Test1.ItemLevel_Id, Test1.Level1, unique=True)

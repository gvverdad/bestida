from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Text, String,
                        Index, Boolean)
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class ProgramState(Model):
    __tablename__ = "ProgramStates"
    __table_args__ = dict(info=dict(label="Program States",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id", "Program_Id",
                                              "Param1", "Param2", "Param3",
                                              "Param4", "Param5",
                                              "Role_Id"],
                                    key="User_Id"))
    
    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company",
                           primaryjoin="Company.Id==ProgramState.Company_Id")

    # Many2One    
    Program_Id = Column(Integer, ForeignKey("Programs.Id"), nullable=False,
                        info=dict(label="Program", selectId="Id",
                                  selectKey="Name"))
    Program = relationship("Program",
                           primaryjoin="Program.Id==ProgramState.Program_Id")

    Param1 = Column(String(32), nullable=True, info=dict(label="Program Parameter 1"))
    Param2 = Column(String(32), nullable=True, info=dict(label="Program Parameter 2"))
    Param3 = Column(String(32), nullable=True, info=dict(label="Program Parameter 3"))
    Param4 = Column(String(32), nullable=True, info=dict(label="Program Parameter 4"))
    Param5 = Column(String(32), nullable=True, info=dict(label="Program Parameter 5"))

    # Many2One
    Role_Id = Column(Integer, ForeignKey("Roles.Id"),
                     info=dict(label="Role", selectId="Id", selectKey="Role"))
    Role = relationship("Role", primaryjoin="Role.Id==ProgramState.Role_Id")

    # Many2One
    User_Id = Column(Integer, ForeignKey("Users.Id"),
                     default=get_current_uid,
                     info=dict(label="User", selectId="Id", selectKey="UserId"))
    User = relationship("User", primaryjoin="User.Id==ProgramState.User_Id")
    
    Depth = Column(Integer, default=1, info=dict(label="Depth"))
    CurrentPage = Column(Integer, default=0, info=dict(label="Current Page"))
    PageSize = Column(Integer, default=10, info=dict(label="Page Size"))
    AutoRefresh = Column(Boolean, default=False, info=dict(label="Auto Refresh"))
    RefreshInterval = Column(Integer, default=60, info=dict(label="Refresh Interval in Seconds"))

    State = Column(Text, info=dict(label="State"))
        
    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==ProgramState.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==ProgramState.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # Param1..Param5,Role_Id,User_Id are nullable - enforce uniqueness - see db.models.unique
    __nullable_unique_fields__ = ["Company_Id", "Program_Id",
                                  "Param1", "Param2", "Param3", "Param4", "Param5",
                                  "Role_Id", "User_Id"]


Index("ProgramState_Index1", ProgramState.Company_Id, ProgramState.Program_Id,
      ProgramState.Param1, ProgramState.Param2, ProgramState.Param3,
      ProgramState.Param4, ProgramState.Param5,
      ProgramState.Role_Id, ProgramState.User_Id,
      unique=True)

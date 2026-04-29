from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Text, Index, String
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class Ruleset(Model):
    __versioned__ = {}
    __tablename__ = "Rulesets"
    __table_args__ = dict(info=dict(label="Rulesets", companyField="Company_Id"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company",
                                  selectId="Id", selectKey="Name",
                                  selectGetter="/getCompaniesList"))
    Company = relationship("Company",
                           primaryjoin="Company.Id==Ruleset.Company_Id")

    # Many2One    
    Program_Id = Column(Integer, ForeignKey("Programs.Id"), nullable=False,
                        info=dict(label="Program", selectId="Id", selectKey="Name"))
    Program = relationship("Program",
                           primaryjoin="Program.Id==Ruleset.Program_Id")

    # Many2One
    Role_Id = Column(Integer, ForeignKey("Roles.Id"), nullable=False,
                     info=dict(label="Role", selectId="Id", selectKey="Role"))
    Role = relationship("Role", primaryjoin="Role.Id==Ruleset.Role_Id")

    # Many2One
    User_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                     info=dict(label="User", selectId="Id", selectKey="UserId"))
    User = relationship("User", primaryjoin="User.Id==Ruleset.User_Id")

    Title = Column(String(128), nullable=False, info=dict(label="Title"))

    Params = Column(Text, info=dict(label="Params", textType="Dict"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Ruleset.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))

    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Ruleset.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("Ruleset_Index1", Ruleset.Company_Id, Ruleset.Program_Id,
      Ruleset.Role_Id, Ruleset.User_Id, unique=False)
Index("Ruleset_Index2", Ruleset.Company_Id, Ruleset.Program_Id,
      Ruleset.User_Id, unique=False)

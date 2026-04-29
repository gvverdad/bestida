from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Boolean, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class Role(Model):
    __versioned__ = {}
    __tablename__ = "Roles"
    __table_args__ = dict(info=dict(label="Security Roles",
                                    stepperTitleFields=[],
                                    keyPaths=["Group_Id"],
                                    key="Role"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Group_Id = Column(Integer, ForeignKey("Groups.Id"), nullable=False,
                      info=dict(label="Group", depth=1, selectId="Id",
                                selectKey="Group"))
    Group = relationship("Group", primaryjoin="Group.Id==Role.Group_Id")

    Role = Column(String(32), nullable=False, info=dict(label="Role",
                                                        case="uppercase",
                                                        selectId="Id",
                                                        selectKey="Role",
                                                        selectColumn="Role",
                                                        selectFormat=["Role", "Group.Group", "Description"],
                                                        selectTable="Roles"
                                                        ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    IsAdmin = Column(Boolean, default=False, info=dict(label="Admin"))

    # Many2One
    StartMenu_Id = Column(Integer, ForeignKey("Menus.Id"), nullable=False,
                          info=dict(label="Starting Menu",
                                    depth=1,
                                    selectId="Id", selectKey="Name"))
    StartMenu = relationship("Menu", primaryjoin="Menu.Id==Role.StartMenu_Id")

    RunLevel = Column(Integer, default=999,
                      info=dict(label="Run Level", min="0", max="99999"))
    CreateLevel = Column(Integer, default=999,
                         info=dict(label="Create Level", min="0", max="99999"))
    UpdateLevel = Column(Integer, default=999,
                         info=dict(label="Update Level", min="0", max="99999"))
    DeleteLevel = Column(Integer, default=999,
                         info=dict(label="Delete Level", min="0", max="99999"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Role.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))

    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Role.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of User
    # uselist=False - this is just used in validate_delete
    Users = relationship("User", uselist=False, back_populates="Role",
                         primaryjoin="User.Role_Id==Role.Id",
                         info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Users is not None:
            is_ok = False
            tables = "Users"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Role"

        return is_ok, message


Index("Role_Index1", Role.Group_Id, Role.Role, unique=True)
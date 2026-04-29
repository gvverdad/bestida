from datetime import datetime

from sqlalchemy import Table, Column, ForeignKey, String, Boolean, Integer, DateTime
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid

company_group_table = Table("company_group", Model.metadata,
                            Column("company_id", Integer, ForeignKey("Companies.Id")),
                            Column("group_id", Integer, ForeignKey("Groups.Id"))
                            )
company_group_table.__versioned__ = {}  # Mark secondary table for versioning

class Group(Model):
    __versioned__ = {}
    __tablename__ = "Groups"
    __table_args__ = dict(info=dict(label="Security Groups",
                                    stepperTitleFields=[],
                                    key="Group"))
    
    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    Group = Column(String(32), index=True, unique=True, nullable=False,
                   info=dict(label="Group", case="uppercase",
                             selectId="Id",
                             selectKey="Group",
                             selectColumn="Group",
                             selectFormat=["Group", "Description"],
                             selectTable="Groups"
                             ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    IsAdmin = Column(Boolean, default=False, info=dict(label="Admin"))

    # Many2Many
    Companies = relationship("Company", secondary=company_group_table,
                             back_populates="Groups",
                             info=dict(label="Valid Companies",
                                       selectId="Id", selectKey="Name",
                                       selectGetter="/getAllCompaniesList",
                                       depth=1))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Group.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Group.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Role
    # uselist=False - this is just used in validate_delete
    Roles = relationship("Role", uselist=False, back_populates="Group",
                         primaryjoin="Role.Group_Id==Group.Id",
                         info=dict(hidden=True, dump=False))

    def validate_update(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        # TODO: check that changes to Companies will not affect Users Company

        return is_ok, message

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Roles is not None:
            is_ok = False
            tables = "Roles"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Group"

        return is_ok, message

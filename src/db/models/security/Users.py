# coding=utf-8
from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlalchemy import event, inspect
from sqlalchemy import (Column, ForeignKey, String, Boolean,
                        Integer, DateTime, Date, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ..model import Model
from ....security.policy import get_current_uid
from ....utils.crypt import CryptField
from ..functions import get_default_user_expiry, get_default_password_expiry


def expiry_date():
    return datetime.utcnow() + relativedelta(days=get_default_user_expiry())


class User(Model):
    __versioned__ = {}
    __tablename__ = "Users"
    # TODO: investigate why cannot sort/search password_expiry_date
    __table_args__ = dict(info=dict(label="Users",
                                    key="UserId",
                                    hybrids=[
                                        dict(name="password_expiry_date",
                                             label="Password Expiry Date",
                                             type="Date",
                                             sortable=False,
                                             searchable=False)
                                    ]))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    UserId = Column(String(64), index=True, unique=True, nullable=False,
                    info=dict(label="User Id",
                              selectId="Id",
                              selectKey="UserId",
                              selectColumn="UserId",
                              selectFormat=["UserId", "Personal.FirstName", "Personal.LastName", "Role.Group.Group", "Role.Role"],
                              selectGetter="/usersdata",
                              selectTable="Users"
                              ))
    Password = Column(Text, nullable=False,
                      info=dict(label="Password", displayable=False))
    
    PasswordExpiryDays = Column(Integer, default=get_default_password_expiry,
                                nullable=False,
                                info=dict(label="Password Expiry Days",
                                          validator=["ZeroPositive"]))
    LastPasswordModifiedDate = Column(DateTime, default=datetime.utcnow,
                                      info=dict(label="Password Last Modified Date",
                                                modifiable=False))

    Inactive = Column(Boolean, default=False, info=dict(label="Inactive"))
    InactiveOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             info=dict(label="Inactive By", modifiable=False))
    InactiveOpId = relationship("User", remote_side="User.Id",
                                primaryjoin="User.Id==User.InactiveOpId_Id",
                                info=dict(modifiable=False))
    InactiveTimeStamp = Column(DateTime, default=None,
                               info=dict(label="Inactive Timestamp",
                                         modifiable=False))

    ExpiryDate = Column(Date(), nullable=False, default=expiry_date,
                        info=dict(label="Expiry Date"))

    # Many2One
    # on initial load - remove nullable=False
    # restore after initial load
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", selectId="Id",
                                  selectKey="Name",
                                  selectGetter="/getCompaniesList"
                        ))
    Company = relationship("Company", primaryjoin="Company.Id==User.Company_Id")

    # Many2One
    # on initial load - remove nullable=False
    # restore after initial load
    Role_Id = Column(Integer, ForeignKey("Roles.Id"), nullable=False,
                     info=dict(label="Role", selectId="Id", selectKey="Role",
                               selectFormat=["Group.Group", "Role"]))
    Role = relationship("Role", primaryjoin="Role.Id==User.Role_Id")

    AutoReadNotifications = Column(Boolean, default=False, info=dict(label="Auto-Read Notifications"))

    # One2One side of UserPerson    
    Personal = relationship("UserPerson", uselist=False,
                            back_populates="ItemUser",
                            primaryjoin="UserPerson.ItemUser_Id==User.Id",
                            cascade="all, delete-orphan",
                            info=dict(label="Personal",
                                      dumpFields=["Id"]))

    # One2One side of UserSettings
    Settings = relationship("UserSetting", uselist=False,
                            back_populates="ItemUser",
                            primaryjoin="UserSetting.ItemUser_Id==User.Id",
                            cascade="all, delete-orphan",
                            info=dict(label="Settings",
                                      dumpFields=["Id"]))

    # adjacency list - self referential
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", remote_side="User.Id",
                              primaryjoin="User.Id==User.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created By Timestamp",
                                       modifiable=False))
    # adjacency list - self referential    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", remote_side="User.Id",
                                primaryjoin="User.Id==User.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified By Timestamp",
                                         modifiable=False))

    # One2Many side of Spooler
    # uselist=False - this is just used in validate_delete
    Spoolers = relationship("Spooler", uselist=False, back_populates="User",
                            primaryjoin="User.Id==Spooler.User_Id",
                            info=dict(hidden=True, dump=False))

    # One2Many side of Task
    # uselist=False - this is just used in validate_delete
    Tasks = relationship("Task", uselist=False, back_populates="User",
                         primaryjoin="User.Id==Task.User_Id",
                         info=dict(hidden=True, dump=False))

    # calculated columns
    @hybrid_property
    def password_expiry_date(self):
        return (self.LastPasswordModifiedDate +
                relativedelta(days=self.PasswordExpiryDays))

    @password_expiry_date.expression
    def password_expiry_date(cls):
        return (cls.LastPasswordModifiedDate +
                relativedelta(days=cls.PasswordExpiryDays))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""
        if user_rowid == self.Id:
            is_ok = False
            message = "Cannot Delete Self"
            return is_ok, message

        if self.Spoolers is not None:
            is_ok = False
            tables = "Spoolers"
        if self.Tasks is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Tasks"
        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this User"
        return is_ok, message

    def get_id(self):
        return self.Id


def on_user_insert(mapper, connection, target):
    password = getattr(target, "Password")
    if password is None or password == "":
        setattr(target, "Password", getattr(target, "UserId"))
        setattr(target, "PasswordExpiryDays", 0)

    inactive = getattr(target, "Inactive")
    if inactive and getattr(target, "InactiveTimeStamp") is None:
        setattr(target, "InactiveTimeStamp", datetime.utcnow())
        setattr(target, "InactiveOpId_Id", get_current_uid())
    elif not inactive and getattr(target, "InactiveTimeStamp") is not None:
        setattr(target, "InactiveTimeStamp", None)
        setattr(target, "InactiveOpId_Id", None)


def on_user_update(mapper, connection, target):
    # check if Password has been modified
    pass_hist = inspect(target).attrs.Password.history
    # new record  History(added=['123'], unchanged=(), deleted=())
    # no status change History(added=(), unchanged=['123'], deleted=())
    # status change History(added=['456'], unchanged=(), deleted=['123'])
    if isinstance(pass_hist.deleted, list):
        setattr(target, "LastPasswordModifiedDate", datetime.utcnow())
        # TODO: dont hardcode 365 days
        setattr(target, "PasswordExpiryDays", 365)
    else:
        pass_days_hist = inspect(target).attrs.PasswordExpiryDays.history
        # check if PasswordExpiryDays has been modified to zero days
        if (isinstance(pass_days_hist.deleted, list) and
                getattr(target, "PasswordExpiryDays") == 0):
            # reset password
            setattr(target, "Password", getattr(target, "UserId"))
            setattr(target, "LastPasswordModifiedDate", datetime.utcnow())

    inactive = getattr(target, "Inactive")
    if inactive and getattr(target, "InactiveTimeStamp") is None:
        setattr(target, "InactiveTimeStamp", datetime.utcnow())
        setattr(target, "InactiveOpId_Id", get_current_uid())
    elif not inactive and getattr(target, "InactiveTimeStamp") is not None:
        setattr(target, "InactiveTimeStamp", None)
        setattr(target, "InactiveOpId_Id", None)


event.listen(User, "before_update", on_user_update)  # Mapper Event
event.listen(User, "before_insert", on_user_insert)  # mapper Event

event.listen(User, "load", CryptField("Password").load_decrypt)  # Instance Event
event.listen(User, "refresh", CryptField("Password").refresh_decrypt)  # Instance Event
event.listen(User, "before_update", CryptField("Password").encrypt)  # Mapper Event
event.listen(User, "before_insert", CryptField("Password").encrypt)  # mapper Event

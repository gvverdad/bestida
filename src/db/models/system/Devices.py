from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Enum, Text
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class Device(Model):
    __versioned__ = {}
    __tablename__ = "Devices"
    __table_args__ = dict(info=dict(label="Devices", key="Device"))

    Id = Column(Integer, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    Device = Column(String(32), index=True, unique=True, nullable=False,
                    info=dict(label="Device", case="uppercase",
                              selectId="Id",
                              selectKey="Device",
                              selectColumn="Device",
                              selectFormat=["Device", "Description"],
                              selectTable="Devices"
                              ))
    Description = Column(String(128), nullable=True, info=dict(label="Description"))

    Type = Column(Enum("spooler", "dashboard", "printer", name="DeviceTypes"),
                  nullable=False, default="spooler", info=dict(label="Type"))

    Script = Column(Text, info=dict(label="Script"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Device.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))

    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Device.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Task
    # uselist=False - this is just used in validate_delete
    Tasks = relationship("Task", uselist=False, back_populates="Device",
                         info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Tasks is not None:
            is_ok = False
            tables = "Tasks"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Device"

        return is_ok, message

from datetime import datetime

from sqlalchemy import event
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Text, Boolean, Index
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class Notification(Model):
    __tablename__ = "Notifications"
    __table_args__ = dict(info=dict(label="Notifications"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    User_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                     default=get_current_uid,
                     info=dict(label="User",  selectId="Id", selectKey="UserId"))
    User = relationship("User", primaryjoin="User.Id==Notification.User_Id")

    Title = Column(String(128), nullable=False, info=dict(label="Title"))

    Text = Column(Text, info=dict(label="Text"))

    Read = Column(Boolean, default=False, info=dict(label="Read"))
    ReadTimeStamp = Column(DateTime, default=None,
                           info=dict(label="Read Timestamp", modifiable=False))

    SpoolTitle = Column(String(128), default=None, info=dict(label="Spool Title"))
    SpoolFile = Column(String(4096), default=None, info=dict(label="Spool File"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Notification.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))

    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Notification.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("Notification_Index1", Notification.User_Id, unique=False)

def on_notification_insert(mapper, connection, target):
    from ..security.Users import User

    read = False
    uid = get_current_uid()
    user = connection.execute(
        User.__table__.select().
        where(User.Id == uid)
    ).first()
    if user and user.AutoReadNotifications:
        read = True
        setattr(target, "Read", read)

    if read and getattr(target, "ReadTimeStamp") is None:
        setattr(target, "ReadTimeStamp", datetime.utcnow())
    elif not read and getattr(target, "ReadTimeStamp") is not None:
        setattr(target, "ReadTimeStamp", None)

def on_notification_update(mapper, connection, target):
    read = getattr(target, "Read")
    if read and getattr(target, "ReadTimeStamp") is None:
        setattr(target, "ReadTimeStamp", datetime.utcnow())
    elif not read and getattr(target, "ReadTimeStamp") is not None:
        setattr(target, "ReadTimeStamp", None)


event.listen(Notification, "before_update", on_notification_update)  # Mapper Event
event.listen(Notification, "before_insert", on_notification_insert)  # mapper Event

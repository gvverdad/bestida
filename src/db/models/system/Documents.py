from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Enum, Text
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class Document(Model):
    __versioned__ = {}
    __tablename__ = "Documents"
    __table_args__ = dict(info=dict(label="Documents", key="Document"))

    Id = Column(Integer, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    Document = Column(String(16), index=True, unique=False, nullable=False,
                      info=dict(label="Document", case="uppercase",
                                selectId="Id",
                                selectKey="Document",
                                selectColumn="Document",
                                selectFormat=["Document", "Description"],
                                selectTable="Documents"
                                ))
    Description = Column(String(128), nullable=True, info=dict(label="Description"))

    Type = Column(Enum("pdf", "txt", "xls", "csv", "odf", name="DocumentTypes"),
                  nullable=False, default="pdf", info=dict(label="Type"))

    Script = Column(Text, info=dict(label="Script"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Document.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))

    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Document.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Task
    # uselist=False - this is just used in validate_delete
    Tasks = relationship("Task", uselist=False, back_populates="Document",
                         info=dict(hidden=True, dump=False))

    # One2Many side of Spooler
    # uselist=False - this is just used in validate_delete
    Spoolers = relationship("Spooler", uselist=False, back_populates="Document",
                            info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""
        if self.Tasks is not None:
            is_ok = False
            tables = "Tasks"
        if self.Spoolers is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Spoolers"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Document"
        return is_ok, message

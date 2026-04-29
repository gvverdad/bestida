import os
from datetime import datetime

from sqlalchemy import event, Column, ForeignKey, String, Integer, Date, DateTime, Index
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class Spooler(Model):
    __tablename__ = "Spoolers"
    __table_args__ = dict(info=dict(label="Spoolers", companyField="Company_Id"))

    Id = Column(Integer, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", selectId="Id", selectKey="Name",
                                  selectGetter="/getCompaniesList"))
    Company = relationship("Company", primaryjoin="Company.Id==Spooler.Company_Id")

    # Many2One
    Role_Id = Column(Integer, ForeignKey("Roles.Id"),
                     info=dict(label="Role", selectId="Id", selectKey="Role"))
    Role = relationship("Role", primaryjoin="Role.Id==Spooler.Role_Id")

    # Many2One
    Program_Id = Column(Integer, ForeignKey("Programs.Id"), nullable=False,
                        info=dict(label="Program", selectId="Id", selectKey="Name"))
    Program = relationship("Program",
                           primaryjoin="Program.Id==Spooler.Program_Id")

    # Many2One
    User_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                     default=get_current_uid,
                     info=dict(label="User",  selectId="Id", selectKey="UserId"))
    User = relationship("User", primaryjoin="User.Id==Spooler.User_Id")

    RunScript = Column(String(1024), nullable=False, info=dict(label="Run Script"))

    Title = Column(String(128), nullable=False, info=dict(label="Title"))

    File = Column(String(4096), nullable=False, info=dict(label="File"))

    # Many2One
    Document_Id = Column(Integer, ForeignKey("Documents.Id"), nullable=False,
                         info=dict(label="Document Type", selectId="Id",
                                   selectKey="Document"))
    Document = relationship("Document",
                            primaryjoin="Document.Id==Spooler.Document_Id")

    ExpiryDate = Column(Date, nullable=False, info=dict(label="Expiry Date"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Spooler.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))

    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Spooler.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("Spooler_Index1", Spooler.Company_Id, Spooler.Role_Id, Spooler.Program_Id, Spooler.User_Id, unique=False)
Index("Spooler_Index2", Spooler.Company_Id, Spooler.User_Id, Spooler.ExpiryDate, unique=False)
Index("Spooler_Index3", Spooler.ExpiryDate, unique=False)
Index("Spooler_Index4", Spooler.Company_Id, Spooler.Role_Id, unique=False)


def on_spooler_delete(mapper, connection, target):
    spoolfile = getattr(target, "File", None)

    try:
        os.remove(spoolfile)
    except:
        pass


event.listen(Spooler, "before_delete", on_spooler_delete)  # mapper Event

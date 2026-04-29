from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class WarehouseEmailType(Model):
    __versioned__ = {}
    __tablename__ = "WarehouseEmailTypes"
    __table_args__ = dict(info=dict(label="Warehouse Email Type",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Type"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==WarehouseEmailType.Company_Id")
        
    Type = Column(String(32), nullable=False, info=dict(label="Type",
                                                        case="uppercase",
                                                        selectId="Id",
                                                        selectKey="Type",
                                                        selectColumn="Type",
                                                        selectFormat=["Type", "Description"],
                                                        selectTable="WarehouseEmailTypes",
                                                        ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==WarehouseEmailType.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==WarehouseEmailType.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of WarehouseEmail
    # uselist=False - this is just used in validate_delete
    Emails = relationship("WarehouseEmail", uselist=False, back_populates="Type",
                          info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Emails is not None:
            is_ok = False
            tables = "WarehouseEmails"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Warehouse Email Type"

        return is_ok, message


Index("WarehouseEmailType_Index1", WarehouseEmailType.Company_Id,
      WarehouseEmailType.Type, unique=True)

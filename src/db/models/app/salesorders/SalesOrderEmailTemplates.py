from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Text, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class SalesOrderEmailTemplate(Model):
    __versioned__ = {}
    __tablename__ = "SalesOrderEmailTemplates"
    __table_args__ = dict(info=dict(label="Sales Order Email Template",
                                    desc="Email Template",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    key="Company_Id"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company",
                           primaryjoin="Company.Id==SalesOrderEmailTemplate.Company_Id")
        
    Subject = Column(String(128), nullable=False, info=dict(label="Email Subject"))

    Body = Column(Text, nullable=True, info=dict(label="Email Body"))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SalesOrderEmailTemplate.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SalesOrderEmailTemplate.CreateOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("SalesOrderEmailTemplate_Index1", SalesOrderEmailTemplate.Company_Id,
      unique=True)

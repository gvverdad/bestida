from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid
from .SupplierProcessingGroups import supplier_ageing_groups


class SupplierAgeingGroup(Model):
    __versioned__ = {}
    __tablename__ = "SupplierAgeingGroups"
    __table_args__ = dict(info=dict(label="Supplier Ageing Group",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Group"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SupplierAgeingGroup.Company_Id")
        
    Group = Column(String(32), nullable=False, info=dict(label="Process Group",
                                                         case="uppercase"))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SupplierAgeingGroup.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SupplierAgeingGroup.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # Many2Many
    ProcessingGroups = relationship("SupplierProcessingGroup",
                                    secondary=supplier_ageing_groups,
                                    back_populates="AgeingGroups",
                                    info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if len(self.ProcessingGroups):
            is_ok = False
            tables = "SupplierProcessingGroups"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Supplier Ageing Group"

        return is_ok, message


Index("SupplierAgeingGroup_Index1", SupplierAgeingGroup.Company_Id,
      SupplierAgeingGroup.Group, unique=True)

from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class CustomerPriority(Model):
    __versioned__ = {}
    __tablename__ = "CustomerPriorities"
    __table_args__ = dict(info=dict(label="Customer Priorities",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Priority"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==CustomerPriority.Company_Id")                                      

    # 1 is the highest Priority
    Priority = Column(Integer, nullable=False,
                      info=dict(label="Priority",
                                validator=["NotZero", "Positive"],
                                selectId="Id",
                                selectKey="Priority",
                                selectColumn="Priority",
                                selectFormat=["Priority", "Description"],
                                selectTable="CustomerPriorities",
                                ))

    Description = Column(String(128), nullable=False, info=dict(label="Description"))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==CustomerPriority.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CustomerPriority.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Customer
    # uselist=False - this is just used in validate_delete
    Customers = relationship("Customer", uselist=False,
                             back_populates="Priority",
                             info=dict(hidden=True, dump=False))

    Stores = relationship("CustomerStore", uselist=False,
                          back_populates="Priority",
                          info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Customers is not None:
            is_ok = False
            tables = "Customers"
        if self.Stores is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "CustomerStores"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Customer Priority"

        return is_ok, message


Index("CustomerPriority_Index1", CustomerPriority.Company_Id,
      CustomerPriority.Priority, unique=True)

from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class CustomerClass(Model):
    __versioned__ = {}
    __tablename__ = "CustomerClasses"
    __table_args__ = dict(info=dict(label="Customer Class",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Class"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==CustomerClass.Company_Id")                                      
        
    Class = Column(String(32), nullable=False, info=dict(label="Class",
                                                         case="uppercase",
                                                         selectId="Id",
                                                         selectKey="Class",
                                                         selectColumn="Class",
                                                         selectFormat=["Class", "Description"],
                                                         selectTable="CustomerClasses",
                                                         ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==CustomerClass.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CustomerClass.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Customer
    # uselist=False - this is just used in validate_delete
    Customers = relationship("Customer", uselist=False,
                             back_populates="Class",
                             info=dict(hidden=True, dump=False))
    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                                  back_populates="CustomerClass",
                                  info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Customers is not None:
            is_ok = False
            tables = "Customers"

        if self.ContractPrices is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Contract Price/Discounts"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Customer Class"

        return is_ok, message


Index("CustomerClass_Index1", CustomerClass.Company_Id, CustomerClass.Class, unique=True)

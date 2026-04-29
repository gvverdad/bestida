from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class CustomerContactType(Model):
    __versioned__ = {}
    __tablename__ = "CustomerContactTypes"
    __table_args__ = dict(info=dict(label="Customer Contact Type",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Type"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==CustomerContactType.Company_Id")
        
    Type = Column(String(32), nullable=False, info=dict(label="Type",
                                                        case="uppercase",
                                                        selectId="Id",
                                                        selectKey="Type",
                                                        selectColumn="Type",
                                                        selectFormat=["Type", "Description"],
                                                        selectTable="CustomerContactTypes",
                                                        ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==CustomerContactType.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CustomerContactType.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of CustomerContact
    # uselist=False - this is just used in validate_delete
    CustContacts = relationship("CustomerContact", uselist=False,
                                back_populates="Type",
                                info=dict(hidden=True, dump=False))
    CustStoreContacts = relationship("CustomerStoreContact", uselist=False,
                                     back_populates="Type",
                                     info=dict(hidden=True, dump=False))
    CustWarehouseContacts = relationship("CustomerWarehouseContact", uselist=False,
                                         back_populates="Type",
                                         info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.CustContacts is not None:
            is_ok = False
            tables = "CustomerContacts"

        if self.CustStoreContacts is not None:
            is_ok = False
            tables = (tables + ("" if tables == "" else ", ") +
                      "CustomerStoreContacts")

        if self.CustWarehouseContacts is not None:
            is_ok = False
            tables = (tables + ("" if tables == "" else ", ") +
                        "CustomerWarehouseContacts")

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Customer Contact Type"

        return is_ok, message


Index("CustomerContactType_Index1", CustomerContactType.Company_Id,
      CustomerContactType.Type, unique=True)

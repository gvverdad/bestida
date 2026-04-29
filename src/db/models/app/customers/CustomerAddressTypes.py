from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class CustomerAddressType(Model):
    __versioned__ = {}
    __tablename__ = "CustomerAddressTypes"
    __table_args__ = dict(info=dict(label="Customer Address Type",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Type"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==CustomerAddressType.Company_Id")
        
    Type = Column(String(32), nullable=False, info=dict(label="Type",
                                                        case="uppercase",
                                                        selectId="Id",
                                                        selectKey="Type",
                                                        selectColumn="Type",
                                                        selectFormat=["Type", "Description"],
                                                        selectTable="CustomerAddressTypes"
                                                        ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==CustomerAddressType.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CustomerAddressType.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of CustomerAddress
    # uselist=False - this is just used in validate_delete
    CustAddresses = relationship("CustomerAddress", uselist=False,
                                 back_populates="Type",
                                 info=dict(hidden=True, dump=False))
    CustStoreAddresses = relationship("CustomerStoreAddress", uselist=False,
                                 back_populates="Type",
                                 info=dict(hidden=True, dump=False))
    CustWarehouseAddresses = relationship("CustomerWarehouseAddress", uselist=False,
                                          back_populates="Type",
                                          info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.CustAddresses is not None:
            is_ok = False
            tables = "CustomerAddresses"

        if self.CustStoreAddresses is not None:
            is_ok = False
            tables = (tables + ("" if tables == "" else ", ") +
                        "CustomerStoreAddresses")

        if self.CustWarehouseAddresses is not None:
            is_ok = False
            tables = (tables + ("" if tables == "" else ", ") +
                        "CustomerWarehouseAddresses")

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Customer Address Type"

        return is_ok, message


Index("CustomerAddressType_Index1", CustomerAddressType.Company_Id,
      CustomerAddressType.Type, unique=True)

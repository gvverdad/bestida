from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class UOM(Model):
    __versioned__ = {}
    __tablename__ = "UOMs"
    __table_args__ = dict(info=dict(label="UOMs", companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="UOM"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==UOM.Company_Id")
        
    UOM = Column(String(8), nullable=False, info=dict(label="UOM",
                                                      case="uppercase",
                                                      selectId="Id",
                                                      selectKey="UOM",
                                                      selectColumn="UOM",
                                                      selectFormat=["UOM", "Description"],
                                                      selectTable="UOMs",
                                                      ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==UOM.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==UOM.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Products
    # uselist=False - this is just used in validate_delete
    Products = relationship("Product", uselist=False,
                            back_populates="UOM",
                            info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Products is not None:
            is_ok = False
            tables = "Products"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this UOM"

        return is_ok, message


Index("UOM_Index1", UOM.Company_Id, UOM.UOM, unique=True)

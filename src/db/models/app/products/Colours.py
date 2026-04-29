from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class Colour(Model):
    __versioned__ = {}
    __tablename__ = "Colours"
    __table_args__ = dict(info=dict(label="Colours",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Colour"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==Colour.Company_Id")
        
    Colour = Column(String(16), nullable=False, info=dict(label="Colour",
                                                          case="uppercase",
                                                          selectId="Id",
                                                          selectKey="Colour",
                                                          selectColumn="Colour",
                                                          selectFormat=["Colour", "Description"],
                                                          selectTable="Colours",
                                                          ))
    Description = Column(String(128), nullable=False,
                         info=dict(label="Description",
                                   alias="Colour_Description"))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Colour.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Colour.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of ProductColourFitDims
    # uselist=False - this is just used in validate_delete
    ProductColourFitDims = relationship("ProductColourFitDim", uselist=False,
                                        back_populates="Colour",
                                        info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.ProductColourFitDims is not None:
            is_ok = False
            tables = "ProductColourFitDims"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Colour"

        return is_ok, message


Index("Colour_Index1", Colour.Company_Id, Colour.Colour, unique=True)

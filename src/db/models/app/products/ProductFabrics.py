from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class ProductFabric(Model):
    __versioned__ = {}
    __tablename__ = "ProductFabrics"
    __table_args__ = dict(info=dict(label="Product Fabrics",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Fabric"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==ProductFabric.Company_Id")
        
    Fabric = Column(String(32), nullable=False, info=dict(label="Fabric",
                                                          case="uppercase",
                                                          selectId="Id",
                                                          selectKey="Fabric",
                                                          selectColumn="Fabric",
                                                          selectFormat=["Fabric", "Description"],
                                                          selectTable="ProductFabrics",
                                                          ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==ProductFabric.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==ProductFabric.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Products
    # uselist=False - this is just used in validate_delete
    Products = relationship("Product", uselist=False,
                            back_populates="Fabric",
                            primaryjoin="Product.Fabric_Id==ProductFabric.Id",
                            info=dict(hidden=True, dump=False))
    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                               back_populates="Fabric",
                               primaryjoin="ContractPriceDiscount.Fabric_Id==ProductFabric.Id",
                               info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Products is not None:
            is_ok = False
            tables = "Products"

        if self.ContractPrices is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Contract Price/Discounts"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Product Fabric"

        return is_ok, message


Index("ProductFabric_Index1", ProductFabric.Company_Id, ProductFabric.Fabric, unique=True)

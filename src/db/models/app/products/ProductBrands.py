from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid
from ..customers.Customers import brand_customer_table


class ProductBrand(Model):
    __versioned__ = {}
    __tablename__ = "ProductBrands"
    __table_args__ = dict(info=dict(label="Product Brands",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Brand"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==ProductBrand.Company_Id")
        
    Brand = Column(String(32), nullable=False, info=dict(label="Brand",
                                                         case="uppercase",
                                                         selectId="Id",
                                                         selectKey="Brand",
                                                         selectColumn="Brand",
                                                         selectFormat=["Brand", "Description"],
                                                         selectTable="ProductBrands",
                                                         ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==ProductBrand.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==ProductBrand.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # Many2Many
    Customers = relationship("Customer",
                             secondary=brand_customer_table,
                             back_populates="Brands",
                             info=dict(hidden=True, dump=False))

    # One2Many side of Products
    # uselist=False - this is just used in validate_delete
    Products = relationship("Product", uselist=False,
                            back_populates="Brand",
                            primaryjoin="Product.Brand_Id==ProductBrand.Id",
                            info=dict(hidden=True, dump=False))
    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                               back_populates="Brand",
                               primaryjoin="ContractPriceDiscount.Brand_Id==ProductBrand.Id",
                               info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Products is not None:
            is_ok = False
            tables = "Products"

        if len(self.Customers):
            is_ok = False
            tables = tables + (", " if tables else "") + "Customers"

        if self.ContractPrices is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Contract Price/Discounts"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Product Brand"

        return is_ok, message


Index("ProductBrand_Index1", ProductBrand.Company_Id, ProductBrand.Brand, unique=True)

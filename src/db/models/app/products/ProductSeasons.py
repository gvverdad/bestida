from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, Date, DateTime, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class ProductSeason(Model):
    __versioned__ = {}
    __tablename__ = "ProductSeasons"
    __table_args__ = dict(info=dict(label="Product Seasons",
                                    companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Season"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==ProductSeason.Company_Id")
        
    Season = Column(String(32), nullable=False, info=dict(label="Season",
                                                          case="uppercase",
                                                          selectId="Id",
                                                          selectKey="Season",
                                                          selectColumn="Season",
                                                          selectFormat=["Season", "Description"],
                                                          selectTable="ProductSeasons",
                                                          ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    StartDate = Column(Date(), nullable=False, default=None,
                       info=dict(label="Season Start Date"))
    EndDate = Column(Date(), nullable=False, default=None,
                     info=dict(label="Season End Date"))

    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==ProductSeason.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==ProductSeason.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Products
    # uselist=False - this is just used in validate_delete
    Products = relationship("Product", uselist=False,
                            back_populates="Season",
                            primaryjoin="Product.Season_Id==ProductSeason.Id",
                            info=dict(hidden=True, dump=False))
    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                               back_populates="Season",
                               primaryjoin="ContractPriceDiscount.Season_Id==ProductSeason.Id",
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
            message = f"Cannot Delete. {tables} linked to this Product Season"

        return is_ok, message


Index("ProductSeason_Index1", ProductSeason.Company_Id, ProductSeason.Season, unique=True)
Index("ProductSeason_Index2", ProductSeason.Company_Id, ProductSeason.StartDate, unique=False)
Index("ProductSeason_Index3", ProductSeason.Company_Id, ProductSeason.EndDate, unique=False)

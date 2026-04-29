from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, String, Date, Index,
                        Numeric, Enum)
from sqlalchemy.orm import relationship

from ....model import Model
from ....functions import get_currency_choices, get_default_currency
from ......security.policy import get_current_uid


class PriceList(Model):
    __versioned__ = {}
    __tablename__ = "PriceLists"
    __table_args__ = dict(info=dict(label="Product PriceLists",
                                    companyField="Company_Id"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==PriceList.Company_Id")

    # Many2One
    Style_Id = Column(Integer, ForeignKey("Products.Id"), nullable=False,
                      info=dict(label="Style",
                                selectId="Id", selectKey="Style",
                                selectFormat=["Style", "Name"],
                                depth=1))
    Style = relationship("Product", primaryjoin="Product.Id==PriceList.Style_Id")

    # Many2One
    ColFitDim_Id = Column(Integer, ForeignKey("ProductColourFitDims.Id"),
                          nullable=True,
                          info=dict(label="Colour/Fitting/Dimension",
                                    selectId="Id",
                                    selectKey="style_col_fit_dim",
                                    selectFormat=["ItemProduct.Style",
                                                  "Colour.Description",
                                                  "Fitting.Description",
                                                  "Dimension.Description"],
                                    selectField="ItemProduct_Id",
                                    selectFieldValue="Style.Id"
                                    ))
    ColFitDim = relationship("ProductColourFitDim",
                             primaryjoin="ProductColourFitDim.Id==PriceList.ColFitDim_Id")

    # Many2One
    SKU_Id = Column(Integer, ForeignKey("ProductSKUs.Id"), nullable=True,
                    info=dict(label="Size",
                              selectId="Id",
                              selectKey="Size.Size",
                              selectFormat=["ItemColourFitDim.ItemProduct.Style",
                                            "ItemColourFitDim.Colour.Description",
                                            "ItemColourFitDim.Fitting.Description",
                                            "ItemColourFitDim.Dimension.Description",
                                            "Size.Size"],
                              selectField="ItemColourFitDim_Id",
                              selectFieldValue="ColFitDim.Id"
                              ))
    SKU = relationship("ProductSKU",
                       primaryjoin="ProductSKU.Id==PriceList.SKU_Id")

    Currency = Column(String(3), nullable=False, default=get_default_currency,
                      info=dict(label="Currency",
                                choices=get_currency_choices,
                                choices_getter="getCurrencyList"))

    EffectiveFrom = Column(Date, nullable=False, info=dict(label="Effective Date From"))
    EffectiveTo = Column(Date, nullable=False, info=dict(label="Effective Date To"))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("PriceTypes.Id"),
                     nullable=False, info=dict(label="Type", selectId="Id",
                                               selectKey="Description",
                                               depth=1))
    Type = relationship("PriceType", primaryjoin="PriceType.Id==PriceList.Type_Id")

    # PriceList is ex GST
    Price = Column(Numeric(20, 8), nullable=False,
                   default=0,
                   info=dict(label="Price",
                             numberType="currency",  # number, currency, percent, string
                             currencyCodeField="Currency",
                             validator=["ZeroPositive"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==PriceList.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==PriceList.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("PriceList_Index1",
      PriceList.Company_Id,
      PriceList.Style_Id, PriceList.ColFitDim_Id, PriceList.SKU_Id,
      PriceList.Currency, PriceList.EffectiveFrom, PriceList.EffectiveTo,
      PriceList.Type_Id,
      unique=True)

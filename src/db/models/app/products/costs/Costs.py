from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, String, Date, Index,
                        Numeric, Enum)
from sqlalchemy.orm import relationship

from ....model import Model
from ....functions import get_currency_choices, get_default_currency
from ......security.policy import get_current_uid


class Cost(Model):
    __tablename__ = "Costs"
    __table_args__ = dict(info=dict(label="Product Costs",
                                    companyField="Company_Id"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==Cost.Company_Id")

    # Many2One
    Style_Id = Column(Integer, ForeignKey("Products.Id"), nullable=False,
                      info=dict(label="Style",
                                selectId="Id", selectKey="Style",
                                selectFormat=["Style", "Name"],
                                depth=1))
    Style = relationship("Product", primaryjoin="Product.Id==Cost.Style_Id")

    # Many2One
    ColFitDim_Id = Column(Integer, ForeignKey("ProductColourFitDims.Id"),
                          nullable=True,
                          info=dict(label="Colour/Fitting/Dimension",
                                    selectId="Id",
                                    selectKey=["Colour.Colour",
                                               "Fitting.Fitting",
                                               "Dimension.Dimension"],
                                    selectFormat=["ItemProduct.Style",
                                                  "Colour.Description",
                                                  "Fitting.Description",
                                                  "Dimension.Description"],
                                    selectField="ItemProduct_Id",
                                    selectFieldValue="Style.Id"
                                    ))
    ColFitDim = relationship("ProductColourFitDim",
                             primaryjoin="ProductColourFitDim.Id==Cost.ColFitDim_Id")

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
                              selectFieldValue="ColFitDim.Id",
                              ))
    SKU = relationship("ProductSKU",
                       primaryjoin="ProductSKU.Id==Cost.SKU_Id")

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CostTypes.Id"),
                     nullable=False, info=dict(label="Type", selectId="Id",
                                               selectKey="Description",
                                               depth=1))
    Type = relationship("CostType", primaryjoin="CostType.Id==Cost.Type_Id")

    Currency = Column(String(3), nullable=False, default=get_default_currency,
                      info=dict(label="Currency",
                                choices=get_currency_choices,
                                choices_getter="getCurrencyList"))

    # Cost is ex GST
    Cost = Column(Numeric(19, 8), nullable=False, default=0,
                  info=dict(label="Cost",
                            numberType="currency",  # number, currency, percent, string
                            currencyCodeField="Currency",
                            validator=["ZeroPositive"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Cost.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Cost.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("Cost_Index1",
      Cost.Company_Id,
      Cost.Style_Id, Cost.ColFitDim_Id, Cost.SKU_Id,
      Cost.Type_Id, Cost.Currency,
      unique=True)

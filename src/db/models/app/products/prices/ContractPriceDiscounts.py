from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Date, Index,
                        String, Numeric)
from sqlalchemy.orm import relationship

from ....model import Model
from ....functions import get_currency_choices, get_default_currency
from ......security.policy import get_current_uid


class ContractPriceDiscount(Model):
    __versioned__ = {}
    __tablename__ = "ContractPriceDiscounts"
    __table_args__ = dict(info=dict(label="Contract Price/Discounts",
                                    companyField="Company_Id"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==ContractPriceDiscount.Company_Id")

    Currency = Column(String(3), nullable=False, default=get_default_currency,
                      info=dict(label="Currency",
                                choices=get_currency_choices,
                                choices_getter="getCurrencyList"))

    # Many2One
    Customer_Id = Column(Integer, ForeignKey("Customers.Id"),
                         nullable=True,
                         info=dict(label="Account",
                                   selectId="Id",
                                   selectKey="Name",
                                   selectFormat=["Account", "Name"],
                                   selectTableFieldValue=[{"field": "Inactive", "value": False}],
                                   ))
    Customer = relationship("Customer",
                            primaryjoin="Customer.Id==ContractPriceDiscount.Customer_Id")

    # Many2One
    DeliverVia_Id = Column(Integer, ForeignKey("CustomerWarehouses.Id"),
                           nullable=True,
                           info=dict(label="Deliver Via",
                                     selectId="Id",
                                     selectKey="Name",
                                     selectFormat=["ItemCustomer.Account",
                                                   "Warehouse",
                                                   "Name"],
                                     selectField="ItemCustomer_Id",
                                     selectFieldValue="Customer.Id",
                                     selectTableFieldValue=[{"field": "Inactive", "value": False}],
                                     ))
    DeliverVia = relationship("CustomerWarehouse",
                              primaryjoin="CustomerWarehouse.Id==ContractPriceDiscount.DeliverVia_Id")

    # Many2One
    Store_Id = Column(Integer, ForeignKey("CustomerStores.Id"),
                      nullable=True,
                      info=dict(label="Store",
                                selectId="Id",
                                selectKey="Name",
                                selectFormat=["ItemCustomer.Account",
                                              "Store",
                                              "Name"],
                                selectField="ItemCustomer_Id",
                                selectFieldValue="Customer.Id",
                                selectTableFieldValue=[{"field": "Inactive", "value": False},
                                                       {"field": "AllowDeliveries", "value": True}],
                                ))
    Store = relationship("CustomerStore",
                         primaryjoin="CustomerStore.Id==ContractPriceDiscount.Store_Id")

    # Many2One
    Region_Id = Column(Integer, ForeignKey("CustomerRegions.Id"),
                       nullable=True,
                       info=dict(label="Region", selectId="Id",
                                 selectKey="Description",
                                 depth=1))
    Region = relationship("CustomerRegion",
                          primaryjoin="CustomerRegion.Id==ContractPriceDiscount.Region_Id")

    # Many2One
    CustomerType_Id = Column(Integer, ForeignKey("CustomerTypes.Id"),
                             nullable=True,
                             info=dict(label="Customer Type", selectId="Id",
                                       selectKey="Description",
                                       depth=1))
    CustomerType = relationship("CustomerType",
                                primaryjoin="CustomerType.Id==ContractPriceDiscount.CustomerType_Id")

    # Many2One
    CustomerClass_Id = Column(Integer, ForeignKey("CustomerClasses.Id"),
                              nullable=True,
                              info=dict(label="Customer Class", selectId="Id",
                                        selectKey="Description",
                                        depth=1))
    CustomerClass = relationship("CustomerClass",
                                 primaryjoin="CustomerClass.Id==ContractPriceDiscount.CustomerClass_Id")

    # Many2One
    CustomerGroup_Id = Column(Integer, ForeignKey("CustomerGroups.Id"), 
                              nullable=True,
                              info=dict(label="Customer Group", selectId="Id",
                                        selectKey="Description",
                                        depth=1))
    CustomerGroup = relationship("CustomerGroup", 
                                 primaryjoin="CustomerGroup.Id==ContractPriceDiscount.CustomerGroup_Id")

    # Many2One
    Style_Id = Column(Integer, ForeignKey("Products.Id"),
                      nullable=True,
                      info=dict(label="Style",
                                selectId="Id", selectKey="Style",
                                selectFormat=["Style", "Name"],
                                depth=1))
    Style = relationship("Product",
                         primaryjoin="Product.Id==ContractPriceDiscount.Style_Id")

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
                                    selectFieldValue="Style.Id",
                                    selectTableFieldValue=[{"field": "AllowSales", "value": True}],
                                    depth=1))
    ColFitDim = relationship("ProductColourFitDim",
                             primaryjoin="ProductColourFitDim.Id==ContractPriceDiscount.ColFitDim_Id")

    # Many2One
    SKU_Id = Column(Integer, ForeignKey("ProductSKUs.Id"),
                    nullable=True,
                    info=dict(label="Size",
                              selectId="Id",
                              selectKey="Size.Size",
                              selectFormat=["Size.Size"],
                              selectField="ItemColourFitDim_Id",
                              selectFieldValue="ColFitDim.Id",
                              selectTableFieldValue=[{"field": "Status", "value": "Valid"}],
                              depth=1
                              ))
    SKU = relationship("ProductSKU",
                       primaryjoin="ProductSKU.Id==ContractPriceDiscount.SKU_Id")

    # Many2One
    Gender_Id = Column(Integer, ForeignKey("ProductGenders.Id"),
                       nullable=True,
                       info=dict(label="Product Gender", selectId="Id",
                                 selectKey="Description",
                                 depth=1))
    Gender = relationship("ProductGender",
                          primaryjoin="ProductGender.Id==ContractPriceDiscount.Gender_Id")

    # Many2One
    Brand_Id = Column(Integer, ForeignKey("ProductBrands.Id"),
                      nullable=True,
                      info=dict(label="Brand", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Brand = relationship("ProductBrand",
                         primaryjoin="ProductBrand.Id==ContractPriceDiscount.Brand_Id")

    # Many2One
    Category_Id = Column(Integer, ForeignKey("ProductCategories.Id"),
                         nullable=True,
                         info=dict(label="Product Category", selectId="Id",
                                   selectKey="Description", depth=1))
    Category = relationship("ProductCategory",
                            primaryjoin="ProductCategory.Id==ContractPriceDiscount.Category_Id")

    # Many2One
    Fabric_Id = Column(Integer, ForeignKey("ProductFabrics.Id"),
                       nullable=True,
                       info=dict(label="Fabric", selectId="Id",
                                 selectKey="Description", depth=1))
    Fabric = relationship("ProductFabric",
                          primaryjoin="ProductFabric.Id==ContractPriceDiscount.Fabric_Id")

    # Many2One
    Class_Id = Column(Integer, ForeignKey("ProductClasses.Id"),
                      nullable=True,
                      info=dict(label="Product Class", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Class = relationship("ProductClass",
                         primaryjoin="ProductClass.Id==ContractPriceDiscount.Class_Id")

    # Many2One
    Type_Id = Column(Integer, ForeignKey("ProductTypes.Id"),
                     nullable=True,
                     info=dict(label="Product Type", selectId="Id",
                               selectKey="Description",
                               depth=1))
    Type = relationship("ProductType",
                        primaryjoin="ProductType.Id==ContractPriceDiscount.Type_Id")

    # Many2One
    Group_Id = Column(Integer, ForeignKey("ProductGroups.Id"),
                      nullable=True,
                      info=dict(label="Product Group", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Group = relationship("ProductGroup",
                         primaryjoin="ProductGroup.Id==ContractPriceDiscount.Group_Id")

    # Many2One
    Season_Id = Column(Integer, ForeignKey("ProductSeasons.Id"),
                       nullable=True,
                       info=dict(label="Season", selectId="Id",
                                 selectKey="Description", depth=1))
    Season = relationship("ProductSeason",
                          primaryjoin="ProductSeason.Id==ContractPriceDiscount.Season_Id")

    # Many2One
    ShipFromWarehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                                  nullable=True,
                                  info=dict(label="Ship From Warehouse",
                                            selectId="Id", selectKey="Name",
                                            depth=1))
    ShipFromWarehouse = relationship("Warehouse",
                                     primaryjoin="Warehouse.Id==ContractPriceDiscount.ShipFromWarehouse_Id")

    # Many2One
    Source_Id = Column(Integer, ForeignKey("SalesOrderSources.Id"),
                       nullable=True, info=dict(label="Order Source", selectId="Id",
                                                selectKey="Description",
                                                depth=1))
    Source = relationship("SalesOrderSource",
                          primaryjoin="SalesOrderSource.Id==ContractPriceDiscount.Source_Id")

    EffectiveFrom = Column(Date, nullable=False, 
                           info=dict(label="Effective Date From"))
    EffectiveTo = Column(Date, nullable=False, 
                         info=dict(label="Effective Date To"))

    Volume = Column(Integer, default=0, nullable=True,
                    info=dict(label="Max Volume",
                              validator=["ZeroPositive"]))

    Price = Column(Numeric(20, 8), default=0, nullable=False,
                   info=dict(label="Price",
                             requiredIf="Discount == 0",
                             numberType="currency",  # number, currency, percent, string
                             currencyCodeField="Currency",
                             validator_messages=[dict(RequiredIf="Price OR Discount required")],
                             validator=["ZeroPositive"]))

    Discount = Column(Numeric(10, 6), default=0, nullable=False,
                      info=dict(label="Discount Percentage",
                                numberType="percent",  # number, currency, percent, string
                                validator=["ZeroPositive"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==ContractPriceDiscount.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==ContractPriceDiscount.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("ContractPriceDiscount_Index1",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Customer_Id, ContractPriceDiscount.DeliverVia_Id, ContractPriceDiscount.Store_Id,
      ContractPriceDiscount.Region_Id, ContractPriceDiscount.CustomerType_Id,
      ContractPriceDiscount.CustomerClass_Id, ContractPriceDiscount.CustomerGroup_Id,
      ContractPriceDiscount.Style_Id, ContractPriceDiscount.ColFitDim_Id, ContractPriceDiscount.SKU_Id,
      ContractPriceDiscount.Season_Id, ContractPriceDiscount.Gender_Id,
      ContractPriceDiscount.Brand_Id, ContractPriceDiscount.Category_Id,
      ContractPriceDiscount.Fabric_Id, ContractPriceDiscount.Class_Id,
      ContractPriceDiscount.Type_Id, ContractPriceDiscount.Group_Id,
      ContractPriceDiscount.ShipFromWarehouse_Id, ContractPriceDiscount.Source_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo,
      ContractPriceDiscount.Volume,
      unique=True)
Index("ContractPriceDiscount_Index2",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Customer_Id, ContractPriceDiscount.DeliverVia_Id, ContractPriceDiscount.Store_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index3",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Region_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index4",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.CustomerType_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index5",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.CustomerClass_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index6",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.CustomerGroup_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index7",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Style_Id, ContractPriceDiscount.ColFitDim_Id, ContractPriceDiscount.SKU_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index8",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Gender_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index9",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Brand_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index10",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Category_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index11",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Fabric_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index12",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Class_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index13",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Type_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index14",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Group_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index15",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Season_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index16",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.ShipFromWarehouse_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)
Index("ContractPriceDiscount_Index17",
      ContractPriceDiscount.Company_Id, ContractPriceDiscount.Currency,
      ContractPriceDiscount.Source_Id,
      ContractPriceDiscount.EffectiveFrom, ContractPriceDiscount.EffectiveTo, ContractPriceDiscount.Volume,
      unique=False)

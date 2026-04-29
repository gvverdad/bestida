from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Index, String,
                        Boolean, func, select, Table)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid

keyword_product_table = Table("keyword_product", Model.metadata,
                              Column("keyword_id", Integer, ForeignKey("ProductKeywords.Id")),
                              Column("product_id", Integer, ForeignKey("Products.Id"))
                              )
keyword_product_table.__versioned__ = {}  # Mark the secondary table for versioning

class Product(Model):
    __versioned__ = {}
    __tablename__ = "Products"
    __table_args__ = dict(info=dict(label="Styles",
                                    companyField="Company_Id",
                                    stepperTitleFields=["Style", "Name"],
                                    keyPaths=["Company_Id"],
                                    key="Style",
                                    hybrids=[dict(name="number_of_colfitdims",
                                                  label="ColourFitDims",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True)],
                                    documents=[
                                        dict(program="DocumentFGNetPosition",
                                             title="Net Position",
                                             params=dict(styleId="Id"))
                                    ]
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==Product.Company_Id")

    Style = Column(String(20), nullable=False,
                   info=dict(label="Style",
                             case="uppercase",
                             selectId="Id",
                             selectKey="Style",
                             selectColumn="Style",
                             selectFormat=["Style", "Name"],
                             selectTable="Products",
                             documents=[
                                 dict(program="DocumentProduct",
                                      params=dict(style="."))
                             ]
                             ))

    Name = Column(String(128), nullable=False, info=dict(label="Name"))

    # Many2Many
    Keywords = relationship("ProductKeyword", secondary=keyword_product_table,
                            back_populates="Products",
                            info=dict(label="Search Keywords",
                                      selectId="Id", selectKey="Keyword",
                                      depth=1))

    Number = Column(String(30), nullable=True,
                    info=dict(label="Product Number",
                              selectId="Id",
                              selectKey="Number",
                              selectColumn="Number",
                              selectFormat=["Number", "Style", "Name"],
                              selectTable="Products",
                              ))

    Sample = Column(Boolean, default=False, info=dict(label="Sample Style"))
    AllowSales = Column(Boolean, default=False, info=dict(label="Allow Sales"))
    AllowProduction = Column(Boolean, default=False, info=dict(label="Allow Production"))
    AllowPurchasing = Column(Boolean, default=False, info=dict(label="Allow Purchasing"))

    # Many2One
    UOM_Id = Column(Integer, ForeignKey("UOMs.Id"), nullable=False,
                    info=dict(label="UOM", selectId="Id",
                              selectKey="Description",
                              depth=1))
    UOM = relationship("UOM", primaryjoin="UOM.Id==Product.UOM_Id")

    # Many2One
    Season_Id = Column(Integer, ForeignKey("ProductSeasons.Id"), nullable=False,
                       info=dict(label="Season", selectId="Id",
                                 selectKey="Description", depth=1))
    Season = relationship("ProductSeason",
                          primaryjoin="ProductSeason.Id==Product.Season_Id")

    # Many2One
    Gender_Id = Column(Integer, ForeignKey("ProductGenders.Id"), nullable=False,
                       info=dict(label="Gender", selectId="Id",
                                 selectKey="Description",
                                 depth=1))
    Gender = relationship("ProductGender",
                          primaryjoin="ProductGender.Id==Product.Gender_Id")

    # Many2One
    Brand_Id = Column(Integer, ForeignKey("ProductBrands.Id"), nullable=False,
                      info=dict(label="Brand", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Brand = relationship("ProductBrand",
                         primaryjoin="ProductBrand.Id==Product.Brand_Id")

    # Many2One
    Category_Id = Column(Integer, ForeignKey("ProductCategories.Id"), nullable=False,
                         info=dict(label="Category", selectId="Id",
                                   selectKey="Description", depth=1))
    Category = relationship("ProductCategory",
                            primaryjoin="ProductCategory.Id==Product.Category_Id")

    # Many2One
    Fabric_Id = Column(Integer, ForeignKey("ProductFabrics.Id"), nullable=False,
                       info=dict(label="Fabric", selectId="Id",
                                 selectKey="Description", depth=1))
    Fabric = relationship("ProductFabric",
                          primaryjoin="ProductFabric.Id==Product.Fabric_Id")

    # Many2One
    Class_Id = Column(Integer, ForeignKey("ProductClasses.Id"), nullable=False,
                      info=dict(label="Class", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Class = relationship("ProductClass",
                         primaryjoin="ProductClass.Id==Product.Class_Id")

    # Many2One
    Type_Id = Column(Integer, ForeignKey("ProductTypes.Id"), nullable=False,
                     info=dict(label="Type", selectId="Id",
                               selectKey="Description",
                               depth=1))
    Type = relationship("ProductType",
                        primaryjoin="ProductType.Id==Product.Type_Id")

    # Many2One
    Group_Id = Column(Integer, ForeignKey("ProductGroups.Id"), nullable=False,
                      info=dict(label="Group", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Group = relationship("ProductGroup",
                         primaryjoin="ProductGroup.Id==Product.Group_Id")

    # Many2One
    SizeScale_Id = Column(Integer, ForeignKey("SizeScales.Id"), nullable=False,
                          info=dict(label="SizeScale", selectId="Id",
                                    selectKey="Description", depth=1))
    SizeScale = relationship("SizeScale",
                             primaryjoin="SizeScale.Id==Product.SizeScale_Id")

    # TODO:  Weight, Dimension, Replen Days, Hit Dates, Costing, BOM, ReOrder Qty, Substitute Style, Pref Supplier

    # One2One side of ProductProcessingGroup
    ProcessingGroups = relationship("ProductProcessingGroup", uselist=False,
                                    back_populates="ItemProduct",
                                    primaryjoin="ProductProcessingGroup.ItemProduct_Id==Product.Id",
                                    cascade="all, delete-orphan",
                                    info=dict(label="Processing Groups",
                                              gridSubTable=True,
                                              dumpFields=["Id"]))

    # One2Many
    Descriptions = relationship("ProductStyleDescription", uselist=True,
                                backref="ItemProduct",
                                cascade="all, delete-orphan",
                                info=dict(dumpFields=["Id"]))

    # One2Many
    Images = relationship("ProductStyleImage", uselist=True,
                                backref="ItemProduct",
                                cascade="all, delete-orphan",
                                info=dict(dumpFields=["Id"]))


    # One2Many
    ColourFitDims = relationship("ProductColourFitDim", uselist=True,
                                 backref="ItemProduct",
                                 cascade="all, delete-orphan",
                                 info=dict(dumpFields=["Id"]))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Product.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Product.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of ContractPriceDiscount
    # uselist=False - this is just used in validate_delete
    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                               back_populates="Style",
                               info=dict(hidden=True, dump=False))
    PriceBands = relationship("PriceBand", uselist=False,
                               back_populates="Style",
                               info=dict(hidden=True, dump=False))


    @hybrid_property
    def number_of_colfitdims(self):
        return len(self.ColourFitDims)

    @number_of_colfitdims.expression
    def number_of_colfitdims(cls):
        from .ProductColourFitDims import ProductColourFitDim

        return (select([func.count()]).
                where(ProductColourFitDim.ItemProduct_Id == cls.Id).
                as_scalar())

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = ""
        tables = ""

        for cfd in self.ColourFitDims:
            is_ok, tables = cfd.validate_delete(user_rowid, company_rowid,
                                                 locale, timezone, None)
            if not is_ok:
                break

        if self.ContractPrices is not None:
            is_ok = False
            tables = "Contract Price/Discounts"

        if not is_ok:
            if data is None:
                message = tables
            else:
                message = f"Cannot Delete. {tables} linked to this Style"

        return is_ok, message


Index("Product_Index1", Product.Company_Id, Product.Style, unique=True)
Index("Product_Index2", Product.Company_Id, Product.Season_Id, unique=False)
Index("Product_Index3", Product.Company_Id, Product.Brand_Id, unique=False)
Index("Product_Index4", Product.Company_Id, Product.Class_Id, unique=False)
Index("Product_Index5", Product.Company_Id, Product.Group_Id, unique=False)
Index("Product_Index6", Product.Company_Id, Product.Type_Id, unique=False)
Index("Product_Index7", Product.Company_Id, Product.Category_Id, unique=False)
Index("Product_Index8", Product.Company_Id, Product.Number, unique=False)

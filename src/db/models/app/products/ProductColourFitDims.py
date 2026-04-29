from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, String, Index,
                        func, select, Boolean)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid


class ProductColourFitDim(Model):
    __versioned__ = {}
    __tablename__ = "ProductColourFitDims"
    __table_args__ = dict(info=dict(label="Colour/Fitting/Dimensions",
                                    desc="Colour/Fitting/Dimensions",
                                    companyField="Company_Id",
                                    stepperTitleFields=["Colour.Colour",
                                                  "Fitting.Fitting",
                                                  "Dimension.Dimension",
                                                  "Name"],
                                    keyPaths=["Company_Id", "Colour_Id",
                                              "Fitting_Id"],
                                    key="Dimension_Id",
                                    parentTables=[
                                        dict(column="ItemProduct",
                                             table="Products")
                                    ],
                                    hybrids=[dict(name="number_of_sizes",
                                                  label="Sizes",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="style_col_fit_dim",
                                                  label="Style/Col/Fit/Dim",
                                                  type="String",
                                                  length=71,
                                                  decimals=0,
                                                  sortable=True,
                                                  searchable=True)
                                             ],
                                    documents=[
                                        dict(program="DocumentFGNetPosition",
                                             title="Net Position",
                                             params=dict(styleId="ItemProduct_Id",
                                                         colFitDimId="Id"))
                                    ]
                                    )
                          )

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==ProductColourFitDim.Company_Id")

    # Many2One side of Product
    ItemProduct_Id = Column(Integer, ForeignKey("Products.Id"),
                            info=dict(label="Style",
                                      selectId="Id", selectKey="Style",
                                      selectFormat=["Style", "Name"],
                                      exceptSchemaFields=["Company_Id", "Company", "ColourFitDims",
                                                          "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                          "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                          "versions"],
                                      depth=1))

    # Many2One
    Colour_Id = Column(Integer, ForeignKey("Colours.Id"), nullable=False,
                       info=dict(label="Colour", selectId="Id",
                                 selectKey="Description",
                                 selectFormat=["Colour", "Description"],
                                 depth=1))
    Colour = relationship("Colour", primaryjoin="Colour.Id==ProductColourFitDim.Colour_Id")

    # Many2One
    Fitting_Id = Column(Integer, ForeignKey("Fittings.Id"), nullable=True,
                        info=dict(label="Fitting",
                                  selectId="Id",
                                  selectKey="Description",
                                  selectFormat=["Fitting", "Description"],
                                  depth=1))
    Fitting = relationship("Fitting", primaryjoin="Fitting.Id==ProductColourFitDim.Fitting_Id")

    # Many2One
    Dimension_Id = Column(Integer, ForeignKey("Dimensions.Id"), nullable=True,
                          info=dict(label="Dimension", selectId="Id",
                                    selectKey="Description",
                                    selectFormat=["Dimension", "Description"],
                                    depth=1))
    Dimension = relationship("Dimension", primaryjoin="Dimension.Id==ProductColourFitDim.Dimension_Id")

    Name = Column(String(128), nullable=True, info=dict(label="Name"))

    Number = Column(String(30), nullable=True,
                    info=dict(label="Product Number",
                              selectId="Id",
                              selectKey="Number",
                              selectColumn="Number",
                              selectFormat=["Number", "style_col_fit_dim"],
                              selectTable="ProductColourFitDims",
                              ))

    AllowSales = Column(Boolean, default=False, info=dict(label="Allow Sales"))
    AllowProduction = Column(Boolean, default=False, info=dict(label="Allow Production"))
    AllowPurchasing = Column(Boolean, default=False, info=dict(label="Allow Purchasing"))

    # Many2One
    Season_Id = Column(Integer, ForeignKey("ProductSeasons.Id"), nullable=False,
                       info=dict(label="Season", selectId="Id",
                                 selectKey="Description",
                                 depth=1))
    Season = relationship("ProductSeason", primaryjoin="ProductSeason.Id==ProductColourFitDim.Season_Id")

    # One2Many
    Descriptions = relationship("ProductColourFitDimDescription", uselist=True,
                                backref="ItemColourFitDim",
                                cascade="all, delete-orphan",
                                info=dict(dumpFields=["Id"], depth=1))

    # One2Many
    Images = relationship("ProductColourFitDimImage", uselist=True,
                                backref="ItemColourFitDim",
                                cascade="all, delete-orphan",
                                info=dict(dumpFields=["Id"], depth=1))

    # One2Many
    Sizes = relationship("ProductSKU", uselist=True,
                         backref="ItemColourFitDim",
                         cascade="all, delete-orphan",
                         info=dict(dumpFields=["Id"], depth=1))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==ProductColourFitDim.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==ProductColourFitDim.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of ContractPriceDiscount
    # uselist=False - this is just used in validate_delete
    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                               back_populates="ColFitDim",
                               primaryjoin="ContractPriceDiscount.ColFitDim_Id==ProductColourFitDim.Id",
                               info=dict(hidden=True, dump=False))

    @hybrid_property
    def number_of_sizes(self):
        return len(self.Sizes)

    @number_of_sizes.expression
    def number_of_sizes(cls):
        from .ProductSKUs import ProductSKU

        return (select([func.count()]).
                where(ProductSKU.ItemColourFitDim_Id == cls.Id).
                as_scalar())

    @hybrid_property
    def style_col_fit_dim(self):
        if self.Dimension:
            return self.ItemProduct.Style + " " + \
                   self.Colour.Colour + " " + \
                   self.Fitting.Fitting + " " + \
                   self.Dimension.Dimension
        elif self.Fitting:
            return self.ItemProduct.Style + " " + \
                   self.Colour.Colour + " " + \
                   self.Fitting.Fitting
        else:
            return self.ItemProduct.Style + " " + \
                   self.Colour.Colour

    @style_col_fit_dim.expression
    def style_col_fit_dim(cls):
        from .Products import Product
        from .Colours import Colour
        from .Fittings import Fitting
        from .Dimensions import Dimension

        if cls.Dimension:
            return (select([Product.Style + " " +
                           Colour.Colour + " " +
                           Fitting.Fitting + " " +
                           Dimension.Dimension]).
                    where(Product.Id == cls.ItemProduct_Id).
                    where(Colour.Id == cls.Colour_Id).
                    where(Fitting.Id == cls.Fitting_Id).
                    where(Dimension.Id == cls.Dimension_Id).
                    as_scalar())
        elif cls.Fitting:
            return (select([Product.Style + " " +
                           Colour.Colour + " " +
                           Fitting.Fitting]).
                    where(Product.Id == cls.ItemProduct_Id).
                    where(Colour.Id == cls.Colour_Id).
                    where(Fitting.Id == cls.Fitting_Id).
                    as_scalar())
        else:
            return (select([Product.Style + " " +
                           Colour.Colour]).
                    where(Product.Id == cls.ItemProduct_Id).
                    where(Colour.Id == cls.Colour_Id).as_scalar())

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data=None):
        is_ok = True
        message = ""
        tables = ""

        for size in self.Sizes:
            is_ok, message = size.validate_delete(user_rowid, company_rowid,
                                                  locale, timezone)
            if not is_ok:
                break

        if self.ContractPrices is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Contract Price/Discounts"

        if not is_ok:
            if data is None:
                message = f"Cannot Delete. {tables} linked to this Colour/Fitting/Dimensions"
            else:
                message = f"Cannot Delete. {tables} linked to this Colour/Fitting/Dimensions"

        return is_ok, message

    # Fitting_Id and Dimension_Id are nullable - enforce uniqueness - see db.models.unique
    __nullable_unique_fields__ = ["Company_Id", "ItemProduct_Id", "Colour_Id", "Fitting_Id", "Dimension_Id"]

Index("ProductColourFitDim_Index1", ProductColourFitDim.Company_Id,
      ProductColourFitDim.ItemProduct_Id,
      ProductColourFitDim.Colour_Id,
      ProductColourFitDim.Fitting_Id,
      ProductColourFitDim.Dimension_Id,
      unique=True,
)
Index("ProductColourFitDim_Index2", ProductColourFitDim.Company_Id,
      ProductColourFitDim.Season_Id, unique=False)
Index("ProductColourFitDim_Index3", ProductColourFitDim.Company_Id,
      ProductColourFitDim.Number, unique=False)

from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, String,
                        Enum, Index, select, func)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid


class ProductSKU(Model):
    __versioned__ = {}
    __tablename__ = "ProductSKUs"
    __table_args__ = dict(info=dict(label="Product Sizes",
                                    desc="Sizes",
                                    companyField="Company_Id",
                                    stepperTitleFields=["Size.Size"],
                                    keyPaths=["ItemColourFitDim_Id"],
                                    key="Size_Id",
                                    parentTables=[
                                        dict(column="ItemColourFitDim",
                                             table="ProductColourFitDims")
                                    ],
                                    hybrids=[dict(name="style_col_fit_dim_size",
                                                  label="Style/Col/Fit/Dim/Size",
                                                  type="String",
                                                  length=88,
                                                  decimals=0,
                                                  sortable=True,
                                                  searchable=True),
                                             dict(name="size",
                                                  label="Size",
                                                  type="String",
                                                  length=16,
                                                  decimals=0,
                                                  sortable=True,
                                                  searchable=True)
                                    ]
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company",
                           primaryjoin="Company.Id==ProductSKU.Company_Id")

    # Many2One side of ProductColourFitDims
    ItemColourFitDim_Id = Column(Integer, ForeignKey("ProductColourFitDims.Id"),
                                 info=dict(label="Style/Col/Fit/Dim",
                                           selectId="Id",
                                           selectKey="style_col_fit_dim",
                                           selectFormat=["style_col_fit_dim"],
                                           exceptSchemaFields=["Company", "Sizes",
                                                               "CreateTimeStamp", "CreateOpId",
                                                               "ModifiedTimeStamp", "ModifiedOpId",
                                                               "versions"],
                                           depth=1))

    # Many2One
    Size_Id = Column(Integer, ForeignKey("SizeBuckets.Id"), nullable=False,
                     info=dict(label="Size",
                               selectId="Id",
                               selectKey="Size",
                               # selectField/selectFieldValue - additional filter
                               selectField="ItemScale_Id",  # SizeBucket.ItemScale_Id
                               selectFieldValue="ItemColourFitDim.ItemProduct.SizeScale.Id",  # field in parentTable - ProductColourFitDims
                               depth=1))
    Size = relationship("SizeBucket",
                        primaryjoin="SizeBucket.Id==ProductSKU.Size_Id")

    # Many2One
    TaxType_Id = Column(Integer, ForeignKey("TaxTypes.Id"), nullable=False,
                        info=dict(label="Tax Type", selectId="Id",
                                  selectKey="Description", depth=1))
    TaxType = relationship("TaxType",
                           primaryjoin="TaxType.Id==ProductSKU.TaxType_Id")

    Status = Column(Enum("Valid", "NotValid", "SoldOut", name="SKU_Status"),
                    nullable=False, default="Valid",
                    info=dict(label="Status"))

    Number = Column(String(30), nullable=True,
                    info=dict(label="Product Number",
                              selectId="Id",
                              selectKey="Number",
                              selectColumn="Number",
                              selectFormat=["Number", "ItemColourFitDim.style_col_fit_dim", "Size.Size"],
                              selectTable="ProductSKUs",
                              ))
    EAN = Column(String(30), nullable=True,
                 info=dict(label="EAN",
                           selectId="Id",
                           selectKey="EAN",
                           selectColumn="EAN",
                           selectFormat=["EAN", "ItemColourFitDim.style_col_fit_dim", "Size.Size"],
                           selectTable="ProductSKUs",
                           ))
    UPC = Column(String(30), nullable=True,
                 info=dict(label="UPC",
                           selectId="Id",
                           selectKey="UPC",
                           selectColumn="UPC",
                           selectFormat=["UPC", "ItemColourFitDim.style_col_fit_dim", "Size.Size"],
                           selectTable="ProductSKUs",
                           ))

    Name = Column(String(128), nullable=True, info=dict(label="Name"))

    # One2Many
    Descriptions = relationship("ProductSKUDescription", uselist=True,
                                backref="ItemSKU",
                                cascade="all, delete-orphan",
                                info=dict(dumpFields=["Id"], depth=1))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==ProductSKU.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==ProductSKU.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    @hybrid_property
    def style_col_fit_dim_size(self):
        if self.ItemColourFitDim.Dimension:
            return self.ItemColourFitDim.ItemProduct.Style + " " + \
                   self.ItemColourFitDim.Colour.Colour + " " + \
                   self.ItemColourFitDim.Fitting.Fitting + " " + \
                   self.ItemColourFitDim.Dimension.Dimension + " " + \
                   self.Size.Size
        elif self.ItemColourFitDim.Fitting:
            return self.ItemColourFitDim.ItemProduct.Style + " " + \
                   self.ItemColourFitDim.Colour.Colour + " " + \
                   self.ItemColourFitDim.Fitting.Fitting + " " + \
                   self.Size.Size
        else:
            return self.ItemColourFitDim.ItemProduct.Style + " " + \
                   self.ItemColourFitDim.Colour.Colour + " " + \
                   self.Size.Size

    @style_col_fit_dim_size.expression
    def style_col_fit_dim_size(cls):
        from .Products import Product
        from .ProductColourFitDims import ProductColourFitDim
        from .Colours import Colour
        from .Fittings import Fitting
        from .Dimensions import Dimension
        from .SizeBuckets import SizeBucket

        # func.coalesce is similar to: Fitting.Fitting if Fitting.Fitting is not None else ""
        return (select([Product.Style + " " +
                       Colour.Colour + " " +
                       func.coalesce(Fitting.Fitting, "") + " " +
                       func.coalesce(Dimension.Dimension, "") + " " +
                       SizeBucket.Size]).
                where(ProductColourFitDim.Id == cls.ItemColourFitDim_Id).
                where(Product.Id == ProductColourFitDim.ItemProduct_Id).
                where(Colour.Id == ProductColourFitDim.Colour_Id).
                where(Fitting.Id == ProductColourFitDim.Fitting_Id).
                where(Dimension.Id == ProductColourFitDim.Dimension_Id).
                where(SizeBucket.Id == cls.Size_Id).
                as_scalar())

    @hybrid_property
    def size(self):
        return self.Size.Size

    @size.expression
    def size(cls):
        from .SizeBuckets import SizeBucket

        return (select([SizeBucket.Size]).
                where(SizeBucket.Id == cls.Size_Id).
                as_scalar())

    # One2Many side of WarehouseLocations
    # uselist=False - this is just used in validate_delete
    Reserved = relationship("WarehouseLocation", uselist=False,
                            back_populates="Reserved",
                            primaryjoin="WarehouseLocation.Reserved_Id==ProductSKU.Id",
                            info=dict(hidden=True, dump=False))

    # One2Many side of StockMovements
    # uselist=False - this is just used in validate_delete
    Movements = relationship("FGStockMovement", uselist=False,
                             back_populates="SKU",
                             primaryjoin="FGStockMovement.SKU_Id==ProductSKU.Id",
                             info=dict(hidden=True, dump=False))

    ContractPrices = relationship("ContractPriceDiscount", uselist=False,
                               back_populates="SKU",
                               primaryjoin="ContractPriceDiscount.SKU_Id==ProductSKU.Id",
                               info=dict(hidden=True, dump=False))


    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data=None):
        is_ok = True
        message = ""
        tables = ""

        if self.Reserved is not None:
            is_ok = False
            tables = "Reserved Warehouse Locations"

        if self.Movements is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Product Stock Movements"

        if self.ContractPrices is not None:
            is_ok = False
            tables = tables + (", " if tables else "") + "Contract Price/Discounts"

        if not is_ok:
            if data is None:
                message = f"Cannot Delete. {tables} linked to this Size: {self.Size.Size}"
            else:
                message = f"Cannot Delete. {tables} linked to this Product SKU"

        return is_ok, message


Index("ProductSKU_Index1", ProductSKU.Company_Id,
      ProductSKU.ItemColourFitDim_Id, ProductSKU.Size_Id, unique=True)
Index("ProductSKU_Index2", ProductSKU.Company_Id, ProductSKU.Number, unique=False)
Index("ProductSKU_Index3", ProductSKU.Company_Id, ProductSKU.EAN, unique=False)
Index("ProductSKU_Index4", ProductSKU.Company_Id, ProductSKU.UPC, unique=False)

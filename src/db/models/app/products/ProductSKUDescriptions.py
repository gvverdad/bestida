from sqlalchemy import (Column, ForeignKey, Integer)

from .ProductDescriptions import ProductDescription


class ProductSKUDescription(ProductDescription):
    __versioned__ = {}
    __tablename__ = "ProductSKUDescriptions"
    __table_args__ = dict(info=dict(label="Size Descriptions",
                                    desc="Descriptions"))

    Id = Column(Integer, ForeignKey("ProductDescriptions.Id"),
                primary_key=True, nullable=False,
                info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "Size"
    }

    # ManyToOne side of ProductSKU
    ItemSKU_Id = Column(Integer, ForeignKey("ProductSKUs.Id"),
                        info=dict(hidden=True,
                                  exceptSchemaFields=["Descriptions",
                                                      "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                      "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                      "versions"],
                                  ))

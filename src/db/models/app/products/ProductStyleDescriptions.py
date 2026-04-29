from sqlalchemy import (Column, ForeignKey, Integer)

from .ProductDescriptions import ProductDescription


class ProductStyleDescription(ProductDescription):
    __versioned__ = {}
    __tablename__ = "ProductStyleDescriptions"
    __table_args__ = dict(info=dict(label="Style Descriptions",
                                    desc="Style Descriptions"))

    Id = Column(Integer, ForeignKey("ProductDescriptions.Id"),
                primary_key=True, nullable=False,
                info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "Style"
    }

    # ManyToOne side of Product
    ItemProduct_Id = Column(Integer, ForeignKey("Products.Id"),
                            info=dict(hidden=True,
                                      exceptSchemaFields=["Descriptions",
                                                          "CreateTimeStamp", "CreateOpId",
                                                          "ModifiedTimeStamp", "ModifiedOpId",
                                                          "versions"],
                                      ))

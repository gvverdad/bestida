from sqlalchemy import (Column, ForeignKey, Integer)

from .ProductDescriptions import ProductDescription


class ProductColourFitDimDescription(ProductDescription):
    __versioned__ = {}
    __tablename__ = "ProductColourFitDimDescriptions"
    __table_args__ = dict(info=dict(label="Colour/Fit/Dimension Descriptions",
                                    desc="Descriptions"))

    Id = Column(Integer, ForeignKey("ProductDescriptions.Id"),
                primary_key=True, nullable=False,
                info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "ColourFitDim"
    }

    # ManyToOne side of ProductColourFitDims
    ItemColourFitDim_Id = Column(Integer, ForeignKey("ProductColourFitDims.Id"),
                                 info=dict(hidden=True,
                                           exceptSchemaFields=["Descriptions",
                                                               "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                               "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                               "versions"],
                                           ))

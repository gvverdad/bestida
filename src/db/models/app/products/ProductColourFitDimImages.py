import os
from sqlalchemy import (Column, ForeignKey, Integer, event)

from .ProductImages import ProductImage


class ProductColourFitDimImage(ProductImage):
    __versioned__ = {}
    __tablename__ = "ProductColourFitDimImages"
    __table_args__ = dict(info=dict(label="Colour/Fit/Dimension Images",
                                    desc="Colour/Fit/Dimension Images",
                                    viewer=dict(type="ImageViewer",
                                                title="Style/Col/Fit/Dim",
                                                title_fields=["ItemColourFitDim.ItemProduct.Style",
                                                              "ItemColourFitDim.Colour.Colour",
                                                              "ItemColourFitDim.Fitting.Fitting",
                                                              "ItemColourFitDim.Dimension.Dimension",
                                                              "ImageType.Type"],
                                                tooltip="View Colour/Fit/Dim Image",
                                                file_field="File"),
                                    loader=dict(type="uploadImage",
                                                file_field="File",
                                                mime_field="MimeType")))

    Id = Column(Integer, ForeignKey("ProductImages.Id"),
                primary_key=True, nullable=False,
                info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "ColourFitDim"
    }

    # ManyToOne side of ProductColourFitDims
    ItemColourFitDim_Id = Column(Integer, ForeignKey("ProductColourFitDims.Id"),
                                 info=dict(hidden=True,
                                           exceptSchemaFields=["Images",
                                                               "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                               "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                               "versions"],
                                           ))

def on_image_delete(mapper, connection, target):
    image_file = getattr(target, "Path", None)

    try:
        os.remove(image_file)
    except:
        pass


event.listen(ProductColourFitDimImage, "before_delete", on_image_delete)  # mapper Event

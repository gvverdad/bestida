import os
from sqlalchemy import (Column, ForeignKey, Integer, event)

from .ProductImages import ProductImage


class ProductStyleImage(ProductImage):
    __versioned__ = {}
    __tablename__ = "ProductStyleImages"
    __table_args__ = dict(info=dict(label="Style Images",
                                    desc="Style Images",
                                    viewer=dict(type="ImageViewer",
                                                title="Style",
                                                title_fields=["ItemProduct.Style",
                                                              "ImageType.Type"],
                                                tooltip="View Style Image",
                                                file_field="File"),
                                    loader=dict(type="uploadImage",
                                                file_field="File",
                                                mime_field="MimeType")))

    Id = Column(Integer, ForeignKey("ProductImages.Id"),
                primary_key=True, nullable=False,
                info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "Style"
    }

    # ManyToOne side of Product
    ItemProduct_Id = Column(Integer, ForeignKey("Products.Id"),
                            info=dict(hidden=True,
                                      exceptSchemaFields=["Images",
                                                          "CreateTimeStamp", "CreateOpId",
                                                          "ModifiedTimeStamp", "ModifiedOpId",
                                                          "versions"],
                                      ))

def on_image_delete(mapper, connection, target):
    image_file = getattr(target, "Path", None)

    try:
        os.remove(image_file)
    except:
        pass


event.listen(ProductStyleImage, "before_delete", on_image_delete)  # mapper Event

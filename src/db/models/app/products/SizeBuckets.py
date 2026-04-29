from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, DateTime, Index, String, Index
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class SizeBucket(Model):
    __versioned__ = {}
    __tablename__ = "SizeBuckets"
    __table_args__ = dict(info=dict(label="Size Buckets",
                                    companyField="Company_Id",
                                    componentOf=dict(table="SizeScales",
                                                     key=["Scale"],
                                                     list=dict(field="Sizes",
                                                               backref="ItemScale")
                                                     ),
                                    stepperTitleFields=[],
                                    keyPaths=["ItemScale_Id", "Bucket"],
                                    key="Size"
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SizeBucket.Company_Id")

    # Many2One side of SizeScale
    ItemScale_Id = Column(Integer, ForeignKey("SizeScales.Id"),
                          info=dict(depth=1))

    Bucket = Column(Integer, nullable=False, info=dict(label="Bucket Number"))

    # Many2One
    #System_Id = Column(Integer, ForeignKey("SizeSystems.Id"), nullable=False,
    #                   info=dict(label="System",
    #                             selectId="Id",
    #                             selectKey="System",
    #                             depth=1))
    #System = relationship("SizeSystem", primaryjoin="SizeSystem.Id==SizeBucket.System_Id")

    Size = Column(String(16), nullable=False, info=dict(label="Size",
                                                        case="uppercase"))

    Seat = Column(Integer, default=0, info=dict(label="Seat"))
    Thigh = Column(Integer, default=0, info=dict(label="Thigh"))
    Waist = Column(Integer, default=0, info=dict(label="Waist"))
    Length = Column(Integer, default=0, info=dict(label="Length"))

    Neck = Column(Integer, default=0, info=dict(label="Neck"))
    Shoulder = Column(Integer, default=0, info=dict(label="Shoulder"))
    Chest = Column(Integer, default=0, info=dict(label="Chest"))

    # Many2One
    UOM_Id = Column(Integer, ForeignKey("UOMs.Id"),
                    info=dict(label="UOM", selectId="Id",
                              selectKey="Description",
                              selectFormat=["UOM", "Description"],
                              requiredIf="Seat > 0 or Thigh > 0 or Waist > 0 or Length > 0 or Neck > 0 or Shoulder > 0 or Chest > 0",
                              depth=1))
    UOM = relationship("UOM", primaryjoin="UOM.Id==SizeBucket.UOM_Id")

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SizeBucket.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SizeBucket.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of ProductSKUs
    # uselist=False - this is just used in validate_delete
    SKUs = relationship("ProductSKU", uselist=False, back_populates="Size",
                        info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.SKUs is not None:
            is_ok = False
            tables = "ProductSKUs"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Size Bucket"

        return is_ok, message


Index("SizeBucket_Index1", SizeBucket.Company_Id,
      SizeBucket.ItemScale_Id, SizeBucket.Bucket,
      SizeBucket.Size, unique=True)
Index("SizeBucket_Index2", SizeBucket.Company_Id,
      SizeBucket.ItemScale_Id, SizeBucket.Size, unique=True)

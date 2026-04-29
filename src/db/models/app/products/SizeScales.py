from datetime import datetime

from sqlalchemy import (Column, ForeignKey, Integer, DateTime, Index, String,
                        func, select)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ...model import Model
from .....security.policy import get_current_uid


class SizeScale(Model):
    __versioned__ = {}
    __tablename__ = "SizeScales"
    __table_args__ = dict(info=dict(label="Size Scales",
                                    companyField="Company_Id",
                                    stepperTitleFields=["Scale","Name"],
                                    keyPaths=["Company_Id"],
                                    key="Scale",
                                    hybrids=[dict(name="number_of_buckets",
                                                  label="Sizes",
                                                  type="Integer",
                                                  sortable=True,
                                                  searchable=True)]
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==SizeScale.Company_Id")

    Scale = Column(String(8), nullable=False, info=dict(label="Scale",
                                                        case="uppercase",
                                                        selectId="Id",
                                                        selectKey="Scale",
                                                        selectColumn="Scale",
                                                        selectFormat=["Scale", "Description"],
                                                        selectTable="SizeScales",
                                                        ))
    Description = Column(String(128), nullable=False,
                         info=dict(label="Description"))

    # One2Many
    Sizes = relationship("SizeBucket", uselist=True, backref="ItemScale",
                         cascade="all, delete-orphan", )

    #SizeSystems = Column(String(64), nullable=True,
    #                     info=dict(label="Size Systems", modifiable=False))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==SizeScale.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==SizeScale.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Products
    # uselist=False - this is just used in validate_delete
    Products = relationship("Product", uselist=False, back_populates="SizeScale",
                            info=dict(hidden=True, dump=False))

    @hybrid_property
    def number_of_buckets(self):
        return len(self.Sizes)

    @number_of_buckets.expression
    def number_of_buckets(cls):
        from .SizeBuckets import SizeBucket

        return (select([func.count()]).
                where(SizeBucket.ItemScale_Id == cls.Id).
                as_scalar())


    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Products is not None:
            is_ok = False
            tables = "Products"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Size Scale"

        return is_ok, message


Index("SizeScale_Index1", SizeScale.Company_Id,
      SizeScale.Scale, unique=True)

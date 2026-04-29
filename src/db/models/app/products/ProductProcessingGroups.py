from sqlalchemy import (Table, Column, ForeignKey, Integer)
from sqlalchemy.orm import relationship

from ...model import Model

product_reporting_groups = Table("product_reporting_group", Model.metadata,
                                 Column("processing_group_id", Integer,
                                        ForeignKey("ProductProcessingGroups.Id")),
                                 Column("group_id", Integer,
                                        ForeignKey("ProductReportingGroups.Id"))
                                 )
product_reporting_groups.__versioned__ = {}  # Mark secondary table for versioning

product_sales_groups = Table("product_sales_group", Model.metadata,
                             Column("processing_group_id", Integer,
                                    ForeignKey("ProductProcessingGroups.Id")),
                             Column("group_id", Integer,
                                    ForeignKey("ProductSalesGroups.Id"))
                             )
product_sales_groups.__versioned__ = {}  # Mark secondary table for versioning

product_allocation_groups = Table("product_allocation_group", Model.metadata,
                                  Column("processing_group_id", Integer,
                                         ForeignKey("ProductProcessingGroups.Id")),
                                  Column("group_id", Integer,
                                         ForeignKey("ProductAllocationGroups.Id"))
                                  )
product_allocation_groups.__versioned__ = {}  # Mark secondary table for versioning

product_picking_groups = Table("product_picking_group", Model.metadata,
                               Column("processing_group_id", Integer,
                                      ForeignKey("ProductProcessingGroups.Id")),
                               Column("group_id", Integer,
                                      ForeignKey("ProductPickingGroups.Id"))
                               )
product_picking_groups.__versioned__ = {}  # Mark secondary table for versioning

product_packing_groups = Table("product_packing_group", Model.metadata,
                               Column("processing_group_id", Integer,
                                      ForeignKey("ProductProcessingGroups.Id")),
                               Column("group_id", Integer,
                                      ForeignKey("ProductPackingGroups.Id"))
                               )
product_packing_groups.__versioned__ = {}  # Mark secondary table for versioning

product_despatch_groups = Table("product_despatch_group", Model.metadata,
                                Column("processing_group_id", Integer,
                                       ForeignKey("ProductProcessingGroups.Id")),
                                Column("group_id", Integer,
                                       ForeignKey("ProductDespatchGroups.Id"))
                                )
product_despatch_groups.__versioned__ = {}  # Mark secondary table for versioning

product_returns_groups = Table("product_returns_group", Model.metadata,
                               Column("processing_group_id", Integer,
                                      ForeignKey("ProductProcessingGroups.Id")),
                               Column("group_id", Integer,
                                      ForeignKey("ProductReturnsGroups.Id"))
                               )
product_returns_groups.__versioned__ = {}  # Mark secondary table for versioning

product_cancel_groups = Table("product_cancel_group", Model.metadata,
                              Column("processing_group_id", Integer,
                                     ForeignKey("ProductProcessingGroups.Id")),
                              Column("group_id", Integer,
                                     ForeignKey("ProductCancelGroups.Id"))
                              )
product_cancel_groups.__versioned__ = {}  # Mark secondary table for versioning

class ProductProcessingGroup(Model):
    __versioned__ = {}
    __tablename__ = "ProductProcessingGroups"
    __table_args__ = dict(info=dict(label="Product Processing Groups"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2Many
    ReportingGroups = relationship("ProductReportingGroup",
                                   secondary=product_reporting_groups,
                                   back_populates="ProcessingGroups",
                                   info=dict(label="Reporting Groups",
                                             nullable=True, depth=1,
                                             selectId="Id",
                                             selectKey="Description",
                                             dumpFields=["Id"]))

    # Many2Many
    SalesGroups = relationship("ProductSalesGroup",
                               secondary=product_sales_groups,
                               back_populates="ProcessingGroups",
                               info=dict(label="Sales Groups",
                                         nullable=True, depth=1,
                                         selectId="Id",
                                         selectKey="Description",
                                         dumpFields=["Id"]))

    # Many2Many
    AllocationGroups = relationship("ProductAllocationGroup",
                                    secondary=product_allocation_groups,
                                    back_populates="ProcessingGroups",
                                    info=dict(label="Allocation Groups",
                                              nullable=True, depth=1,
                                              selectId="Id",
                                              selectKey="Description",
                                              dumpFields=["Id"]))

    # Many2Many
    PickingGroups = relationship("ProductPickingGroup",
                                 secondary=product_picking_groups,
                                 back_populates="ProcessingGroups",
                                 info=dict(label="Picking Groups",
                                           nullable=True, depth=1,
                                           selectId="Id",
                                           selectKey="Description",
                                           dumpFields=["Id"]))

    # Many2Many
    PackingGroups = relationship("ProductPackingGroup",
                                 secondary=product_packing_groups,
                                 back_populates="ProcessingGroups",
                                 info=dict(label="Packing Groups",
                                           nullable=True, depth=1,
                                           selectId="Id",
                                           selectKey="Description",
                                           dumpFields=["Id"]))

    # Many2Many
    DespatchGroups = relationship("ProductDespatchGroup",
                                  secondary=product_despatch_groups,
                                  back_populates="ProcessingGroups",
                                  info=dict(label="Despatch Groups",
                                            nullable=True, depth=1,
                                            selectId="Id",
                                            selectKey="Description",
                                            dumpFields=["Id"]))

    # Many2Many
    ReturnsGroups = relationship("ProductReturnsGroup",
                                 secondary=product_returns_groups,
                                 back_populates="ProcessingGroups",
                                 info=dict(label="Returns Groups",
                                           nullable=True, depth=1,
                                           selectId="Id",
                                           selectKey="Description",
                                           dumpFields=["Id"]))

    # Many2Many
    CancelGroups = relationship("ProductCancelGroup",
                                secondary=product_cancel_groups,
                                back_populates="ProcessingGroups",
                                info=dict(label="Cancel Groups",
                                          nullable=True, depth=1,
                                          selectId="Id",
                                          selectKey="Description",
                                          dumpFields=["Id"]))

    # OneToOne side of Product
    ItemProduct_Id = Column(Integer, ForeignKey("Products.Id"),
                            info=dict(hidden=True))
    ItemProduct = relationship("Product", back_populates="ProcessingGroups",
                               primaryjoin="Product.Id==ProductProcessingGroup.ItemProduct_Id")

from sqlalchemy import (Table, Column, ForeignKey, Integer)
from sqlalchemy.orm import relationship

from ...model import Model

supplier_reporting_groups = Table("supplier_reporting_group", Model.metadata,
                                  Column("Id", Integer, autoincrement=True,
                                         primary_key=True, nullable=False),
                                  Column("processing_group_id", Integer,
                                         ForeignKey("SupplierProcessingGroups.Id")),
                                  Column("group_id", Integer,
                                         ForeignKey("SupplierReportingGroups.Id"))
                                  )
supplier_reporting_groups.__versioned__ = {}  # Mark the secondary table for versioning

supplier_po_groups = Table("supplier_po_group", Model.metadata,
                           Column("Id", Integer, autoincrement=True,
                                  primary_key=True, nullable=False),
                           Column("processing_group_id", Integer,
                                  ForeignKey("SupplierProcessingGroups.Id")),
                           Column("group_id", Integer,
                                  ForeignKey("SupplierPOGroups.Id"))
                           )
supplier_po_groups.__versioned__ = {}  # Mark the secondary table for versioning

supplier_picking_groups = Table("supplier_picking_group", Model.metadata,
                                Column("Id", Integer, autoincrement=True,
                                       primary_key=True, nullable=False),
                                Column("processing_group_id", Integer,
                                       ForeignKey("SupplierProcessingGroups.Id")),
                                Column("group_id", Integer,
                                       ForeignKey("SupplierPickingGroups.Id"))
                                )
supplier_picking_groups.__versioned__ = {}  # Mark the secondary table for versioning

supplier_despatch_groups = Table("supplier_despatch_group", Model.metadata,
                                 Column("Id", Integer, autoincrement=True,
                                        primary_key=True, nullable=False),
                                 Column("processing_group_id", Integer,
                                        ForeignKey("SupplierProcessingGroups.Id")),
                                 Column("group_id", Integer,
                                        ForeignKey("SupplierDespatchGroups.Id"))
                                 )
supplier_despatch_groups.__versioned__ = {}  # Mark the secondary table for versioning

supplier_receipt_groups = Table("supplier_receipt_group", Model.metadata,
                                Column("Id", Integer, autoincrement=True,
                                       primary_key=True, nullable=False),
                                Column("processing_group_id", Integer,
                                       ForeignKey("SupplierProcessingGroups.Id")),
                                Column("group_id", Integer,
                                       ForeignKey("SupplierReceiptGroups.Id"))
                                )
supplier_receipt_groups.__versioned__ = {}  # Mark the secondary table for versioning

supplier_returns_groups = Table("supplier_returns_group", Model.metadata,
                                Column("Id", Integer, autoincrement=True,
                                       primary_key=True, nullable=False),
                                Column("processing_group_id", Integer,
                                       ForeignKey("SupplierProcessingGroups.Id")),
                                Column("group_id", Integer,
                                       ForeignKey("SupplierReturnsGroups.Id"))
                                )
supplier_returns_groups.__versioned__ = {}  # Mark the secondary table for versioning

supplier_cancel_groups = Table("supplier_cancel_group", Model.metadata,
                               Column("Id", Integer, autoincrement=True,
                                      primary_key=True, nullable=False),
                               Column("processing_group_id", Integer,
                                      ForeignKey("SupplierProcessingGroups.Id")),
                               Column("group_id", Integer,
                                      ForeignKey("SupplierCancelGroups.Id"))
                               )
supplier_cancel_groups.__versioned__ = {}  # Mark the secondary table for versioning

supplier_ageing_groups = Table("supplier_ageing_group", Model.metadata,
                               Column("Id", Integer, autoincrement=True,
                                      primary_key=True, nullable=False),
                               Column("processing_group_id", Integer,
                                      ForeignKey("SupplierProcessingGroups.Id")),
                               Column("group_id", Integer,
                                      ForeignKey("SupplierAgeingGroups.Id"))
                               )
supplier_ageing_groups.__versioned__ = {}  # Mark the secondary table for versioning


class SupplierProcessingGroup(Model):

    __tablename__ = "SupplierProcessingGroups"
    __table_args__ = dict(info=dict(label="Supplier Processing Groups",
                                    desc="Processing Groups"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2Many
    ReportingGroups = relationship("SupplierReportingGroup",
                                   secondary=supplier_reporting_groups,
                                   back_populates="ProcessingGroups",
                                   info=dict(label="Reporting Groups",
                                             nullable=True, depth=1,
                                             selectId="Id",
                                             selectKey="Description",
                                             dumpFields=["Id"]))

    # Many2Many
    POGroups = relationship("SupplierPOGroup", secondary=supplier_po_groups,
                            back_populates="ProcessingGroups",
                            info=dict(label="PO Groups",
                                      nullable=True, depth=1,
                                      selectId="Id",
                                      selectKey="Description",
                                      dumpFields=["Id"]))

    # Many2Many
    PickingGroups = relationship("SupplierPickingGroup", secondary=supplier_picking_groups,
                                 back_populates="ProcessingGroups",
                                 info=dict(label="Picking Groups",
                                           nullable=True, depth=1,
                                           selectId="Id",
                                           selectKey="Description",
                                           dumpFields=["Id"]))

    # Many2Many
    DespatchGroups = relationship("SupplierDespatchGroup", secondary=supplier_despatch_groups,
                                  back_populates="ProcessingGroups",
                                  info=dict(label="Despatch Groups",
                                            nullable=True, depth=1,
                                            selectId="Id",
                                            selectKey="Description",
                                            dumpFields=["Id"]))

    # Many2Many
    ReceiptGroups = relationship("SupplierReceiptGroup", secondary=supplier_receipt_groups,
                                 back_populates="ProcessingGroups",
                                 info=dict(label="Receipt Groups",
                                           nullable=True, depth=1,
                                           selectId="Id",
                                           selectKey="Description",
                                           dumpFields=["Id"]))

    # Many2Many
    ReturnsGroups = relationship("SupplierReturnsGroup", secondary=supplier_returns_groups,
                                 back_populates="ProcessingGroups",
                                 info=dict(label="Returns Groups",
                                           nullable=True, depth=1,
                                           selectId="Id",
                                           selectKey="Description",
                                           dumpFields=["Id"]))

    # Many2Many
    CancelGroups = relationship("SupplierCancelGroup", secondary=supplier_cancel_groups,
                                back_populates="ProcessingGroups",
                                info=dict(label="Cancel Groups",
                                          nullable=True, depth=1,
                                          selectId="Id",
                                          selectKey="Description",
                                          dumpFields=["Id"]))

    # Many2Many
    AgeingGroups = relationship("SupplierAgeingGroup", secondary=supplier_ageing_groups,
                                back_populates="ProcessingGroups",
                                info=dict(label="Ageing Groups",
                                          nullable=True, depth=1,
                                          selectId="Id",
                                          selectKey="Description",
                                          dumpFields=["Id"]))

    # OneToOne side of Supplier
    ItemSupplier_Id = Column(Integer, ForeignKey("Suppliers.Id"),
                             info=dict(label="Supplier Id", hidden=True))
    ItemSupplier = relationship("Supplier", back_populates="ProcessingGroups",
                                primaryjoin="Supplier.Id==SupplierProcessingGroup.ItemSupplier_Id")

    # OneToOne side of SupplierStore
    ItemSupplierStore_Id = Column(Integer, ForeignKey("SupplierStores.Id"),
                                  info=dict(label="Supplier Store Id", hidden=True))
    ItemSupplierStore = relationship("SupplierStore", back_populates="ProcessingGroups",
                                     primaryjoin="SupplierStore.Id==SupplierProcessingGroup.ItemSupplierStore_Id")

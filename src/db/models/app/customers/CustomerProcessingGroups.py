from sqlalchemy import (Table, Column, ForeignKey, Integer)
from sqlalchemy.orm import relationship

from ...model import Model

customer_reporting_groups = Table("customer_reporting_group", Model.metadata,
                                  Column("processing_group_id", Integer,
                                         ForeignKey("CustomerProcessingGroups.Id")),
                                  Column("group_id", Integer,
                                         ForeignKey("CustomerReportingGroups.Id"))
                                  )
customer_reporting_groups.__versioned__ = {}  # Mark the secondary table for versioning

customer_sales_groups = Table("customer_sales_group", Model.metadata,
                              Column("processing_group_id", Integer,
                                     ForeignKey("CustomerProcessingGroups.Id")),
                              Column("group_id", Integer,
                                     ForeignKey("CustomerSalesGroups.Id"))
                              )
customer_sales_groups.__versioned__ = {}  # Mark the secondary table for versioning

customer_allocation_groups = Table("customer_allocation_group", Model.metadata,
                                   Column("processing_group_id", Integer,
                                          ForeignKey("CustomerProcessingGroups.Id")),
                                   Column("group_id", Integer,
                                          ForeignKey("CustomerAllocationGroups.Id"))
                                   )
customer_allocation_groups.__versioned__ = {}  # Mark the secondary table for versioning

customer_picking_groups = Table("customer_picking_group", Model.metadata,
                                Column("processing_group_id", Integer,
                                       ForeignKey("CustomerProcessingGroups.Id")),
                                Column("group_id", Integer,
                                       ForeignKey("CustomerPickingGroups.Id"))
                                )
customer_picking_groups.__versioned__ = {}  # Mark the secondary table for versioning

customer_packing_groups = Table("customer_packing_group", Model.metadata,
                                Column("processing_group_id", Integer,
                                       ForeignKey("CustomerProcessingGroups.Id")),
                                Column("group_id", Integer,
                                       ForeignKey("CustomerPackingGroups.Id"))
                                )
customer_packing_groups.__versioned__ = {}  # Mark the secondary table for versioning

customer_despatch_groups = Table("customer_despatch_group", Model.metadata,
                                 Column("processing_group_id", Integer,
                                        ForeignKey("CustomerProcessingGroups.Id")),
                                 Column("group_id", Integer,
                                        ForeignKey("CustomerDespatchGroups.Id"))
                                 )
customer_despatch_groups.__versioned__ = {}  # Mark the secondary table for versioning

customer_returns_groups = Table("customer_returns_group", Model.metadata,
                                Column("processing_group_id", Integer,
                                       ForeignKey("CustomerProcessingGroups.Id")),
                                Column("group_id", Integer,
                                       ForeignKey("CustomerReturnsGroups.Id"))
                                )
customer_returns_groups.__versioned__ = {}  # Mark the secondary table for versioning

customer_cancel_groups = Table("customer_cancel_group", Model.metadata,
                               Column("processing_group_id", Integer,
                                      ForeignKey("CustomerProcessingGroups.Id")),
                               Column("group_id", Integer,
                                      ForeignKey("CustomerCancelGroups.Id"))
                               )
customer_cancel_groups.__versioned__ = {}  # Mark the secondary table for versioning

customer_ageing_groups = Table("customer_ageing_group", Model.metadata,
                               Column("processing_group_id", Integer,
                                      ForeignKey("CustomerProcessingGroups.Id")),
                               Column("group_id", Integer,
                                      ForeignKey("CustomerAgeingGroups.Id"))
                               )
customer_ageing_groups.__versioned__ = {}  # Mark the secondary table for versioning

customer_statement_groups = Table("customer_statement_group", Model.metadata,
                                  Column("processing_group_id", Integer,
                                         ForeignKey("CustomerProcessingGroups.Id")),
                                  Column("group_id", Integer,
                                         ForeignKey("CustomerStatementGroups.Id"))
                                  )
customer_statement_groups.__versioned__ = {}  # Mark the secondary table for versioning


class CustomerProcessingGroup(Model):
    __tablename__ = "CustomerProcessingGroups"
    __table_args__ = dict(info=dict(label="Customer Processing Groups",
                                    desc="Processing Groups"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2Many
    ReportingGroups = relationship("CustomerReportingGroup",
                                   secondary=customer_reporting_groups,
                                   back_populates="ProcessingGroups",
                                   info=dict(label="Reporting Groups",
                                             nullable=True, depth=1,
                                             selectId="Id",
                                             selectKey="Description",
                                             dumpFields=["Id"]))

    # Many2Many
    SalesGroups = relationship("CustomerSalesGroup", secondary=customer_sales_groups,
                               back_populates="ProcessingGroups",
                               info=dict(label="Sales Groups",
                                         nullable=True, depth=1,
                                         selectId="Id",
                                         selectKey="Description",
                                         dumpFields=["Id"]))

    # Many2Many
    AllocationGroups = relationship("CustomerAllocationGroup", secondary=customer_allocation_groups,
                                    back_populates="ProcessingGroups",
                                    info=dict(label="Allocation Groups",
                                              nullable=True, depth=1,
                                              selectId="Id",
                                              selectKey="Description",
                                              dumpFields=["Id"]))

    # Many2Many
    PickingGroups = relationship("CustomerPickingGroup", secondary=customer_picking_groups,
                                 back_populates="ProcessingGroups",
                                 info=dict(label="Picking Groups",
                                           nullable=True, depth=1,
                                           selectId="Id",
                                           selectKey="Description",
                                           dumpFields=["Id"]))

    # Many2Many
    PackingGroups = relationship("CustomerPackingGroup", secondary=customer_packing_groups,
                                 back_populates="ProcessingGroups",
                                 info=dict(label="Packing Groups",
                                           nullable=True, depth=1,
                                           selectId="Id",
                                           selectKey="Description",
                                           dumpFields=["Id"]))

    # Many2Many
    DespatchGroups = relationship("CustomerDespatchGroup", secondary=customer_despatch_groups,
                                  back_populates="ProcessingGroups",
                                  info=dict(label="Despatch Groups",
                                            nullable=True, depth=1,
                                            selectId="Id",
                                            selectKey="Description",
                                            dumpFields=["Id"]))

    # Many2Many
    ReturnsGroups = relationship("CustomerReturnsGroup", secondary=customer_returns_groups,
                                 back_populates="ProcessingGroups",
                                 info=dict(label="Returns Groups",
                                           nullable=True, depth=1,
                                           selectId="Id",
                                           selectKey="Description",
                                           dumpFields=["Id"]))

    # Many2Many
    CancelGroups = relationship("CustomerCancelGroup", secondary=customer_cancel_groups,
                                back_populates="ProcessingGroups",
                                info=dict(label="Cancel Groups",
                                          nullable=True, depth=1,
                                          selectId="Id",
                                          selectKey="Description",
                                          dumpFields=["Id"]))

    # Many2Many
    AgeingGroups = relationship("CustomerAgeingGroup", secondary=customer_ageing_groups,
                                back_populates="ProcessingGroups",
                                info=dict(label="Ageing Groups",
                                          nullable=True, depth=1,
                                          selectId="Id",
                                          selectKey="Description",
                                          dumpFields=["Id"]))

    # Many2Many
    StatementGroups = relationship("CustomerStatementGroup", secondary=customer_statement_groups,
                                   back_populates="ProcessingGroups",
                                   info=dict(label="Statement Groups",
                                             nullable=True, depth=1,
                                             selectId="Id",
                                             selectKey="Description",
                                             dumpFields=["Id"]))

    # OneToOne side of Customer
    ItemCustomer_Id = Column(Integer, ForeignKey("Customers.Id"),
                             info=dict(label="Customer Id", hidden=True))
    ItemCustomer = relationship("Customer", back_populates="ProcessingGroups",
                                primaryjoin="Customer.Id==CustomerProcessingGroup.ItemCustomer_Id")

    # OneToOne side of CustomerStore
    ItemCustomerStore_Id = Column(Integer, ForeignKey("CustomerStores.Id"),
                                  info=dict(label="Customer Id", hidden=True))
    ItemCustomerStore = relationship("CustomerStore", back_populates="ProcessingGroups",
                                     primaryjoin="CustomerStore.Id==CustomerProcessingGroup.ItemCustomerStore_Id")

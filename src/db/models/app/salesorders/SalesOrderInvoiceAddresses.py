from sqlalchemy import Column, ForeignKey, Integer

from ...address.Addresses import Address


class SalesOrderInvoiceAddress(Address):
    __versioned__ = {}
    __tablename__ = "SalesOrderInvoiceAddresses"
    __table_args__ = dict(info=dict(label="Sales Order Invoice Addresses",
                                    desc="Addresses"))
        
    Id = Column(Integer, ForeignKey("Addresses.Id"), primary_key=True,
                nullable=False,
                info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "SalesOrderInvoice"
    }    
                                                  
    # ManyToOne side of SalesOrderInvoice
    ItemSalesOrderInvoice_Id = Column(Integer, ForeignKey("SalesOrderInvoices.Id"),
                              info=dict(hidden=True,
                                        exceptSchemaFields=["Addresses",
                                                            "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                            "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                            "versions"],
                                        ))

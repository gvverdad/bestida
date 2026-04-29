from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...address.Emails import Email


class CustomerWarehouseEmail(Email):
    __versioned__ = {}
    __tablename__ = "CustomerWarehouseEmails"
    __table_args__ = dict(info=dict(label="Customer Warehouse Emails", desc="Emails"))
        
    Id = Column(Integer, ForeignKey("Emails.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CustomerEmailTypes.Id"),
                     nullable=False,
                     info=dict(label="Email Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("CustomerEmailType",
                        primaryjoin="CustomerEmailType.Id==CustomerWarehouseEmail.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "CustomerWarehouse"
    }    

    # ManyToOne side of CustomerWarehouse
    ItemCustomerWarehouse_Id = Column(Integer, ForeignKey("CustomerWarehouses.Id"),
                                      info=dict(hidden=True,
                                                exceptSchemaFields=["Emails",
                                                                    "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                                    "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                                    "versions"],
                                                ))

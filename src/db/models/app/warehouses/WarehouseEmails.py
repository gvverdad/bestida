from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ...address.Emails import Email


class WarehouseEmail(Email):
    __versioned__ = {}
    __tablename__ = "WarehouseEmails"
    __table_args__ = dict(info=dict(label="Warehouse Emails", desc="Emails"))
        
    Id = Column(Integer, ForeignKey("Emails.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("WarehouseEmailTypes.Id"),
                     nullable=False,
                     info=dict(label="Email Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("WarehouseEmailType",
                        primaryjoin="WarehouseEmailType.Id==WarehouseEmail.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Warehouse"
    }    

    # ManyToOne side of Warehouse
    ItemWarehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                              info=dict(hidden=True,
                                        exceptSchemaFields=["Emails",
                                                            "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                            "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                            "versions"],
                                        ))

from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...address.Phones import Phone


class WarehousePhone(Phone):
    __versioned__ = {}
    __tablename__ = "WarehousePhones"
    __table_args__ = dict(info=dict(label="Warehouse Phones",
                                    desc="Phones",
                                    parentTables=[
                                        dict(column="ItemWarehouse",
                                             table="Warehouses")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Phones.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))
    
    # Many2One
    Type_Id = Column(Integer, ForeignKey("WarehousePhoneTypes.Id"),
                     nullable=False,
                     info=dict(label="Phone Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("WarehousePhoneType",
                        primaryjoin="WarehousePhoneType.Id==WarehousePhone.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Warehouse"
    }        
                                              
    # ManyToOne side of Warehouse 
    ItemWarehouse_Id = Column(Integer, ForeignKey("Warehouses.Id"),
                              info=dict(hidden=True,
                                        exceptSchemaFields=["Phones",
                                                            "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                            "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                            "versions"],
                                        ))

Index("WarehousePhone_Index1", WarehousePhone.ItemWarehouse_Id,
      WarehousePhone.Type_Id, unique=True)

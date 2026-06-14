from sqlalchemy import Column, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship

from ...address.Emails import Email


class CustomerEmail(Email):
    __versioned__ = {}
    __tablename__ = "CustomerEmails"
    __table_args__ = dict(info=dict(label="Customer Emails",
                                    desc="Emails",
                                    parentTables=[
                                        dict(column="ItemCustomer",
                                             table="Customers")
                                    ]
                                    ))
        
    Id = Column(Integer, ForeignKey("Emails.Id"), primary_key=True, nullable=False,
                info=dict(hidden=True))

    # Many2One
    Type_Id = Column(Integer, ForeignKey("CustomerEmailTypes.Id"),
                     nullable=False,
                     info=dict(label="Email Type",
                               selectId="Id", selectKey="Description",
                               depth=1))
    Type = relationship("CustomerEmailType",
                        primaryjoin="CustomerEmailType.Id==CustomerEmail.Type_Id")

    __mapper_args__ = {
        "polymorphic_identity": "Customer"
    }    

    # ManyToOne side of Customer 
    ItemCustomer_Id = Column(Integer, ForeignKey("Customers.Id"),
                             info=dict(hidden=True,
                                       exceptSchemaFields=["Emails",
                                                           "CreateTimeStamp", "CreateOpId_Id", "CreateOpId",
                                                           "ModifiedTimeStamp", "ModifiedOpId_Id", "ModifiedOpId",
                                                           "versions"],
                                       ))

Index("CustomerEmail_Index1", CustomerEmail.ItemCustomer_Id,
      CustomerEmail.Type_Id, unique=True)

from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ..model import Model
from ....security.policy import get_current_uid


class PersonGender(Model):
    __versioned__ = {}
    __tablename__ = "PersonGenders"
    __table_args__ = dict(info=dict(label="Gender", companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id"],
                                    key="Gender"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
    
    # Many2One    
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==PersonGender.Company_Id")                                  
        
    Gender = Column(String(16), nullable=False, info=dict(label="Gender",
                                                          case="uppercase",
                                                          selectId="Id",
                                                          selectKey="Gender",
                                                          selectColumn="Gender",
                                                          selectFormat=["Gender", "Description"],
                                                          selectTable="PersonGenders"
                                                          ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==PersonGender.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==PersonGender.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Person
    # uselist=False - this is just used in validate_delete
    Persons = relationship("Person", uselist=False, back_populates="Gender",
                           info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Persons is not None:
            is_ok = False
            tables = "Persons"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Gender"

        return is_ok, message


Index("PersonGender_Index1", PersonGender.Company_Id, PersonGender.Gender, unique=True)

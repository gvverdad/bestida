from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ..model import Model
from ..functions import get_country_choices, get_default_country
from ....security.policy import get_current_uid


class CountryState(Model):
    __versioned__ = {}
    __tablename__ = "CountryStates"
    __table_args__ = dict(info=dict(label="States",
                                    stepperTitleFields=[],
                                    keyPaths=["Country"],
                                    key="StateCode"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    Country = Column(String(2), nullable=False, default=get_default_country,
                     info=dict(label="Country",
                               choices=get_country_choices,         # server getter
                               choices_getter="getCountriesList"))  # client getter

    StateCode = Column(String(16), nullable=False,
                       info=dict(label="State Code", case="uppercase",
                                 selectId="Id",
                                 selectKey="StateCode",
                                 selectColumn="StateCode",
                                 selectFormat=["SateCode", "Name", "Country"],
                                 selectTable="CountryStates"
                                 ))

    Name = Column(String(64), nullable=False,
                  info=dict(label="Name"))
    
    # Many2One        
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==CountryState.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CountryState.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of CountryLocalities
    # uselist=False - this is just used in validate_delete
    Localities = relationship("CountryLocality", uselist=False,
                              back_populates="State",
                              info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Localities is not None:
            is_ok = False
            tables = "Localities"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this State"

        return is_ok, message

    
Index("CountryState_Index1",
      CountryState.Country,
      CountryState.StateCode, unique=True)

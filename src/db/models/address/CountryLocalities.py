from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ..model import Model
from ..functions import get_country_choices, get_default_country
from ....security.policy import get_current_uid


class CountryLocality(Model):
    __versioned__ = {}
    __tablename__ = "CountryLocalities"
    __table_args__ = dict(info=dict(label="Localities",
                                    stepperTitleFields=[],
                                    keyPaths=["Country", "State_Id"],
                                    key="Name"
                                    ))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    Country = Column(String(2), nullable=False, default=get_default_country,
                     info=dict(label="Country",
                               choices=get_country_choices,         # server getter
                               choices_getter="getCountriesList"))  # client getter

    # Many2One    
    State_Id = Column(Integer, ForeignKey("CountryStates.Id"), nullable=False,
                      info=dict(label="State",
                                selectId="Id",
                                selectKey="StateCode",
                                selectFormat=["Country", "StateCode", "Name"],
                                selectCascade=[{"field": "Country", "value": "Country"}],
                                # selectField/selectFieldValue - additional filter
                                selectField="Country",  # CountryLocalities.Country
                                selectFieldValue="Country"  # key in CountryLocalities.Country
                                ))
    State = relationship("CountryState", primaryjoin="CountryState.Id==CountryLocality.State_Id")                                  

    Name = Column(String(64), nullable=False,
                  info=dict(label="Name", case="uppercase",
                            selectId="Id",
                            selectKey="Name",
                            selectColumn="Name",
                            selectFormat=["Name", "State.StateCode", "Country"],
                            selectTable="CountryLocalities"
                            ))
        
    # Many2One        
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==CountryLocality.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CountryLocality.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of CountryPostcodes
    # uselist=False - this is just used in validate_delete
    Postcodes = relationship("CountryPostcode", uselist=False, back_populates="Locality",
                             info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""
        if self.Postcodes is not None:
            is_ok = False
            tables = "Postcodes"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Locality"

        return is_ok, message


Index("CountryLocality_Index1",
      CountryLocality.Country,
      CountryLocality.State_Id, CountryLocality.Name, unique=True)

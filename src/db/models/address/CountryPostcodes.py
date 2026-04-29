from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from ..model import Model
from ..functions import get_country_choices, get_default_country
from ....security.policy import get_current_uid


class CountryPostcode(Model):
    __versioned__ = {}
    __tablename__ = "CountryPostcodes"
    __table_args__ = dict(info=dict(label="Postcodes",
                                    stepperTitleFields=[],
                                    keyPaths=["Country", "State_Id", "Locality_Id"],
                                    key="Postcode"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    Country = Column(String(2), nullable=False, default=get_default_country,
                     info=dict(label="Country",
                               choices=get_country_choices,      # server getter
                               choices_getter="getCountriesList")) # client getter

    # Many2One    
    State_Id = Column(Integer, ForeignKey("CountryStates.Id"), nullable=False,
                      info=dict(label="State",
                                selectTable="CountryStates",  # used for server update
                                selectObject="CountryStates",  # used for client selection list
                                selectId="Id",
                                selectKey="StateCode",
                                selectFormat=["Country", "StateCode", "Name"],
                                selectCascade=[{"field": "Country", "value": "Country"}],
                                # selectField/selectFieldValue - additional filter
                                selectField="Country",  # CountryPostcodes.Country
                                selectFieldValue="Country"  # key in CountryPostcodes.Country
                                ))
    State = relationship("CountryState", primaryjoin="CountryState.Id==CountryPostcode.State_Id")                                  
    # Many2One    
    Locality_Id = Column(Integer, ForeignKey("CountryLocalities.Id"), nullable=False,
                         info=dict(label="Locality",
                                   selectTable="CountryLocalities",  # used for server update
                                   selectObject="CountryLocalities",  # used for client selection list
                                   selectId="Id",
                                   selectKey="Name",
                                   selectFormat=["Country", "State.StateCode", "Name"],
                                   selectCascade=[{"field": "State", "value": "State"},
                                                  {"field": "Country", "value": "Country"}],
                                   # selectField/selectFieldValue - additional filter
                                   selectField="State.Id",  # CountryPostcodes.State.Id
                                   selectFieldValue="State.Id"  # key in CountryPostcodes - State.Id
                                   ))
    Locality = relationship("CountryLocality", primaryjoin="CountryLocality.Id==CountryPostcode.Locality_Id")                                  

    Postcode = Column(String(16), nullable=False,
                      info=dict(label="Postcode",
                                case="uppercase"))
        
    # Many2One        
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==CountryPostcode.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==CountryPostcode.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Address
    # uselist=False - this is just used in validate_delete
    Addresses = relationship("Address", uselist=False, back_populates="Postcode",
                             info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.Addresses is not None:
            is_ok = False
            tables = "Addresses"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Postcode"

        return is_ok, message


Index("CountryPostcode_Index1",
      CountryPostcode.Country, CountryPostcode.State_Id,
      CountryPostcode.Locality_Id, CountryPostcode.Postcode, unique=True)
Index("CountryPostcode_Index2",
      CountryPostcode.Country, CountryPostcode.State_Id,
      CountryPostcode.Locality_Id, unique=False)
Index("CountryPostcode_Index3",
      CountryPostcode.Country, CountryPostcode.State_Id,
      unique=False)
Index("CountryPostcode_Index4",
      CountryPostcode.Country, unique=False)

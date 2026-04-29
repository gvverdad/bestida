from datetime import datetime

from sqlalchemy import (Column, ForeignKey, String, Integer, Numeric, DateTime)
from sqlalchemy.orm import relationship

from ..model import Model
from ..functions import get_country_choices, get_default_country
from ....security.policy import get_current_uid


class Address(Model):
    __versioned__ = {}
    __tablename__ = "Addresses"
    __table_args__ = dict(info=dict(label="Address"))

    Id = Column(Integer, autoincrement=True, primary_key=True,
                nullable=False,
                info=dict(label="Address Id", modifiable=False))

    Line1 = Column(String(64), nullable=False, info=dict(label="Line 1"))
    Line2 = Column(String(64), nullable=True, info=dict(label="Line 2"))
    # Many2One    
    Locality_Id = Column(Integer, ForeignKey("CountryLocalities.Id"), nullable=False,
                         info=dict(label="Locality", depth=1,
                                   selectTable="CountryLocalities",  # used for server update
                                   selectObject="CountryPostcodes",  # used for client selection list
                                   # selectId, selectKey, selectFormat will use selectObject
                                   selectId="Locality.Id",
                                   selectKey="Locality.Name",
                                   selectFormat=["Locality.Name",
                                                 "State.Name",
                                                 "Postcode",
                                                 "Country"],
                                   selectCascade=[{"field": "State", "value": "State"},
                                                  {"field": "Postcode", "value": "."},
                                                  {"field": "Country", "value": "Country"}],
                                   # selectField/selectFieldValue - additional filter
                                   selectField="Country",  # CountryLocalities.Country
                                   selectFieldValue="Country"  # key in CountryLocalities.Country
                                   ))
    Locality = relationship("CountryLocality",
                            primaryjoin="CountryLocality.Id==Address.Locality_Id")

    # Many2One    
    State_Id = Column(Integer, ForeignKey("CountryStates.Id"), nullable=False,
                      info=dict(label="State", depth=1,
                                # if no selectTable or selectObject defined then
                                # client selection list/server update will use join_list[0][2]
                                selectId="Id",
                                selectKey="Name",
                                selectFormat=["StateCode",
                                              "Country"],
                                # selectField/selectFieldValue - additional filter
                                selectField="Country",  # CountryPostcodes.Country
                                selectFieldValue="Country"  # key in CountryPostcodes.Country
                                ))
    State = relationship("CountryState",
                         primaryjoin="CountryState.Id==Address.State_Id")

    # Many2One    
    Postcode_Id = Column(Integer, ForeignKey("CountryPostcodes.Id"), nullable=False,
                         info=dict(label="Postcode", depth=1,
                                   selectId="Id",
                                   selectKey="Postcode",
                                   selectFormat=["Postcode",
                                                 "Locality.Name",
                                                 "State.StateCode",
                                                 "Country"],
                                   # selectField/selectFieldValue - additional filter
                                   selectField="Country",  # CountryPostcodes.Country
                                   selectFieldValue="Country"  # key in CountryPostcodes.Country
                                   ))
    Postcode = relationship("CountryPostcode",
                            primaryjoin="CountryPostcode.Id==Address.Postcode_Id")

    Country = Column(String(2), nullable=False, default=get_default_country,
                     info=dict(label="Country",
                               choices=get_country_choices,         # server getter
                               choices_getter="getCountriesList"))  # frontend getter
    
    Latitude = Column(Numeric(10, 8), default=0, info=dict(label="Latitude"))
    Longtitude = Column(Numeric(11, 8), default=0, info=dict(label="Longtitude"))
    
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Address.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"), 
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Address.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    TypeOfAddress = Column(String(32), info=dict(hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "Base",
        "polymorphic_on": TypeOfAddress
    }

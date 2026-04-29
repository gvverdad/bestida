from datetime import datetime

from sqlalchemy import (Column, ForeignKey, String, Integer, DateTime, Index,
                        Enum, Numeric)
from sqlalchemy.orm import relationship

from ...model import Model
from .....security.policy import get_current_uid


class TradingTerm(Model):
    __versioned__ = {}
    __tablename__ = "TradingTerms"
    __table_args__ = dict(info=dict(label="Trading Terms",
                                    companyField="Company_Id"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company", primaryjoin="Company.Id==TradingTerm.Company_Id")

    Type = Column(String(32), nullable=False, info=dict(label="Type",
                                                        case="uppercase",
                                                        selectId="Id",
                                                        selectKey="Type",
                                                        selectColumn="Type",
                                                        selectFormat=["Type", "Description"],
                                                        selectTable="TradingTerms"
                                                        ))
    Description = Column(String(128), nullable=False, info=dict(label="Description"))

    TermsType = Column(Enum("DAYS", "NETEOM", "EOM", "PROX", "COD", "PIA",
                               name="TradingTerms_TermsType"), nullable=False,
                       info=dict(label="Terms Type",
                                 actionOn="{" +
                                          "\"baseFieldName\": \"TermsType\"," +
                                          "\"DAYS\": {\"onFields\":[\"Days\", \"Period1Discount\", \"Period1Days\", \"Period2Discount\", \"Period2Days\", \"Period3Discount\", \"Period3Days\"]," +
                                                     "\"offFields\":[]}," +
                                          "\"NETEOM\": {\"onFields\":[\"Days\", \"Period1Discount\", \"Period1Days\", \"Period2Discount\", \"Period2Days\", \"Period3Discount\", \"Period3Days\"]," +
                                                     "\"offFields\":[]}," +
                                          "\"PROX\": {\"onFields\":[\"Days\", \"Period1Discount\", \"Period1Days\", \"Period2Discount\", \"Period2Days\", \"Period3Discount\", \"Period3Days\"]," +
                                                     "\"offFields\":[]}," +
                                          "\"EOM\": {\"onFields\":[\"Period1Discount\", \"Period1Days\", \"Period2Discount\", \"Period2Days\", \"Period3Discount\", \"Period3Days\"]," +
                                                    "\"offFields\":[\"Days\"]}," +
                                          "\"COD\": {\"onFields\":[]," +
                                                "\"offFields\":[\"Days\", \"Period1Discount\", \"Period1Days\", \"Period2Discount\", \"Period2Days\", \"Period3Discount\", \"Period3Days\"]}," +
                                          "\"PIA\": {\"onFields\":[]," +
                                              "\"offFields\":[\"Days\", \"Period1Discount\", \"Period1Days\", \"Period2Discount\", \"Period2Days\", \"Period3Discount\", \"Period3Days\"]}" +
                                          "}"
                                 ))

    Days = Column(Integer, info=dict(label="Days",
                                          requiredIf="TermsType in (\"DAYS\",\"NETEOM\", \"PROX\")"
                                     ))

    Period1Discount = Column(Numeric(10, 6),
                      info=dict(label="Period 1 Early Payment Discount%",
                                numberType="percent",  # number, currency, percent, string
                                validator=["ZeroPositive"]))
    Period1Days = Column(Integer, info=dict(label="Period 1 Early Payment Days",
                                          requiredIf="Period1Discount > 0"
                                     ))

    Period2Discount = Column(Numeric(10, 6),
                      info=dict(label="Period 2 Early Payment Discount%",
                                numberType="percent",  # number, currency, percent, string
                                validator=["ZeroPositive"]))
    Period2Days = Column(Integer, info=dict(label="Period 2 Early Payment Days",
                                          requiredIf="Period2Discount > 0"
                                     ))

    Period3Discount = Column(Numeric(10, 6),
                      info=dict(label="Period 3 Early Payment Discount%",
                                numberType="percent",  # number, currency, percent, string
                                validator=["ZeroPositive"]))
    Period3Days = Column(Integer, info=dict(label="Period 3 Early Payment Days",
                                          requiredIf="Period3Discount > 0"
                                     ))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid, info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==TradingTerm.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    # Many2One
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid, info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==TradingTerm.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of Accounts
    # uselist=False - this is just used in validate_delete
    CustomerAccounts = relationship("CustomerAccount", uselist=False,
                                    back_populates="TradingTerms",
                                    info=dict(hidden=True, dump=False))

    SupplierAccounts = relationship("SupplierAccount", uselist=False,
                                    back_populates="TradingTerms",
                                    info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.CustomerAccounts is not None:
            is_ok = False
            tables = "Customer Accounts"

        if self.SupplierAccounts is not None:
            is_ok = False
            tables += (", " if tables != "" else "") + "Supplier Accounts"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Trading TradingTerm"

        return is_ok, message


Index("TradingTerm_Index1", TradingTerm.Company_Id, TradingTerm.Type, unique=True)

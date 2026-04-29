# coding=utf-8
from datetime import datetime
import hashlib

from sqlalchemy import (Column, ForeignKey, String, Integer, DateTime, Date)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from ..model import Model
from ....security.policy import get_current_uid
from ....config import config


class Person(Model):
    __versioned__ = {}
    __tablename__ = "Persons"
    __table_args__ = dict(info=dict(label="Person"))

    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
        
    # Many2One            
    Title_Id = Column(Integer, ForeignKey("PersonTitles.Id"), nullable=False,
                      info=dict(label="Title", selectId="Id",
                                selectKey="Description",
                                depth=1))
    Title = relationship("PersonTitle",
                         primaryjoin="PersonTitle.Id==Person.Title_Id")

    FirstName = Column(String(128), info=dict(label="First Name"))
    MiddleName = Column(String(128), info=dict(label="Middle Name"))
    LastName = Column(String(128), nullable=False, info=dict(label="Last Name"))

    Decorations = Column(String(16), info=dict(label="Decorations"))

    # Many2One    
    Gender_Id = Column(Integer, ForeignKey("PersonGenders.Id"), nullable=False,
                       info=dict(label="Gender", selectId="Id",
                                 selectKey="Description", depth=1))
    Gender = relationship("PersonGender",
                          primaryjoin="PersonGender.Id==Person.Gender_Id")
    
    Birthday = Column(Date(), info=dict(label="Birthday"))

    GravatarId = Column(String(128), info=dict(label="Gravatar Id"))
    
    # One2Many    
    Addresses = relationship("PersonAddress", uselist=True, backref="ItemPerson",
                             cascade="all, delete-orphan",
                             info=dict(label="Addresses", depth=1,
                                       dumpFields=["Id"]))

    # One2Many    
    Phones = relationship("PersonPhone", uselist=True, backref="ItemPerson",
                          cascade="all, delete-orphan",
                          info=dict(label="Phones", depth=1,
                                    dumpFields=["Id"]))

    # One2Many    
    Emails = relationship("PersonEmail", uselist=True, backref="ItemPerson",
                          cascade="all, delete-orphan",
                          info=dict(label="Emails", depth=1,
                                    dumpFields=["Id"]))
                                            
    # Many2One    
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User",
                              primaryjoin="User.Id==Person.CreateOpId_Id")
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp",
                                       modifiable=False))
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Person.CreateOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp",
                                         modifiable=False))

    @hybrid_property
    def first_middle_last_name(self):
        return f"{self.FirstName if self.FirstName else ''} {self.MiddleName if self.MiddleName else ''} {self.LastName}"

    @first_middle_last_name.expression
    def first_middle_last_name(cls):
        return f"{cls.FirstName if cls.FirstName else ''} {cls.MiddleName if cls.MiddleName else ''} {cls.LastName}"

    @hybrid_property
    def first_last_name(self):
        return f"{self.FirstName if self.FirstName else ''} {self.LastName}"

    @first_last_name.expression
    def first_last_name(cls):
        return f"{cls.FirstName if cls.FirstName else ''} {cls.LastName}"

    @hybrid_property
    def last_first_name(self):
        return f"{self.LastName} {self.FirstName if self.FirstName else ''}"

    @last_first_name.expression
    def last_first_name(cls):
        return f"{cls.LastName} {cls.FirstName if cls.FirstName else ''}"


    TypeOfPerson = Column(String(32), info=dict(label="Record Type",
                                                hidden=True))

    __mapper_args__ = {
        "polymorphic_identity": "Base",
        "polymorphic_on": TypeOfPerson,
    }

    def gravatar(self):
        url = config["gravatar"]["url"]
        size = config["gravatar"]["size"]
        default = config["gravatar"]["default"]
        rating = config["gravatar"]["rating"]

        try:
            email = self.GravatarId or "gvv@gvvemailserver.com.au"
        except:
            email = "gvv@gvvemailserver.com.au"
        _hash = hashlib.md5(email.encode("utf-8")).hexdigest()

        """
            s   Imagesize, in pixels.
            r   Image rating.Options are "g", "pg", "r", and "x".
            d   The default image generator for users who have no avatars registered with the
                Gravatar service. Options are "404"to return a 404 error, a URL that points to a default
                image, or one of the following image generators:
                "mp", "identicon", "monsterid", "wavatar", "retro", or "blank".
            fd  Force the use of default avatars.
        """
        return "{url}/{hash}?s={size}&d={default}&r={rating}". \
            format(url=url, hash=_hash, size=size, default=default,
                   rating=rating)

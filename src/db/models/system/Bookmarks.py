from datetime import datetime

from sqlalchemy import event
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from ..model import Model
from ... import sqa
from ....security.policy import get_current_uid


class Bookmark(Model):
    __tablename__ = "Bookmarks"
    __table_args__ = dict(info=dict(label="Bookmarks", companyField="Company_Id",
                                    stepperTitleFields=[],
                                    keyPaths=["Company_Id", "User_Id"],
                                    key="Program_Id"))
    
    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    # Many2One
    Company_Id = Column(Integer, ForeignKey("Companies.Id"), nullable=False,
                        info=dict(label="Company", modifiable=False))
    Company = relationship("Company",
                           primaryjoin="Company.Id==Bookmark.Company_Id")

    # Many2One
    User_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                     default=get_current_uid,
                     info=dict(label="User",  selectId="Id", selectKey="UserId",
                               modifiable=False))
    User = relationship("User", primaryjoin="User.Id==Bookmark.User_Id") 
            
    # One2One
    Program_Id = Column(Integer, ForeignKey("Programs.Id"), nullable=False,
                        info=dict(label="Program", selectId="Id", selectKey="Name",
                                  modifiable=False))
    Program = relationship("Program", primaryjoin="Program.Id==Bookmark.Program_Id",
                           cascade="all,delete,delete-orphan",
                           single_parent=True,
                           back_populates="Bookmarks")
        
    URL = Column(String(2048), info=dict(label="Url", modifiable=False))
            
    Desc = Column(String(128), nullable=False, info=dict(label="Name"))

    HomePage = Column(Boolean, default=False,
                      info=dict(label="Home Page",
                                actionOn="{" +
                                      "\"baseFieldName\": \"HomePage\"," +
                                      "\"true\": {\"onFields\":[\"HomePageSequence\"],\"offFields\":[]}," +
                                      "\"false\": {\"onFields\": [], \"offFields\": [\"HomePageSequence\"]}," +
                                      "}"
                                ))
    HomePageSequence = Column(Integer, default=0,
                              info=dict(label="Home Page Sequence",
                                        requiredIf="HomePage == true"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Bookmark.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Bookmark.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))


Index("Bookmark_Index1", Bookmark.Company_Id, Bookmark.User_Id, Bookmark.Program_Id, unique=True)
Index("Bookmark_Index2", Bookmark.Company_Id, Bookmark.User_Id, Bookmark.Program_Id,
      Bookmark.HomePage, Bookmark.HomePageSequence, unique=False)


def on_bookmark_insert(mapper, connection, target):
    home_page = getattr(target, "HomePage")
    home_page_seq = getattr(target, "HomePageSequence")

    if home_page and (home_page_seq == 0 or home_page_seq is None):
        coy_id = getattr(target, "Company_Id")
        user_id = getattr(target, "User_Id")

        next_seq = 1
        db_session = Session.object_session(target)
        record = db_session.query(sqa.get_model("Bookmarks")). \
            filter(sqa.where(f"Company_Id = {coy_id} and User_Id = {user_id} and HomePage = True")). \
            order_by(sqa.sort_desc("Bookmarks", "HomePageSequence")).first()
        if record is not None:
            next_seq = record.HomePageSequence + 1
        setattr(target, "HomePageSequence", next_seq)


event.listen(Bookmark, "before_insert", on_bookmark_insert)  # mapper Event
# Bookmark delete will cascade-delete Program, Program will cascade-delete ProgramStates

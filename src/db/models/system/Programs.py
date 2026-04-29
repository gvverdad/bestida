from datetime import datetime

from sqlalchemy import event, select, case
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Text, Enum, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import func

from ..model import Model
from ..functions import get_tables_choices
from ... import sqa
from ....security.policy import get_current_uid
from ..security.Menus import MenuItemAction

PROGRAM_SYS_MENU = ["/profile", "/bookmarks", "/notifications", "/setlocale",
                    "/settimezone", "/changepassword", "/changecompany",
                    "/jobqueues", "/spooler", "/launcher", "/logout"]


class Program(Model):
    __versioned__ = {}
    __tablename__ = "Programs"
    __table_args__ = dict(info=dict(label="Programs",
                                    stepperTitleFields=[],
                                    keyPaths=["Program"],
                                    key="Type"))
    
    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))
            
    Program = Column(String(1024), nullable=False,
                     info=dict(label="Program",
                               selectId="Id",
                               selectKey="Program",
                               selectColumn="Program",
                               selectFormat=["Program", "Type", "Name"],
                               selectTable="Programs"
                               ))
    Name = Column(String(128), nullable=False, info=dict(label="Name"))

    Type = Column(Enum("Grid", "Form", "Script", "Document", name="ProgramType"),
                  nullable=False, default="Grid",
                  info=dict(label="Program Type",
                            actionOn="{" +
                                     "\"baseFieldName\": \"Type\"," +
                                     "\"Grid\": {\"onFields\":[\"Table\",\"GridDepth\",\"GridSchema\", \"Override\", \"URL\"],\"offFields\":[\"FormDepth\",\"FormSchema\", \"Path\", \"Component\", \"Template\"]}," +
                                     "\"Form\": {\"onFields\": [\"Table\",\"FormDepth\",\"FormSchema\", \"Override\", \"URL\"], \"offFields\": [\"GridDepth\",\"GridSchema\", \"Path\", \"Component\", \"Template\"]}," +
                                     "\"Script\": {\"onFields\": [\"URL\", \"Path\", \"Component\", \"Template\", \"Override\"], \"offFields\": [\"Table\",\"GridDepth\",\"GridSchema\",\"FormDepth\",\"FormSchema\"]}," +
                                     "\"Document\": {\"onFields\": [\"Path\", \"Component\"], \"offFields\": [\"Table\",\"GridDepth\",\"GridSchema\",\"FormDepth\",\"FormSchema\", \"URL\", \"Template\", \"Override\"]}" +
                                     "}"
                            ))

    RunLevel = Column(Integer, default=0,
                      info=dict(label="Run Level", min="0", max="999999"))
    CreateLevel = Column(Integer, default=0,
                         info=dict(label="Create Level", min="0", max="999999"))
    UpdateLevel = Column(Integer, default=0,
                         info=dict(label="Update Level", min="0", max="999999"))
    DeleteLevel = Column(Integer, default=0,
                         info=dict(label="Delete Level", min="0", max="999999"))

    Override = Column(Boolean, default=False,
                      info=dict(label="Override Auto URL Generation"))

    URL = Column(String(2048), info=dict(label="Url",
                                         requiredIf="Override == true"))

    # Max Postgres Table Name is 63
    Table = Column(String(63), info=dict(label="Table",
                                         choices=get_tables_choices,  # server getter
                                         choices_getter="getTablesList",  # client getter
                                         requiredIf="Type in (\"Grid\",\"Form\")"
                                         ))

    Path = Column(String(4096), nullable=True,
                  info=dict(label="Component Path"))
    Component = Column(String(256),
                       info=dict(label="Component", requiredIf="Path !== \"\""))

    Template = Column(String(4096), nullable=True,
                  info=dict(label="Template", requiredIf="Type == \"Script\" && Path == \"\""))

    GridDepth = Column(Integer, default=1, info=dict(label="Grid Depth",
                                                     requiredIf="Type == \"Grid\""
                                                     ))
    FormDepth = Column(Integer, default=1, info=dict(label="Form Depth",
                                                     requiredIf="Type == \"Form\""
                                                     ))
    
    GridSchema = Column(Text, info=dict(label="Grid Schema"))
    FormSchema = Column(Text, info=dict(label="Form Schema"))           

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Program.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp", modifiable=False))
    
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Program.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp", modifiable=False))

    # One2Many side of MenuItemAction
    Menus = relationship("MenuItemAction", uselist=True,
                         back_populates="Program",
                         info=dict(hidden=True, dump=False))

    # One2One side of Bookmark
    Bookmarks = relationship("Bookmark", uselist=True,
                             back_populates="Program",
                             info=dict(hidden=True, dump=False))

    # One2Many side of ProgramState
    ProgramStates = relationship("ProgramState", uselist=True,
                                 back_populates="Program",
                                 cascade="all,delete-orphan",
                                 info=dict(hidden=True, dump=False))

    # One2Many side of RuleSet
    Rulesets = relationship("Ruleset", uselist=True,
                            back_populates="Program",
                            info=dict(hidden=True, dump=False))

    # calculated columns    
    @hybrid_property
    def is_bookmarked(self):
        return len(self.Bookmarks) > 0

    @hybrid_property
    def menu_count(self):
        return len(self.Menus)

    @menu_count.expression
    def menu_count(cls):
        return select([func.count(MenuItemAction.Id)]).\
            where(MenuItemAction.Program_Id == cls.Id).\
            as_scalar()

    @hybrid_property
    def in_sysmenu(self):
        return self.URL in PROGRAM_SYS_MENU

    @hybrid_property
    def is_runnable(self):
        can_run = self.in_sysmenu
        if not can_run:
            can_run = self.menu_count > 0
        return can_run

    @is_runnable.expression
    def is_runnable(cls):
        return case(
            {
                "/profile": True,
                "/bookmarks": True,
                "/notifications": True,
                "/setlocale": True,
                "/settimezone": True,
                "/changepassword": True,
                "/changecompany": True,
                "/jobqueues": True,
                "/spooler": True,
                "/launcher": True,
                "/logout": True
            },
            value=cls.URL,
            else_=cls.menu_count > 0
        )

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        if self.in_sysmenu:
            is_ok = False
            tables = "SystemMenu"
        if len(self.Menus) > 0:
            is_ok = False
            tables = tables + (", " if tables else "") + "MenuItems"
        if len(self.Bookmarks) > 0:
            is_ok = False
            tables = tables + (", " if tables else "") + "Bookmark"
        if len(self.Rulesets) > 0:
            is_ok = False
            tables = tables + (", " if tables else "") + "Rulesets"
        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Program"

        return is_ok, message


Index("Program_Index1", Program.Program, Program.Type, unique=True)


def on_program_update(mapper, connection, target):
    program_type = getattr(target, "Type")
    override = getattr(target, "Override")
    program = getattr(target, "Program")
    if not override:
        if program_type == "Form":
            setattr(target, "URL", "/form/" + program)
        elif program_type == "Grid":
            setattr(target, "URL", "/grid/" + program)
        elif program_type == "Script":
            setattr(target, "URL", "/script/" + program)
            setattr(target, "Table", None)


def on_program_delete(mapper, connection, target):
    program = getattr(target, "Program")
    db_session = object_session(target)

    if target.Type == "Grid":
        form = db_session.query(sqa.get_model("Programs")).with_for_update(). \
            filter(sqa.where("Program = \"{}\" and Type = \"Form\"".format(program))).first()
        if form:
            db_session.delete(form)

    progs = db_session.query(sqa.get_model("Programs")).with_for_update().\
        filter(sqa.where("Program startswith (\"{}.\")".format(program))).all()
    for p in progs:
        db_session.delete(p)


event.listen(Program, "before_update", on_program_update)  # Mapper Event
event.listen(Program, "before_insert", on_program_update)  # mapper Event
event.listen(Program, "before_delete", on_program_delete)  # Mapper Event
# Program will cascade-delete ProgramStates

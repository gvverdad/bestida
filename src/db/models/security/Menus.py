import logging
from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from ..model import Model
from ... import sqa
from ....security.policy import get_current_uid

log = logging.getLogger(__name__)


class Menu(Model):
    __versioned__ = {}
    __tablename__ = "Menus"
    __table_args__ = dict(info=dict(label="Menu", key="MenuId"))
    
    Id = Column(Integer, autoincrement=True, primary_key=True, nullable=False,
                info=dict(label="Id", modifiable=False))

    MenuId = Column(String(64), index=True, unique=True, nullable=False,
                    info=dict(label="Menu Id", case="uppercase",
                              selectId="Id",
                              selectKey="MenuId",
                              selectColumn="MenuId",
                              selectFormat=["MenuId", "Name"],
                              selectTable="Menus"
                              ))
    Name = Column(String(128), nullable=False, info=dict(label="Name"))

    # One2Many    
    Items = relationship("MenuItem", uselist=True, cascade="all, delete-orphan",
                         order_by="MenuItem.Line", backref="ItemMenu")
                                      
    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==Menu.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime, default=datetime.utcnow,
                             info=dict(label="Created Timestamp",
                                       modifiable=False))
    
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==Menu.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime, onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp",
                                         modifiable=False))

    # One2Many side of User
    # uselist=False - this is just used in validate_delete
    Roles = relationship("Role", uselist=False, back_populates="StartMenu",
                         primaryjoin="Menu.Id==Role.StartMenu_Id",
                         info=dict(hidden=True, dump=False))

    def validate_delete(self, user_rowid, company_rowid, locale, timezone, data):
        is_ok = True
        message = "OK"
        tables = ""

        # TODO: validate if Menu is a MenuItem of another Menu
        if self.Roles is not None:
            is_ok = False
            tables = "Roles"

        if not is_ok:
            message = f"Cannot Delete. {tables} linked to this Menu"

        return is_ok, message

    def walk_menu(self, user, level):
        items = list()
        for item in self.Items:
            try:
                record = dict()
                if isinstance(item, MenuItemAction) and \
                        user.Role.RunLevel >= item.Program.RunLevel:
                    record["type"] = "Action"
                    record["level"] = str(level)
                    record["url"] = item.Program.URL
                    if item.Desc:
                        record["title"] = item.Desc
                    else:
                        record["title"] = item.Program.Name
                elif isinstance(item, MenuItemMenu):
                    record["type"] = "Menu"
                    record["level"] = str(level)
                    if item.Desc:
                        record["title"] = item.Desc
                    else:
                        record["title"] = item.Menu.Name
                    record["items"] = item.Menu.walk_menu(user, level+1)
                else:
                    continue

                items.append(record)
            except:
                pass

        return items

    def dump_items(self):
        items = list()
        for item in self.Items:
            record = dict()
            record["Line"] = item.Line
            record["Desc"] = item.Desc
            if isinstance(item, MenuItemAction):
                record["Type"] = "Action"
                record["Program"] = item.Program.Program
                record["ProgramType"] = item.Program.Type
                record["ProgramName"] = item.Program.Name
            else:
                record["Type"] = "Menu"
                record["MenuId"] = item.Menu.MenuId
                record["MenuName"] = item.Menu.Name
                record["MenuItems"] = item.Menu.dump_items()

            items.append(record)

        return items


def next_menu_item_line(context):
    line = 0
    if context:
        db_session = Session.object_session(context)
        if context.__tablename__ == "Menus":
            last_rec = db_session.query(sqa.get_model("MenuItems")).\
                       filter(sqa.where("ItemMenu_Id = %d" % context.Id)).\
                       order_by(sqa.sort_desc("MenuItems", "ItemMenu_Id")).first()
        else:  # MenuItems
            last_rec = db_session.query(sqa.get_model("MenuItems")).\
                       filter(sqa.where("ItemMenu_Id = %d" % context.ItemMenu_Id)).\
                       order_by(sqa.sort_desc("MenuItems", "ItemMenu_Id")).first()
        if last_rec is not None:
            line = last_rec.Line
    return line + 10


class MenuItem(Model):
    __versioned__ = {}
    __tablename__ = "MenuItems"
    __table_args__ = dict(info=dict(label="Menu Items"))
    
    Id = Column(Integer, primary_key=True, nullable=False,
                info=dict(label="MenuItem Id", modifiable=False))
    
    # ManyToOne side of Menu 
    ItemMenu_Id = Column(Integer, ForeignKey("Menus.Id"),
                         info=dict(label="Menu", modifiable=False))

    Line = Column(Integer, nullable=False, default=next_menu_item_line,
                  info=dict(label="Line"))

    Desc = Column(String(128), info=dict(label="Description"))

    # Many2One
    CreateOpId_Id = Column(Integer, ForeignKey("Users.Id"), nullable=False,
                           default=get_current_uid,
                           info=dict(label="Created By", modifiable=False))
    CreateOpId = relationship("User", primaryjoin="User.Id==MenuItem.CreateOpId_Id")                                  
    CreateTimeStamp = Column(DateTime(), default=datetime.utcnow,
                             info=dict(label="Created Timestamp",
                                       modifiable=False))
    
    # Many2One    
    ModifiedOpId_Id = Column(Integer, ForeignKey("Users.Id"),
                             onupdate=get_current_uid,
                             info=dict(label="Modified By", modifiable=False))
    ModifiedOpId = relationship("User", primaryjoin="User.Id==MenuItem.ModifiedOpId_Id")
    ModifiedTimeStamp = Column(DateTime(), onupdate=datetime.utcnow,
                               info=dict(label="Modified Timestamp",
                                         modifiable=False))
    
    TypeOfMenuItem = Column(String(32), nullable=False, default="Menu",
                            info=dict(label="Item Type"))

    __mapper_args__ = {
        "polymorphic_identity": "Base",
        "polymorphic_on": TypeOfMenuItem,
        "with_polymorphic": "*"
    }    


Index("MenuItem_Index1", MenuItem.ItemMenu_Id, MenuItem.Line, unique=True)


class MenuItemMenu(MenuItem):
    __versioned__ = {}
    __tablename__ = "MenuItemMenus"
    __table_args__ = dict(info=dict(label="Menu Item Menu"))                  
         
    Id = Column(Integer, ForeignKey("MenuItems.Id"),
                primary_key=True,
                info=dict(hidden=True))

    __mapper_args__ = {"polymorphic_identity": "Menu"}    

    # ManyToOne
    Menu_Id = Column(Integer, ForeignKey("Menus.Id"), nullable=False,
                     info=dict(label="Menu", selectId="Id",
                               selectKey="Name",
                               requiredIf="TypeOfMenuItem = \"Menu\"",
                               selectFormat=["Name", "MenuId"],
                               depth=1))
    Menu = relationship("Menu", primaryjoin="Menu.Id==MenuItemMenu.Menu_Id")

    # TODO: Menu validation - recursive and self - cyclic test
    # validate this menu is not defined in children menu and menuitems


class MenuItemAction(MenuItem):
    __versioned__ = {}
    __tablename__ = "MenuItemActions"
    __table_args__ = dict(info=dict(label="Menu Item Action"))                  
        
    Id = Column(Integer, ForeignKey("MenuItems.Id"),
                primary_key=True, info=dict(hidden=True))

    __mapper_args__ = {"polymorphic_identity": "Action"}    

    # Many2One
    Program_Id = Column(Integer, ForeignKey("Programs.Id"), nullable=False,
                        info=dict(label="Program", selectId="Id",
                                  selectKey="Name",
                                  requiredIf="TypeOfMenuItem = \"Action\"",
                                  selectFormat=["Name","Type","Program","Table","URL"],
                                  depth=1))
    Program = relationship("Program", primaryjoin="Program.Id==MenuItemAction.Program_Id")

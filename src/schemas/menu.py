import logging, sys
from typing import List

from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..db import sqa
from ..db.models.security.Users import User
from ..db.models.security.Menus import Menu, MenuItemAction, MenuItemMenu


log = logging.getLogger(__name__)


class MenuModel(BaseModel):
    type: str
    url: str = None
    title: str
    id: str = None


class MainMenu(MenuModel):
    level: int = 1
    items: List['MainMenu'] = None


# https://pydantic-docs.helpmanual.io/usage/postponed_annotations/#self-referencing-models
MainMenu.update_forward_refs()


class BookmarkMenu(MenuModel):
    program: str
    program_type: str
    level: int = 1
    home_page: bool = False
    home_page_seq: int = 0


def walk_menu(menu: Menu, user: User,
              menu_id: int, level: int = 1) -> List[MainMenu]:
    items = list()
    for item in menu.Items:
        try:
            if isinstance(item, MenuItemAction):
                if user.Role.RunLevel >= item.Program.RunLevel:
                    record = MainMenu(type="Action", level=level,
                                      url=item.Program.URL,
                                      title=item.Desc if item.Desc else item.Program.Name)
                    items.append(record)
            elif isinstance(item, MenuItemMenu):
                record = MainMenu(type="Menu", level=level,
                                  id=str(menu_id) + str(item.Id),
                                  title=item.Desc if item.Desc else item.Menu.Name,
                                  items=walk_menu(item.Menu, user,
                                                  str(menu_id) + str(item.Id),
                                                  level+1))
                items.append(record)
        except:
            log.exception("schemas/menu/walk_menu exception", sys.exc_info()[0])
            pass

    return items


def walk_bookmarks(session: Session, user: User) -> List[BookmarkMenu]:
    bookmarks = (session.query(sqa.get_model("Bookmarks")).
                 filter(sqa.where(f"Company_Id = {user.Company_Id} and User_Id = {user.Id} "
                                  f"and Bookmarks.HomePage = False")).
                 order_by(sqa.sort_asc("Bookmarks", "Id")).
                 all())

    items = list()
    for b in bookmarks:
        items.append(BookmarkMenu(type="Action", url=b.URL, title=b.Desc,
                                  program=b.Program.Program,
                                  program_type=b.Program.Type,
                                  home_page=b.HomePage,
                                  home_page_seq=b.HomePageSequence))
    return items


def walk_programs(menu: Menu, user: User) -> List:
    items = list()
    for item in menu.Items:
        try:
            if isinstance(item, MenuItemAction):
                if user.Role.RunLevel >= item.Program.RunLevel:
                    if not any(item.Program.URL in kv for kv in items):
                        items.append((item.Program.URL, item.Program.Name))
            else:
                progs = walk_programs(item.Menu, user)
                for pro in progs:
                    if not any(pro[0] in kv for kv in items):
                        items.append(pro)
        except:
            log.exception("schemas/menu walk_programs exception", sys.exc_info()[0])
            pass

    return items

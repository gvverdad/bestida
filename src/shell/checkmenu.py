from src.db import db_session, sqa
from src.db.models.security.Menus import MenuItemAction, MenuItemMenu


# run "./shellserver src.shell.checkmenu development.ini" in /home/gvv/Projects/gvv

def walk_menu(menu, user, tab: int = 0):
    print("", end="\t" * tab)
    print(f"Menu: {menu.MenuId}")
    tab = tab + 1
    for item in menu.Items:
        if isinstance(item, MenuItemAction):
            print("", end="\t" * tab)
            print(f"MenuItem: {item.Desc if item.Desc else item.Program.Name}")
        elif isinstance(item, MenuItemMenu):
            walk_menu(item.Menu, user, tab)


def run(app):
    session = db_session()
    user = session.query(sqa.get_model("Users")).get(1)
    menu = (session.query(sqa.get_model("Menus")).
            filter(sqa.where("MenuId = 'MenuMain'")).
            first())

    walk_menu(menu, user)

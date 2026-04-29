from src.db import db_session, sqa
from src.db.scripts.initmenu import menujson

# run "./shellserver src.shell.loadmenu development.ini" in /home/gvv/Projects/bestida

def create_menu(session, obj, parentobj):
    for o in obj["items"]:
        oi = o["MenuItem"]
        if "items" in oi:
            menu = session.query(sqa.get_model("Menus")).\
                filter(sqa.where("MenuId = '{}'".format(oi["id"]))).first()
            if menu is None:
                menu = sqa.get_model("Menus")()
                menu.MenuId = oi["id"]
                menu.Name = oi["name"]
                db_session.add(menu)

            item = sqa.get_model("MenuItemMenus")()
            item.Line = oi["line"]
            item.Desc = oi["name"]
            item.Menu = menu
            session.add(item)
            parentobj.Items.append(item)
            create_menu(session, oi, menu)
        else:
            prog = session.query(sqa.get_model("Programs")).\
                    filter(sqa.where("Program = '{}'".format(oi["program"]))).\
                    first()
            if not prog:
                prog = sqa.get_model("Programs")()
                prog.Program = oi["program"]
                prog.Name = oi["programname"]
                prog.Type = oi["type"]
                prog.URL = oi["url"]
                prog.Override = "grid" not in oi["url"] and "form" not in oi["url"]
                prog.RunLevel = oi["run"] if "run" in oi else 999
                prog.CreateLevel = oi["create"] if "create" in oi else 999
                prog.UpdateLevel = oi["update"] if "update" in oi else 999
                prog.DeleteLevel = oi["delete"] if "delete" in oi else 999
                if "path" in oi:
                    prog.Path = oi["path"]
                if "component" in oi:
                    prog.Component = oi["component"]
                if "table" in oi:
                    prog.Table = oi["table"]
                session.add(prog)

            item = sqa.get_model("MenuItemActions")()
            item.Line = oi["line"]
            item.Desc = oi["description"]
            item.Program = prog
            session.add(item)
            parentobj.Items.append(item)


def run(app):
    session = db_session()

    main_menu = (session.query(sqa.get_model("Menus")).
                 filter(sqa.where("MenuId = 'MENUMAIN'")).first())

    if main_menu is None:
        main_menu = sqa.get_model("Menus")()
        main_menu.MenuId = "MenuMain"
        main_menu.Name = "Main Menu"
        session.add(main_menu)

    create_menu(session, menujson["Mainmenu"], main_menu)

    session.commit()


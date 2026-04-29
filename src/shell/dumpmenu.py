import json
from src.db import db_session, sqa, engine

# run "./shellserver src.shell.dumpmenu development.ini" in /home/gvv/Projects/bestida

def walk_menu(menu):
    items = list()
    for item in menu.Items:
        #if menu.MenuId == "MENUMAIN" and item.Menu.MenuId == "MenuSysAdmin":
        #    continue
        #if menu.MenuId == "MENUMAIN" and item.Menu.MenuId != "MenuSysAdmin":
        #    continue
        try:
            record = dict()
            if item.TypeOfMenuItem == "Action":
                record["MenuItem"] = dict(line=item.Line, description=item.Desc,
                                          type=item.Program.Type,
                                          table=item.Program.Table,
                                          programname=item.Program.Name,
                                          program=item.Program.Program,
                                          run=item.Program.RunLevel,
                                          create=item.Program.CreateLevel,
                                          update=item.Program.UpdateLevel,
                                          delete=item.Program.DeleteLevel,
                                          path=item.Program.Path,
                                          component=item.Program.Component,
                                          url=item.Program.URL)
            elif item.TypeOfMenuItem == "Menu":
                record["MenuItem"] = dict(line=item.Line, id=item.Menu.MenuId,
                                          description=item.Desc,
                                          name=item.Menu.Name,
                                          items=walk_menu(item.Menu))
            else:
                continue
            items.append(record)
        except Exception as err:
            print("except", str(err))
            continue

    return items

def run(app):
    session = db_session()

    main_menu = (session.query(sqa.get_model("Menus")).
                 filter(sqa.where("MenuId = 'MENUMAIN'")).first())
    menus = dict(Mainmenu=dict(id=main_menu.MenuId, name=main_menu.Name,
                               description=main_menu.Name,
                               items=walk_menu(main_menu)))

    with open("appmenu.json", "w") as f:
        json.dump(menus, f, indent=4)  # indent makes it pretty-printed


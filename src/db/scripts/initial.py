import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .. import sqa, get_session_factory
from ..models.functions import (get_default_country, get_default_locale,
                                get_default_timezone, get_default_currency)
from .initmenu import menujson
from .initapp import initialize_app

log = logging.getLogger(__name__)


def create_menu(db_session, obj, parentobj):
    for o in obj["items"]:
        oi = o["MenuItem"]
        if "items" in oi:
            menu = db_session.query(sqa.get_model("Menus")).\
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
            db_session.add(item)
            parentobj.Items.append(item)
            create_menu(db_session, oi, menu)
        else:
            prog = db_session.query(sqa.get_model("Programs")).\
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
                db_session.add(prog)

            item = sqa.get_model("MenuItemActions")()
            item.Line = oi["line"]
            item.Desc = oi["description"]
            item.Program = prog
            db_session.add(item)
            parentobj.Items.append(item)


def initialize_db(engine):
    """
    before running this program:
    1. remove nullable=False in Users.py ORM
        for fields Company_Id and Role_Id
        then restore after this program
    2. versioning - comment out make_versioned in src.db.__init__.py
        after running this program
        i. uncomment make_versioned in src.db.__init__.py
        ii. intial alembic - alembic upgrade head
        iii. autogenerate - alembic revision --autogenerate -m "version"
        iv. edit alembic version script - remove all Enum definitions
        v.  alembic upgrade head

    :param engine:
    :return:
    """
    log.info("Initialize_db")

    session_factory = get_session_factory(engine)
    db_session = session_factory()

    # define user here because of
    # Key (CreateOpId_Id)=(1) is not present in table "Users".
    # in all other tables
    user = sqa.get_model("Users")()
    user.UserId = "root"
    user.Password = "administrator"
    user.PasswordExpiryDays = 0
    user.ExpiryDate = datetime.utcnow() + relativedelta(years=+50)
    db_session.add(user)

    # Company
    company = db_session.query(sqa.get_model("Companies")).first()
    if company is None:
        company = sqa.get_model("Companies")()
        company.CompanyId = "SETUP"
        company.Name = "Setup Company"
        company.Country = get_default_country()
        company.Currency = get_default_currency()
        company.Locale = get_default_locale()
        company.Timezone = get_default_timezone()
        db_session.add(company)

    # Security Group
    group = db_session.query(sqa.get_model("Groups")).first()
    if group is None:
        group = sqa.get_model("Groups")()
        group.Group = "Setup"
        group.Description = "Setup"
        group.IsAdmin = True
        group.Companies.append(company)
        db_session.add(group)

    # Main Menu
    main_menu = db_session.query(sqa.get_model("Menus")).first()
    if main_menu is None:
        main_menu = sqa.get_model("Menus")()
        main_menu.MenuId = "MenuMain"
        main_menu.Name = "Main Menu"
        db_session.add(main_menu)

        create_menu(db_session, menujson["Mainmenu"], main_menu)

    role = db_session.query(sqa.get_model("Roles")).first()
    if role is None:
        role = sqa.get_model("Roles")()
        role.Group = group
        role.Role = "Admin"
        role.Description = "Admin"
        role.IsAdmin = True
        role.RunLevel = 999
        role.CreateLevel = 999
        role.UpdateLevel = 999
        role.DeleteLevel = 999
        role.StartMenu = main_menu
        db_session.add(role)

    # User Menu
    prog = db_session.query(sqa.get_model("Programs")).filter(sqa.where("Program = 'Profile'")).first()
    if not prog:
        prog = sqa.get_model("Programs")()
        prog.Program = "Profile"
        prog.Name = "Profile"
        prog.Type = "Form"
        prog.Override = True
        prog.URL = "/profile"
        prog.Table = "Persons"
        prog.RunLevel = 0
        prog.CreateLevel = 0
        prog.UpdateLevel = 0
        prog.DeleteLevel = 0
        db_session.add(prog)

    prog = db_session.query(sqa.get_model("Programs")).filter(sqa.where("Program = 'Bookmarks'")).first()
    if not prog:
        prog = sqa.get_model("Programs")()
        prog.Program = "Bookmarks"
        prog.Name = "Bookmarks"
        prog.Type = "Grid"
        prog.Override = True
        prog.URL = "/bookmarks"
        prog.Table = "Bookmarks"
        prog.RunLevel = 0
        prog.CreateLevel = 0
        prog.UpdateLevel = 0
        prog.DeleteLevel = 0
        db_session.add(prog)

    prog = db_session.query(sqa.get_model("Programs")).filter(sqa.where("Program = 'Notifications'")).first()
    if not prog:
        prog = sqa.get_model("Programs")()
        prog.Program = "Notifications"
        prog.Name = "Notifications"
        prog.Type = "Grid"
        prog.Override = True
        prog.URL = "/notifications"
        prog.Table = "Notifications"
        prog.RunLevel = 0
        prog.CreateLevel = 0
        prog.UpdateLevel = 0
        prog.DeleteLevel = 0
        db_session.add(prog)

    prog = db_session.query(sqa.get_model("Programs")).filter(sqa.where("Program = 'Spoolers'")).first()
    if not prog:
        prog = sqa.get_model("Programs")()
        prog.Program = "Spoolers"
        prog.Name = "Spooler"
        prog.Type = "Grid"
        prog.Override = True
        prog.URL = "/spooler"
        prog.Table = "Spoolers"
        prog.RunLevel = 0
        prog.CreateLevel = 0
        prog.UpdateLevel = 0
        prog.DeleteLevel = 0
        db_session.add(prog)

    prog = db_session.query(sqa.get_model("Programs")).filter(sqa.where("Program = 'JobQueues'")).first()
    if not prog:
        prog = sqa.get_model("Programs")()
        prog.Program = "JobQueues"
        prog.Name = "Job Queue"
        prog.Type = "Grid"
        prog.Override = True
        prog.URL = "/jobqueues"
        prog.Table = "Tasks"
        prog.RunLevel = 0
        prog.CreateLevel = 0
        prog.UpdateLevel = 0
        prog.DeleteLevel = 0
        db_session.add(prog)

    prog = db_session.query(sqa.get_model("Programs")).filter(sqa.where("Program = 'Launcher'")).first()
    if not prog:
        prog = sqa.get_model("Programs")()
        prog.Program = "Launcher"
        prog.Name = "Launcher"
        prog.Type = "Form"
        prog.Override = False
        prog.URL = "/form/Launcher"
        prog.Table = "Programs"
        prog.RunLevel = 0
        prog.CreateLevel = 0
        prog.UpdateLevel = 0
        prog.DeleteLevel = 0
        db_session.add(prog)

    prog = db_session.query(sqa.get_model("Programs")).filter(sqa.where("Program = 'Home'")).first()
    if not prog:
        prog = sqa.get_model("Programs")()
        prog.Program = "Home"
        prog.Name = "Home"
        prog.Type = "Script"
        prog.Override = True
        prog.URL = "/home"
        prog.Table = ""
        prog.RunLevel = 0
        prog.CreateLevel = 0
        prog.UpdateLevel = 0
        prog.DeleteLevel = 0
        db_session.add(prog)

    # Controls
    title = db_session.query(sqa.get_model("PersonTitles")).first()
    if title is None:
        title = sqa.get_model("PersonTitles")()
        title.Company = company
        title.Title = "Mr"
        title.Description = "Mr"
        db_session.add(title)

    gender = db_session.query(sqa.get_model("PersonGenders")).first()
    if gender is None:
        gender = sqa.get_model("PersonGenders")()
        gender.Company = company
        gender.Gender = "Male"
        gender.Description = "Male"
        db_session.add(gender)

    device = db_session.query(sqa.get_model("Devices")).first()
    if device is None:
        device = sqa.get_model("Devices")()
        device.Device = "Spooler"
        device.Description = "Spooler"
        db_session.add(device)

    docu = db_session.query(sqa.get_model("Documents")).first()
    if docu is None:
        docu = sqa.get_model("Documents")()
        docu.Document = "PDF"
        docu.Description = "PDF"
        docu.Type = "pdf"
        db_session.add(docu)

    # User
    if user:
        person = sqa.get_model("UserPersons")()
        person.LastName = "Administrator"
        person.FirstName = "Root"
        person.MiddleName = "D"
        person.Title = title
        person.Gender = gender
        person.GravatarId = ""
        db_session.add(person)

        setting = sqa.get_model("UserSettings")()
        setting.Locale = "en-au"
        setting.Timezone = "Australia/Melbourne"
        setting.Theme = "dark"
        setting.SidebarState = "hide"
        db_session.add(setting)

        user.Company = company
        user.Role = role
        user.Personal = person
        user.Settings = setting

    title = sqa.get_model("PersonTitles")()
    title.Company = company
    title.Title = "Ms"
    title.Description = "Ms"
    db_session.add(title)

    gender = sqa.get_model("PersonGenders")()
    gender.Company = company
    gender.Gender = "Female"
    gender.Description = "Female"
    db_session.add(gender)

    db_session.commit()

    # application specific initial setup
    initialize_app(db_session)

    log.info("Initialize_db done")

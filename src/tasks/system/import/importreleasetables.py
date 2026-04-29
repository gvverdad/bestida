import logging, json

from ....db import sqa
from ....server.jobq.tasks import TaskRunner, get_spool_filename

log = logging.getLogger(__name__)


class ImportReleaseTables(TaskRunner):
    def __init__(self, task_id, user_id, settings):
        super(ImportReleaseTables, self).__init__(task_id, user_id, settings)

    def run(self):
        self.context["progId"] = __name__

        programs_added = 0
        programs_updated = 0
        program_states_added = 0
        program_states_updated = 0
        menus_added = 0
        menus_updated = 0
        menu_items_added = 0
        menu_items_updated = 0

        file_name = self.params["file"]["filenames"][0]
        self.context["data_row"] = ["Filename: {}".format(file_name)]
        with open(file_name, "r", encoding="utf-8") as release_file:
            data = json.load(release_file)
            self.context["title"] = "Import Release Tables : " + data["title"]
            initial_load = data["initial"]
            self.context["data_row"].append("Initial Load: {}".format(initial_load))
            select_all_programs = data["selectAllPrograms"]
            self.context["data_row"].append("Select All Programs: {}".format(select_all_programs))

            # Programs
            # program_field_list = ["Program", "Name", "Type",
            #                       "RunLevel", "CreateLevel", "UpdateLevel", "DeleteLevel",
            #                       "Override", "URL", "Table", "Path", "Component"]
            for p in data["Programs"]:
                program = self.db_session.query(sqa.get_model("Programs")).\
                    filter(sqa.where("Programs.Program = '{}' and Programs.Type = '{}'".
                                     format(p["Program"], p["Type"]))).\
                    first()
                if program is None:
                    programs_added += 1
                    program = sqa.get_model("Programs")()
                    program.Program = p["Program"]
                    program.Type = p["Type"]
                else:
                    programs_updated += 1

                try:
                    program.Name = p["Name"] if "Name" in p else None
                except:
                    log.info("Program p is None")

                program.RunLevel = p["RunLevel"] if "RunLevel" in p else 999
                program.CreateLevel = p["CreateLevel"] if "CreateLevel" in p else 999
                program.UpdateLevel = p["UpdateLevel"] if "UpdateLevel" in p else 999
                program.DeleteLevel = p["DeleteLevel"] if "DeleteLevel" in p else 999
                program.Override = p["Override"] if "Override" in p else False
                program.URL = p["URL"] if "URL" in p else None
                program.Table = p["Table"] if "Table" in p else None
                program.Path = p["Path"] if "Path" in p else None
                program.Component = p["Component"] if "Component" in p else None

                self.db_session.add(program)
                self.db_session.commit()

            # ProgramStates
            # states_field_list = ["Program.Program", "Program.Type", "Depth", "Start",
            #                      "PageSize", "State"]
            for ps in data["ProgramStates"]:
                program = self.db_session.query(sqa.get_model("Programs")).\
                    filter(sqa.where("Programs.Program = '{}' and Programs.Type = '{}'".
                                     format(ps["Program"]["Program"], ps["Program"]["Type"]))).\
                    first()
                if program:
                    # Company Level ProgramStates
                    state = self.db_session.query(sqa.get_model("ProgramStates")). \
                        filter(sqa.where("ProgramStates.Company_Id = {:d} and ProgramStates.Program_Id = {:d}".
                                         format(self.task.Company.Id, program.Id))).\
                        first()

                    if state is None:
                        program_states_added += 1
                        state = sqa.get_model("ProgramStates")()
                        state.Company = self.task.Company
                        state.Program = program
                    else:
                        program_states_updated += 1

                    state.Depth = ps["Depth"] if "Depth" in ps else 1
                    state.Start = ps["Start"] if "Start" in ps else 0
                    state.PageSize = ps["PageSize"] if "PageSize" in ps else 10
                    state.State = ps["State"] if "State" in ps else None

                    self.db_session.add(state)
                    self.db_session.commit()

            if initial_load:
                # menus_field_list = ["MenuId", "Name"]
                for m in data["Menus"]:
                    menu = self.db_session.query(sqa.get_model("Menus")).\
                        filter(sqa.where("MenuId = '{}'".format(m["MenuId"]))).\
                        first()
                    if menu is None:
                        menus_added += 1
                        menu = sqa.get_model("Menus")()
                        menu.MenuId = m["MenuId"]
                    else:
                        menus_updated += 1

                    menu.Name = m["Name"] if "Name" in m else None

                    self.db_session.add(menu)
                    self.db_session.commit()

                for mi in data["MenuItems"]:
                    menu = self.db_session.query(sqa.get_model("Menus")).\
                        filter(sqa.where("MenuId = '{}'".format(mi["MenuId"]))).\
                        first()
                    if menu:
                        menu_items_added, menu_items_updated = \
                            self.create_menu(self.db_session, menu, mi["Items"],
                                             menu_items_added, menu_items_updated)
                        self.db_session.commit()

        self.context["data_row"].append(f"Programs Added: {programs_added}")
        self.context["data_row"].append(f"Programs Updated: {programs_updated}")
        self.context["data_row"].append(f"Program States Added: {program_states_added}")
        self.context["data_row"].append(f"Program States Updated: {program_states_updated}")
        self.context["data_row"].append(f"Menus Added: {menus_added}")
        self.context["data_row"].append(f"Menus Updated: {menus_updated}")
        self.context["data_row"].append(f"Menu Items Added: {menu_items_added}")
        self.context["data_row"].append(f"Menu Items Updated: {menu_items_updated}")

        spool_file = get_spool_filename(self.settings)
        self.output_files.append(spool_file + ".pdf")

        self.render_pdf()

        return self.output_files, self.is_conditional

    def create_menu(self, db_session, menu, items,
                    menu_items_added, menu_items_updated):
        for item in items:
            # find existing menuitem
            idx, itm = next(((idx, itm) for idx, itm in enumerate(menu.Items)
                             if itm.Line == item["Line"]), (None, None))
            if item["Type"] == "Action":
                program = db_session.query(sqa.get_model("Programs")). \
                    filter(sqa.where("Programs.Program = '{}' and Programs.Type = '{}'".
                                     format(item["Program"], item["ProgramType"]))). \
                    first()
                if program:
                    if itm is None:
                        menu_items_added += 1
                        itm = sqa.get_model("MenuItemActions")()
                    else:
                        menu_items_updated += 1
                    itm.Line = item["Line"]
                    itm.Desc = item["Desc"]
                    itm.Program = program
                    db_session.add(itm)
                    if idx is None:
                        menu.Items.append(itm)
                    else:
                        menu.Items[idx] = itm
            else:
                men = self.db_session.query(sqa.get_model("Menus")).\
                    filter(sqa.where("MenuId = '{}'".format(item["MenuId"]))).\
                    first()
                if men:
                    if itm is None:
                        menu_items_added += 1
                        itm = sqa.get_model("MenuItemMenus")()
                    else:
                        menu_items_updated += 1
                    itm.Line = item["Line"]
                    itm.Desc = item["Desc"]
                    itm.Menu = men
                    db_session.add(itm)
                    if idx is None:
                        menu.Items.append(itm)
                    else:
                        menu.Items[idx] = itm
                    self.create_menu(db_session, men, item["MenuItems"],
                                     menu_items_added, menu_items_updated)
        db_session.add(menu)
        return menu_items_added, menu_items_updated

    def get_notify_message(self, spool_filename=None, attach_filename=None):
        return super(ImportReleaseTables, self).get_notify_message(self.output_files[0], 'ImportReleaseTables.pdf')

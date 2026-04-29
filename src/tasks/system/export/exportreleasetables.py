import os, logging, json

from ....db import sqa
from ....schemas.datasource import (build_joins, build_filters,
                                    build_where, query, ListCriteriaType)
from ....server.jobq.tasks import TaskRunner, get_spool_filename

log = logging.getLogger(__name__)


class ExportReleaseTables(TaskRunner):
    def __init__(self, task_id, user_id, settings):
        super(ExportReleaseTables, self).__init__(task_id, user_id, settings)

    def run(self):
        self.context["title"] = "Export Release Tables: " + self.task.Title
        self.context["progId"] = __name__

        error_list = []

        data = dict(title=self.task.Title, initial=self.params["initial"],
                    selectAllPrograms=self.params["programs"][0] == "All")

        menus_field_list = ["MenuId", "Name"]
        program_field_list = ["Program", "Name", "Type",
                              "RunLevel", "CreateLevel", "UpdateLevel", "DeleteLevel",
                              "Override", "URL", "Table", "Path", "Component"]
        states_field_list = ["Program.Program", "Program.Type", "Depth", "Start", "PageSize", "State"]

        if self.params["initial"]:
            self.context["data_row"] = ["Initial Release: True"]
            menus = self.db_session.query(sqa.get_model("Menus")).all()

            self.context["data_row"].append(f"Menu records: {len(menus)}")
            data["Menus"] = [r.data_to_dict(depth=1,
                                            field_list=menus_field_list,
                                            except_fields=["Password"],
                                            tuple_choice=False,
                                            choice_key=True,
                                            text_as_string=True,
                                            m2m_merge=False) for r in menus]
            data["MenuItems"] = []
            for m in menus:
                data["MenuItems"].append(dict(MenuId=m.MenuId, Items=m.dump_items()))
        else:
            self.context["data_row"] = ["Initial Release: False"]

        if self.params["programs"][0] == "All":
            self.context["data_row"].append("Programs: ALL")

            if len(self.params["criteria"]) > 0:
                filters, joins, join_tables = build_filters("Programs",
                                                            self.params["criteria"],
                                                            [], {})

                where = build_where("Programs", self.session["timezone"],
                                    filters, ListCriteriaType(self.params["criteriatype"]))

                qry = query(self.db_session, "Programs", [], where)
                progs = qry.all()
            else:
                progs = self.db_session.query(sqa.get_model("Programs")).all()

            self.context["data_row"].append(f"Programs records: {len(progs)}")
            data["Programs"] = [r.data_to_dict(depth=1,
                                               field_list=program_field_list,
                                               except_fields=["Password"],
                                               tuple_choice=False,
                                               choice_key=True,
                                               text_as_string=True,
                                               m2m_merge=False) for r in progs]

            states = (self.db_session.query(sqa.get_model("ProgramStates")).
                      filter(sqa.where(f"ProgramStates.Company_Id = {self.user.Company_Id} and ProgramStates.User_Id = {self.user.Id}")).
                      all())
            self.context["data_row"].append(f"ProgramStates records: {len(states)}")
            data["ProgramStates"] = [r.data_to_dict(depth=1,
                                                    field_list=states_field_list,
                                                    except_fields=["Password"],
                                                    tuple_choice=False,
                                                    choice_key=True,
                                                    text_as_string=True,
                                                    m2m_merge=False) for r in states]
        else:
            self.context["data_row"].append(f"Programs records: {len(self.params['programs'])}")
            data["Programs"] = []
            for pid in self.params["programs"]:
                prog = self.db_session.query(sqa.get_model("Programs")).get(pid)
                self.context["data_row"].append(prog.Program)

                data["Programs"].append(prog.data_to_dict(depth=1,
                                                          field_list=program_field_list,
                                                          except_fields=["Password"],
                                                          tuple_choice=False,
                                                          choice_key=True,
                                                          text_as_string=True,
                                                          m2m_merge=False))
                if prog.Type == "Grid":
                    where = (f"Company_Id = {self.user.Company_Id} and "
                             f"User_Id = {self.user.Id} and "
                             f"ProgramStates.Program.Program startswith ('{prog.Program}')")
                    joins, joins_tables = build_joins("ProgramStates.Program")

                    states = (self.db_session.query(sqa.get_model("ProgramStates")).filter(sqa.where(where)).
                              join(sqa.instrumented_attr(joins[0][0], joins[0][1])).all())
                    self.context["data_row"].append(f"ProgramStates records: {len(states)}")
                    data["ProgramStates"] = [r.data_to_dict(depth=1,
                                                            field_list=states_field_list,
                                                            except_fields=["Password"],
                                                            tuple_choice=False,
                                                            choice_key=True,
                                                            text_as_string=True,
                                                            m2m_merge=False) for r in states]

        rel_file = os.path.join(self.settings["release"]["location"],
                                self.task.Title.replace(" ", "_") + ".json")
        with open(rel_file, "w", encoding="utf-8") as release_file:
            json.dump(data, release_file)
            # https://codeyarns.com/tech/2017-02-22-python-json-dump-misses-last-newline.html
            release_file.write("\n")

        if len(error_list) > 0:
            self.is_conditional = True
            self.context["data_row"].append("Errors:")
            for err in error_list:
                self.context["data_row"].append(err)
        else:
            self.context["data_row"].append("Errors: None")

        spool_file = get_spool_filename(self.settings)
        self.output_files.append(spool_file + ".pdf")

        self.render_pdf()

        return self.output_files, self.is_conditional

    def get_notify_message(self, spool_filename=None, attach_filename=None):
        return super(ExportReleaseTables, self).get_notify_message(self.output_files[0], 'ExportReleaseTables.pdf')

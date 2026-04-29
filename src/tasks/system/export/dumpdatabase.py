import os, logging, json
from datetime import datetime

from ....db import sqa
from ....server.jobq.tasks import TaskRunner, get_spool_filename
from ....db.models.functions import get_tables_choices

log = logging.getLogger(__name__)

# TODO: test this

class DumpDatabase(TaskRunner):
    def __init__(self, task_id, user_id, settings):
        super(DumpDatabase, self).__init__(task_id, user_id, settings)

    def run(self):
        self.context["title"] = "Dump Database : " + self.task.Title
        self.context["progId"] = __name__

        dir_name = "{}_{:%Y%m%d%H%M%f}".format(self.task.Title.strip().replace(" ", "_"),
                                               datetime.now())
        path = os.path.join(self.settings["dump"]["location"], dir_name)
        os.mkdir(path, 0o777)

        if self.params["data"]["Companies"]:
            valid_companies_id = [str(i) for i in self.params["data"]["Companies"]]
        else:
            valid_companies_id = [str(r.Id) for r in self.user.Role.Group.Companies]

        coys = self.db_session.query(sqa.get_model("Companies"))\
            .filter(sqa.where("Id in ({})".format(",".join(valid_companies_id)),
                              table_name="Companies"))
        coy_name = []
        for c in coys:
            coy_name.append(c.CompanyId)

        self.context["data_head"] = list()
        self.context["data_head"].append("Directory: {}".format(dir_name))
        self.context["data_head"].append("Companies: {}".format(",".join(coy_name)))
        if self.params["data"]["Tables"]:
            self.context["data_head"].append("Tables: {}".format(",".join(self.params["data"]["Tables"])))
        else:
            self.context["data_head"].append("Tables: ALL")

        tables = get_tables_choices()
        total_tables = 0
        for table in tables:
            if self.params["data"]["Tables"]:
                if table[0] not in self.params["data"]["Tables"]:
                    continue

            info = sqa.get_table_info(table[0])
            if "polymorphic_id" in info and info["polymorphic_id"] == "Base":
                continue
            company_field = None
            if info is not None and "companyField" in info:
                company_field = info["companyField"]
                if company_field and "." not in company_field:
                    company_field = table[0] + "." + company_field
            where = ""
            if company_field is not None:
                where = ("{} in ({})".format(company_field,
                                             ",".join(valid_companies_id)))

            qry = self.db_session.query(sqa.get_model(table[0]))
            if where:
                qry = qry.filter(sqa.where(where, table_name=table[0]))
            records = qry.all()
            if records is None:
                continue
            record_count = len(records)
            if record_count == 0:
                continue
            file = os.path.join(path, "{}.json".format(table[0]))

            with open(file, "w") as json_file:
                json_file.write('{"info": ')
                json.dump(info, json_file, default=str)
                json_file.write(', "data": [')
                first_time = True
                for record in records:
                    if not first_time:
                        json_file.write(",")
                    json.dump(record.data_to_dict(tuple_choice=False,
                                                  choice_key=True,
                                                  ignore_calc_fields=True,
                                                  dump=True),
                              json_file, default=str)
                    if first_time:
                        first_time = False
                json_file.write("]}")

            self.context["data_row"].append([
                table[0],
                table[1],
                record_count
            ])
            total_tables = total_tables + 1

        self.context["data_sum"] = list()
        self.context["data_sum"].append("Total Tables: {:d}".format(total_tables))

        spool_file = get_spool_filename(self.settings)
        self.output_files.append(spool_file + ".pdf")
        self.render_pdf(body_template="report/system/export/dumpDatabaseBody.jinja2")

        return self.output_files, self.is_conditional

    def get_notify_message(self, spool_filename=None, attach_filename=None):
        return super(DumpDatabase, self).get_notify_message(self.output_files[0],
                                                            'DumpDatabase.pdf')


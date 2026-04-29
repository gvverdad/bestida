import os, logging

import pyexcel
from sqlalchemy.exc import IntegrityError

from ....db import sqa
from ....utils.misc import string_to_type, quoter, get_attr, set_attr
from ....server.jobq.tasks import TaskRunner, get_spool_filename

log = logging.getLogger(__name__)

class ImportTables(TaskRunner):
    def __init__(self, task_id, user_id, settings):
        super(ImportTables, self).__init__(task_id, user_id, settings)

    def run(self):
        self.context["title"] = f"Import Tables : {self.task.Title}"
        self.context["progId"] = __name__

        file_name = self.params["file"]["filenames"][0]
        table = self.params["table"]

        level = self.params["level"]
        header_row = self.params["header"]-1

        maps = self.params["maps"]["data"]
        fields = self.params["maps"]["fields"]

        table_schema = self.params["tableSchema"]

        parent_table_name = None
        parent_company_field = None
        if table_schema["componentOf"] is not None:
            parent_table_name = table_schema["componentOf"]["table"]
            info = sqa.get_table_info(parent_table_name)
            if info is not None and "companyField" in info:
                parent_company_field = info["companyField"]

        company_field = table_schema["companyField"]
        company = None
        if company_field is not None:
            if "." in company_field:
                company = company_field.split(".")[-1]
            else:
                company = company_field

        dup_action = self.params["dups"]["duphandler"] # Overwrite; Skip
        dup_condition = self.params["dups"]["dupkeycond"]  # 0=All; 1=Any; 2=None; 3=Not All
        dup_fields = self.params["dups"]["dupkeys"]
        check_dup = len(dup_fields) > 0

        total_records = 0
        total_create = 0
        total_update = 0
        error_list = []

        try:
            sheet = pyexcel.get_sheet(file_name=file_name)
        except Exception as error:
            sheet = None
            error_list.append(f"FileError : {file_name} : {error}")

        if sheet:
            try:
                for row_idx, row in enumerate(sheet):
                    if row_idx <= header_row:
                        continue

                    total_records = total_records + 1
                    record = None
                    parent_table = None

                    if parent_table_name is not None:
                        where = ""
                        joins = []
                        for idx, fld in enumerate(fields):
                            if fld["table"] != parent_table_name:
                                continue
                            action = f"field_action_{idx}"
                            if maps[action] == "NoAction":
                                continue
                            if where == "" and \
                                    parent_company_field is not None:
                                where = f"{parent_company_field} = {self.task.Company.Id} and "
                            else:
                                where = where + " and "
                            where, joins, error_list = self.build_where(parent_table_name,
                                                                        fld["name"],
                                                                        fld, maps, action, row,
                                                                        row_idx, idx, joins,
                                                                        where, error_list)
                        qry = self.db_session.query(sqa.get_model(parent_table_name))
                        if where:
                            qry = qry.filter(sqa.where(where))
                        parent_table = qry.first()

                    if check_dup:
                        where = ""
                        joins = []

                        for dup_fld in dup_fields:
                            for idx, fld in enumerate(fields):
                                if fld["name"] != dup_fld.replace("_Id", "").strip():
                                    continue

                                action = f"field_action_{idx}"
                                if maps[action] == "NoAction":
                                    break

                                if where == "":
                                    if dup_condition > 1:
                                        where = "NOT ("
                                    if company_field is not None:
                                        where = where + f"{company_field} = {self.task.Company.Id} and "
                                else:
                                    if dup_condition == 0 or dup_condition == 2:
                                        where = where + " and "
                                    else:
                                        where = where + " or "

                                if fld["table"] == parent_table_name:
                                    if parent_table_name is not None and \
                                            parent_table is not None:
                                        backref = table_schema["componentOf"]["list"]["backref"]
                                        if not backref.endswith("_Id"):
                                            backref = backref + "_Id"
                                        where = where + f" {backref} = {parent_table.Id}"
                                    break

                                where, joins, error_list = self.build_where(table, dup_fld,
                                                                            fld, maps, action, row,
                                                                            row_idx, idx, joins,
                                                                            where, error_list)
                                break

                        if where:
                            if dup_condition > 1:
                                where = where + ")"

                        qry = self.db_session.query(sqa.get_model(table))
                        if joins:
                            for j in joins:
                                # joinlist = [(table, key, joinTable, alias),..]
                                # joinlist = [('CountryLocalities', 'Country', 'Countries', u'CountryLocalities_Country')]
                                qry = qry.join(sqa.instrumented_attr(j[0], j[1]))

                        if where:
                            qry = qry.filter(sqa.where(where))

                        record = qry.first()
                        if record is not None and dup_action == "Skip":
                            continue  # skip record found

                    if record is None:
                        record = sqa.get_model(table)()

                        if company is not None:
                            setattr(record, company, self.task.Company.Id)

                        total_create = total_create + 1
                    else:
                        total_update = total_update + 1

                    for fld_idx, fld in enumerate(fields):
                        action = f"field_action_{fld_idx}"
                        if maps[action] == "NoAction":
                            continue
                        data = None
                        value = None
                        try:
                            if maps[action] == "Column":
                                val_name = f"field_value_column_{fld_idx}"
                                value = str(row[int(maps[val_name]) - 1])
                            elif maps[action] == "Constant":
                                val_name = f"field_value_constant_{fld_idx}"
                                if fld["type"] == "Enum" and \
                                        type(maps[val_name]) is list:
                                    value = maps[val_name][0]
                                else:
                                    value = str(maps[val_name])

                            if fld["type"] == "Select":
                                if maps[action] == "Column":
                                    # join_list = [(table, key, joinTable, alias),..]
                                    tbl = fld["join_list"][-1][2]
                                    # get the correct record. ie by Company by Country etc..
                                    info = sqa.get_table_info(tbl)
                                    where = ""
                                    key_found = False

                                    if info is not None:
                                        if "companyField" in info:
                                            if info["companyField"] is not None:
                                                where = f"{info['companyField']} = {self.task.Company.Id} and "
                                        if "keyPaths" in info:
                                            for k in info["keyPaths"]:
                                                if ("companyField" in info and
                                                        info["companyField"] is not None):
                                                    if k == info["companyField"]:
                                                        continue
                                                where = where + f"{k} = {quoter(get_attr(record, k, 0))} and "
                                        if "key" in info:
                                            where = where + f"{info['key']} = {quoter(value)}"
                                            key_found = True
                                    if not key_found:
                                        where = where + f"{fld['select_key']} = {quoter(value)}"

                                    data = self.db_session.query(sqa.get_model(tbl)).\
                                        filter(sqa.where(where)).first()
                                    value = data.Id if data is not None else None
                                else:
                                    value = maps[val_name]["Id"]
                                if value is None:
                                    raise ValueError(f"value: {value}")

                                setattr(record, f"{fld['name']}_Id", int(value))
                            else:
                                setattr(record, fld["name"], string_to_type(fld["type"], value))
                        except ValueError as err:
                            error_list.append(f"Row: {row_idx+1} Field: {fld['name']} Data: {data} AssignError:{str(err)}")
                        except NotImplementedError as err:
                            error_list.append(f"Row: {row_idx+1} Field: {fld['name']} Data: {data} AssignError NotImplementedError:{str(err)}")

                    self.db_session.add(record)

                    if parent_table is not None:
                        list_field = table_schema["componentOf"]["list"]["field"]
                        if list_field:
                            items = get_attr(parent_table, list_field, [])
                            items.append(record)
                            set_attr(parent_table, list_field, items)
                            self.db_session.add(parent_table)

                    self.db_session.commit()
            except IntegrityError as err:
                error_list.append(f"Row: {row_idx+1} DatabaseError:{str(err)}")

        self.context["data_row"] = [f"Table: {table}",
                                    "",
                                    f"Total Records: {total_records}",
                                    f"Total Created: {total_create}",
                                    f"Total Update: {total_update}",
                                    "",
                                    "Errors:"]

        if len(error_list) > 0:
            self.is_conditional = True
            for err in error_list:
                self.context["data_row"].append(err)
        else:
            self.context["data_row"].append("None")
            if os.path.exists(file_name):
                os.remove(file_name)

        spool_file = get_spool_filename(self.settings)
        self.output_files.append(spool_file + ".pdf")

        self.render_pdf()

        return self.output_files, self.is_conditional

    def get_notify_message(self, spool_filename=None, attach_filename=None):
        return super(ImportTables, self).get_notify_message(self.output_files[0], 'ImportTables.pdf')

    def build_where(self, table, fld_name, fld, maps, action, row, row_idx, idx,
                    joins, where, error_list):
        if fld["type"] == "Select":
            # join_list = [(table, key, joinTable, alias),..]
            # join_list = [('CountryLocalities', 'Country', 'Countries', u'CountryLocalities_Country')]
            if maps[action] == "Column":
                for j in fld["join_list"]:
                    joins.append(j)
                col = f"{fld['join_list'][-1][2]}.{fld['select_key']}"
            else:
                col = f"{fld['join_list'][-1][0]}.{fld_name}_Id"
        else:
            col = f"{table}.{fld_name}"

        where = where + col + " == "
        data = None
        try:
            if maps[action] == "Column":
                val_name = f"field_value_column_{idx}"
                data = row[int(maps[val_name]) - 1]
            else:
                val_name = f"field_value_constant_{idx}"
                if fld["type"] == "Enum" and \
                        type(maps[val_name]) is list:
                    data = maps[val_name][0]
                else:
                    data = maps[val_name]

            if fld["type"] == "Select":
                if maps[action] == "Constant":
                    where = where + quoter(str(data["Id"]), "Integer")
                else:
                    where = where + quoter(str(data))
            else:
                where = where + quoter(str(data), fld["type"])
        except ValueError as err:
            err_msg = f"Row: {row_idx+1} Field: {fld['name']} Data: {data} WhereError: {str(err)}"
            error_list.append(err_msg)

        return where, joins, error_list

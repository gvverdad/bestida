import os, logging

from typing import List, Tuple, Dict, Any, Optional

import pyexcel
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import class_mapper, Mapper
from sqlalchemy import Table
from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOONE, MANYTOMANY
from sqlalchemy.inspection import inspect
from sqlalchemy.testing.provision import update_db_opts

from ....db import sqa
from ....utils.misc import string_to_type, quoter, get_attr, set_attr
from ....server.jobq.tasks import TaskRunner, get_spool_filename

log = logging.getLogger(__name__)

EXCLUDE_FIELDS = ("CreateOpId", "ModifiedOpId", "InactiveOpId", "Company", "versions",
                  "CreateTimeStamp", "ModifiedTimeStamp", "InactiveTimeStamp")

class ImportTables(TaskRunner):
    def __init__(self, task_id, user_id, settings):
        super(ImportTables, self).__init__(task_id, user_id, settings)

        self.table = None
        self.table_schema = None
        self.maps = None
        self.fields = None

    def run(self):
        self.context["title"] = f"Import Tables : {self.task.Title}"
        self.context["progId"] = __name__

        self.table = self.params["table"]
        self.table_schema = self.params["tableSchema"]
        self.maps = self.params["maps"]["data"]
        self.fields = self.params["maps"]["fields"]

        cls = sqa.get_model(self.table)
        mapper = class_mapper(cls)

        file_name = self.params["file"]["filenames"][0]
        level = self.params["level"]
        header_row = self.params["header"]-1

        parent_table_name = None
        parent_table_field = None
        if self.table_schema["parentTables"]:
            parent_table_name = self.table_schema["parentTables"][-1]["table"]
            parent_table_field = self.table_schema["parentTables"][-1]["column"]

        company_field = self.table_schema.get("companyField", None)

        dup_action = self.params["dups"]["duphandler"] # Overwrite; Skip
        dup_condition = self.params["dups"]["dupkeycond"]  # 0=All; 1=Any; 2=None; 3=Not All
        dup_fields = self.params["dups"]["dupkeys"]
        check_duplicates = len(dup_fields) > 0

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
            for row_idx, row in enumerate(sheet):
                try:
                    if row_idx <= header_row:
                        continue

                    total_records = total_records + 1
                    record = None
                    parent_table = None

                    if parent_table_name is not None:
                        idx, fld = self.get_field(parent_table_field)
                        if fld is not None:
                            action = f"field_action_{idx}"
                            if self.maps and self.maps.get(action,"NoAction") != "NoAction":
                                parent_table = self.get_record(row, parent_table_name, fld, idx)


                    if check_duplicates:
                        where = ""
                        joins = []

                        for dup_fld in dup_fields:
                            idx, fld = self.get_field(dup_fld)
                            if fld is None:
                                continue

                            action = f"field_action_{idx}"
                            if self.maps[action] == "NoAction":
                                continue

                            if where == "":
                                if dup_condition > 1:
                                    where = "NOT ("
                                if company_field is not None:
                                    where = where + f"{self.table}.{company_field} = {self.task.Company.Id} and "
                            else:
                                if dup_condition == 0 or dup_condition == 2:
                                    where = where + " and "
                                else:
                                    where = where + " or "

                            if fld["name"] == parent_table_field:
                                if parent_table is not None:
                                    where = where + f" {self.table}.{parent_table_field}_Id = {parent_table.Id} "
                                continue

                            where, joins, error_list = self.build_where(self.table, dup_fld,
                                                                            fld, row,
                                                                            row_idx, idx, joins,
                                                                            where, error_list)

                        if where:
                            if dup_condition > 1:
                                where += ")"

                        qry = self.db_session.query(sqa.get_model(self.table))
                        if joins:
                            for j in joins:
                                # join_list = [[table, key, joinTable, alias, nullable, cardinality]]
                                # join_list = [['CustomerStores', 'ItemCustomer', 'Customers', 'CustomerStores_ItemCustomer', True, 'n:1']]
                                qry = qry.join(sqa.instrumented_attr(j[0], j[1]))

                        if where:
                            qry = qry.filter(sqa.where(where))

                        record = qry.first()
                        if record is not None and dup_action == "Skip":
                            continue  # skip record found

                    if record is None:
                        record = cls()
                        mode = "Create"
                    else:
                        mode = "Update"

                    _, updated = self.populate_record(record, mapper, error_list, row_idx, row)
                    if updated:
                        self.db_session.commit()
                        if mode == "Create":
                            total_create = total_create + 1
                        else:
                            total_update = total_update + 1

                except IntegrityError as err:
                    self.db_session.rollback()
                    error_list.append(f"Row: {row_idx+1} DatabaseError:{str(err)}")

        self.context["data_row"] = [f"Table: {self.table}",
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

    def get_notify_message(self, spool_filename: Optional[str] = None, attach_filename: Optional[str] = None):
        return super(ImportTables, self).get_notify_message(self.output_files[0], 'ImportTables.pdf')

    def populate_record(self, record: DeclarativeMeta,
                        mapper: Mapper,
                        error_list: List,
                        row_idx: int, row: List,
                        row_key: Optional[str] = None,
                        required_entry: Optional[Dict] = None) -> Tuple[DeclarativeMeta, bool]:
        updated = False

        table = mapper.local_table
        company_field = table.info.get("companyField", None)

        visited = list()
        errors = 0
        # use mapper.columns instead of table.columns to handle inherited tables
        for col in mapper.columns:
            if col.primary_key:  # Id
                continue
            if company_field and col.key == company_field:
                setattr(record, col.key, self.task.Company.Id)
                updated = True
                continue
            if not col.info.get("modifiable", True):
                continue
            if col.key.startswith(EXCLUDE_FIELDS):
                continue
            if col.foreign_keys:
                rel = next(
                    (r for r in mapper.relationships if col in r.local_columns),
                    None
                )
                if rel is None:
                    continue
                if rel.key in visited:
                    continue
                visited.append(rel.key)
                # col.key = Type_Id;  rel.key = Type
                if row_key is not None:
                    key = f"{row_key}.{rel.key}"
                else:
                    key = rel.key
                value = self.get_value(row, key)
                if value is not None:
                    primary_key = rel.mapper.primary_key[0].key  # Id
                    setattr(record, col.key, getattr(value, primary_key))
                    updated = True

                req_value = getattr(record, col.key, None)
                if row_key is None: # main table
                    if req_value is None:
                        if not col.nullable:
                            updated = False
                            errors += 1
                            error_list.append(
                                f"Row {row_idx + 1} : Field {key} is Invalid: {self.get_cell_value(row, key)}")
                elif required_entry is not None: # related table
                    req_key = required_entry.get("type", None)
                    req_val = required_entry.get("value", None)
                    if "." in req_key:
                        req_key = req_key.split(".")[-1]
                    if req_key and req_key == rel.key and isinstance(req_val, list):
                        val = getattr(value, rel.key, None)
                        if val != req_val[0]:
                            updated = False
                            errors += 1
                            error_list.append(
                                f"Row {row_idx + 1} : Field {key} is Invalid: {val} should be {req_val[0]}")
                    elif req_value is None:
                        if not col.nullable:
                            updated = False
                            errors += 1
                            error_list.append(
                                f"Row {row_idx + 1} : Field {key} is Invalid: {self.get_cell_value(row, key)}")

                continue

            if row_key is not None:
                key = f"{row_key}.{col.key}"
            else:
                key = col.key

            value = self.get_value(row, key)
            if value is not None:
                setattr(record, col.key, value)
                updated = True

            if row_key is None or required_entry is not None: # related table:
                if not col.nullable:
                    val = getattr(record, col.key, None)
                    if val is None or str(val).strip() == "":
                        updated = False
                        errors += 1
                        error_list.append(f"Row {row_idx+1} : Field {key} is a required Field: {self.get_cell_value(row, key)}")

        if not updated or errors > 0:
            return record, False

        self.db_session.add(record)
        self.db_session.flush()  # get PK

        errors = 0
        # import relationships
        for rel in mapper.relationships:
            if rel.lazy == 'dynamic':
                continue
            if rel.key.startswith(EXCLUDE_FIELDS):
                continue
            if rel.info.get("hidden", False):
                continue

            # ignore MANYTOONE backref
            # WarehouseArea - ManyToOne side of Warehouse  ItemWarehouse
            # Warehouse - OneToMany Areas
            # WarehouseArea.ItemWarehouse backref is None
            if rel.direction is MANYTOONE and rel.backref is None and rel.back_populates is not None:
                continue

            if rel.direction is MANYTOMANY:
                continue
            if rel.key in visited:
                continue
            else:
                visited.append(rel.key)

            if row_key is None:
                parent_field_key = rel.key
            else:
                parent_field_key = f"{row_key}.{rel.key}"

            if self.is_record_unique(rel.mapper, row, record, parent_field_key):
                continue

            required_entry = rel.info.get("requiredEntry", None)
            if rel.uselist:
                children = getattr(record, rel.key, [])
                child = rel.mapper.class_()
                child, was_updated = self.populate_record(child, rel.mapper,
                                                          error_list,
                                                          row_idx, row,
                                                          parent_field_key,
                                                          required_entry)
                if was_updated:
                    children.append(child)

                if required_entry is not None:
                    req_key = required_entry.get("type", None)
                    req_val = required_entry.get("value", None)
                    req_min = int(required_entry.get("min", 0))
                    lines = 0
                    if req_key and isinstance(req_val, list) and req_min > 0:
                        for chld in children:
                            val = get_attr(chld, req_key, None)
                            if val == req_val[0]:
                                lines += 1
                    if req_min > 0 and lines < req_min:
                        was_updated = False
                        updated = False
                        errors += 1
                        error_list.append(
                                f"Row {row_idx + 1} : Field {rel.key} requires a min of {req_min} {req_val[0]} record")

                if was_updated:
                    updated = True
                    setattr(record, rel.key, children)
            else:
                child = rel.mapper.class_()
                child, was_updated = self.populate_record(child, rel.mapper,
                                                          error_list,
                                                          row_idx, row,
                                                          parent_field_key,
                                                          required_entry)

                if required_entry is not None:
                    req_key = required_entry.get("type", None)
                    req_val = required_entry.get("value", None)
                    req_min = int(required_entry.get("min", 0))
                    lines = 0
                    if req_key and isinstance(req_val, list) and req_min > 0:
                        val = get_attr(child, req_key, None)
                        if val == req_val[0]:
                            lines += 1
                    if req_min > 0 and lines < req_min:
                        was_updated = False
                        updated = False
                        errors += 1
                        error_list.append(
                                f"Row {row_idx + 1} : Field {rel.key} requires a min of {req_min} {req_val[0]} record")

                if was_updated:
                    setattr(record, rel.key, child)
                    updated = True

        if not updated or errors > 0:
            return record, False
        return record, updated

    def get_unique_index_fields(self, table: Table) -> List[str]:
        for idx in table.indexes:
            if idx.unique:
                return [col for col in idx.columns]  # Column object

        return list()

    def is_record_unique(self, mapper: Mapper, row: List,  parent: Optional[DeclarativeMeta] = None, parent_key: Optional[str] = None) -> bool:
        table = mapper.local_table
        index_columns = self.get_unique_index_fields(table)
        company_field = table.info.get("companyField", None)

        filters = {}
        for col in index_columns:
            if col.key == company_field:
                filters[col.key] = self.task.Company.Id
                continue

            if col.foreign_keys:
                rel = next(
                    (r for r in mapper.relationships
                        if col in r.local_columns
                    ),
                    None
                )
                # col.key = Type_Id; rel.key = Type
                if parent_key is not None:
                    key = f"{parent_key}.{rel.key}"
                else:
                    key = rel.key

                value = self.get_value(row, key)
                if value is None and parent is not None:
                    value = parent
                if value is not None:
                    primary_key = rel.mapper.primary_key[0].key  # Id
                    filters[col.key] = getattr(value, primary_key, None)
                else:
                    filters[col.key] = None
            else:
                if parent_key is not None:
                    key = f"{parent_key}.{col.key}"
                else:
                    key = col.key
                filters[col.key] = self.get_value(row, key)

        if filters:
            existing = self.db_session.query(mapper.class_).filter_by(**filters).first()
            return existing is not None

        return False


    def get_field(self, field_name: str) -> Tuple[str, str]:
        for fld_idx, fld in enumerate(self.fields):
            if fld["name"] == field_name:
                return fld_idx, fld

        return None, None


    def get_cell_value(self, row: List, field_name: str) -> Any:
        fld_idx, fld = self.get_field(field_name)
        if fld is not None:
            action = f"field_action_{fld_idx}"
            if self.maps[action] == "NoAction":
                return None

            if self.maps[action] == "Column":
                val_name = f"field_value_column_{fld_idx}"
                return str(row[int(self.maps[val_name]) - 1])
            elif self.maps[action] == "Constant":
                val_name = f"field_value_constant_{fld_idx}"
                if fld["type"] == "Enum" and type(self.maps[val_name]) is list:
                    return self.maps[val_name][0]
                else:
                    return str(self.maps[val_name])

        return None


    def get_value(self, row: List, field_name: str) -> Any:
        fld_idx, fld = self.get_field(field_name)
        if fld is not None:
            action = f"field_action_{fld_idx}"
            if self.maps[action] == "NoAction":
                return None

            if fld["type"] == "Select":
                table_name = fld["table"]
                join_list = fld.get("join_list", None)
                if join_list:
                    table_name = join_list[-1][2]
                return self.get_record(row, table_name, fld, fld_idx)
            elif self.maps[action] == "Column":
                val_name = f"field_value_column_{fld_idx}"
                return str(row[int(self.maps[val_name]) - 1])
            elif self.maps[action] == "Constant":
                val_name = f"field_value_constant_{fld_idx}"
                if fld["type"] == "Enum" and type(self.maps[val_name]) is list:
                    return self.maps[val_name][0]
                else:
                    return str(self.maps[val_name])

        return None


    def get_record(self, row: List, table_name: str, field: Dict, index: int) -> Any:
        action = f"field_action_{index}"
        if self.maps[action] == "Constant" and field["type"] == "Select":
            value = f"field_value_constant_{index}"
            qry = self.db_session.query(sqa.get_model(table_name))
            return qry.get(self.maps[value]["Id"])

        if self.maps[action] == "Column":
            value = f"field_value_column_{index}"
            data = row[int(self.maps[value]) - 1]
        else:
            value = f"field_value_constant_{index}"
            if field["type"] == "Enum" and type(self.maps[value]) is list:
                data = self.maps[value][0]
            else:
                data = self.maps[value]

        if data is None:
            return None

        info = sqa.get_table_info(table_name)
        key = field.get("select_key", None)
        if "." in key:
            key = key.split(".")[-1]
        if key is None and info:
            key = info.get("key", None)

        if key is None:
            return None

        company_field = None
        if info:
            company_field = info.get("companyField", None)

        filters = {}
        if company_field:
            filters["companyField"] = self.task.Company.Id
        filters[key] = quoter(str(data), field["type"])

        # additional filter
        key = field.get("select_field", None)
        if "." in key:
            key = key.split(".")[-1]
        if key is not None:
            data = self.get_value(row, key)
            if data is not None:
                filters[key] = quoter(str(data), field["type"])

        if filters:
            return self.db_session.query(sqa.get_model(table_name)).filter_by(**filters).first()
        else:
            return None

    def build_where(self, table_name: str, fld_name: str,
                    field: Dict, row: List, row_idx: int, idx: int,
                    joins: List, where: str, error_list: List) -> Tuple[str, List, List]:

        action = f"field_action_{idx}"
        if field["type"] == "Select":
            # join_list = [[table, key, joinTable, alias, nullable, cardinality]]
            # join_list = [['CustomerStores', 'ItemCustomer', 'Customers', 'CustomerStores_ItemCustomer', True, 'n:1']]
            if self.maps[action] == "Column":
                for j in field["join_list"]:
                    joins.append(j)
                col = f"{field['join_list'][-1][2]}.{field['select_key']}"
            else:
                col = f"{field['join_list'][-1][0]}.Id"
        else:
            col = f"{table_name}.{fld_name}"

        where += f"{col} == "
        data = None
        try:
            if self.maps[action] == "Column":
                val_name = f"field_value_column_{idx}"
                data = row[int(self.maps[val_name]) - 1]
            else:
                val_name = f"field_value_constant_{idx}"
                if field["type"] == "Enum" and \
                        type(self.maps[val_name]) is list:
                    data = self.maps[val_name][0]
                else:
                    data = self.maps[val_name]

            if field["type"] == "Select":
                if self.maps[action] == "Constant":
                    where += quoter(str(data["Id"]), "Integer")
                else:
                    where += quoter(str(data))
            else:
                where += quoter(str(data), field["type"])
        except ValueError as err:
            err_msg = f"Row: {row_idx+1} Field: {field['name']} Data: {data} WhereError: {str(err)}"
            error_list.append(err_msg)

        return where, joins, error_list

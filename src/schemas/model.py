import logging
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel

from ..config import config
from ..db import sqa
from ..utils.misc import search_list_of_dict

log = logging.getLogger(__name__)


class Table(BaseModel):
    name: str
    label: str


class TableSchema(Table):
    desc: str
    mapper: str
    primaryKey: List[str]
    companyField: Optional[str] = None
    keyPaths: Optional[List[str]] = None
    key: Optional[str] = None
    componentOf: Optional[Dict[str, Any]] = None
    baseTable: Optional[str] = None
    sum: Optional[List[str]] = None
    sumGroups: Optional[List[str]] = None
    hybrids: Optional[List[Dict[str, Any]]] = None
    parentTables: Optional[List[Dict[str, Any]]] = None
    reprField: Optional[str] = None
    documents: Optional[List[Dict[str, Any]]] = None
    subTables: Optional[List[Dict[str, Any]]] = None
    crud_constraint: Optional[Dict[str, Any]] = None
    crud_options: Optional[Dict[str, Any]] = None
    requiredEntry: Optional[Dict[str, Any]] = None


class Field(BaseModel):
    name: str
    label: str
    alias: Optional[str] = None
    columnLabel: str
    table: str
    type: Optional[str] = None
    length: int = 0
    decimals: int = 0
    numberType: Optional[str] = "number"  # number, currency, percent, string
    textType: Optional[str] = None  # Dict, List, None
    currencyCodeField: Optional[str] = None
    # relationship
    isJoinField: bool = False
    gridSubTable: bool = False
    direction: Optional[str] = None
    isUseList: bool = False
    primaryJoin: Optional[str] = None
    remoteTable: Optional[str] = None
    relations: Optional[List['Field']] = None


# https://pydantic-docs.helpmanual.io/usage/postponed_annotations/#self-referencing-models
Field.update_forward_refs()


class SelectCascade(BaseModel):
    field: str
    value: str


class FieldValuePair(BaseModel):
    field: str
    value: Any


class FieldSchema(Field):
    default: Optional[Any] = None
    actionOn: Optional[List[str]] = None
    requiredIf: Optional[str] = None
    enums: Optional[List[List[str]]] = None
    enum_getter: Optional[str] = None
    sequence: int = 0
    validators: Optional[List[str]] = None
    validator_fields: Optional[List[Dict[str, Any]]] = None
    validator_messages: Optional[List[Dict[str, Any]]] = None
    case: Optional[str] = None
    min: Optional[Any] = None  # int or float
    max: Optional[Any] = None  # int or float

    listFormat: bool = False
    listMin: Optional[int] = None
    listMax: Optional[int] = None

    nullable: bool
    hidden: bool
    modifiable: bool
    displayable: bool
    sortable: bool
    searchable: bool
    draggable: bool
    # lookup
    selectId: Optional[str] = None
    selectKey: Optional[str] = None
    selectColumn: Optional[str] = None
    selectTable: Optional[str] = None
    selectObject: Optional[str] = None
    selectFormat: Optional[List[str]] = None
    selectCascade: Optional[List[SelectCascade]] = None
    selectGetter: Optional[str] = None
    # form field filter
    selectField: Optional[str] = None
    selectFieldValue: Optional[Any] = None
    # table field filter
    selectTableFieldValue: Optional[List[FieldValuePair]] = None


class FormField(BaseModel):
    name: str
    label: str
    alias: Optional[str] = None
    table: str
    field_name: str
    type: str
    length: int = 0
    decimals: int = 0
    numberType: Optional[str] = "number"  # number, currency, percent, string
    textType: Optional[str] = None  # Dict, List, None
    currencyCodeField: Optional[str] = None

    documents: Optional[List[Dict[str, Any]]] = None

    join: bool = False
    join_list: Optional[List[List[Any]]] = None
    reprField: Optional[str] = None

    use_list: bool = False

    default: Any = None
    autoDefault: bool = False   # Select and Enum default to first option
    zero_as_blanks: bool = False

    validValuesKey: Optional[str] = None
    validValues: Optional[List[Any]] = None

    enums: Optional[List[List[str]]] = None
    enum_getter: Optional[str] = None

    actionOn: Optional[Dict[str, Any]] = None
    validators: Optional[List[str]] = None
    validator_fields: Optional[List[Dict[str, Any]]] = None
    validator_messages: Optional[List[Dict[str, Any]]] = None
    case: Optional[str] = None
    min: Optional[Any] = None  # int or float
    max: Optional[Any] = None  # int or float

    listFormat: bool = False
    listMin: Optional[int] = None
    listMax: Optional[int] = None

    required: bool = False
    requiredIf: Optional[str] = None
    requiredIf_message: Optional[str] = None

    dateMode: Optional[str] = "single" # single/range/multiple
    multiple: bool = False # comma separated list - 1 input field
    range: bool = False    # From/To Range - 2 input fields - output is comma separated list of 2 elements

    modifiable: bool = False
    displayable: bool = True
    # lookup
    selectId: Optional[str] = None
    selectKey: Optional[str] = None
    selectColumn: Optional[str] = None
    selectTable: Optional[str] = None
    selectObject: Optional[str] = None
    selectFormat: Optional[List[str]] = None
    selectCascade: Optional[List[SelectCascade]] = None
    selectGetter: Optional[str] = None
    # form field filter
    selectField: Optional[str] = None
    selectFieldValue: Optional[Any] = None
    # table field filter
    selectTableFieldValue: Optional[List[FieldValuePair]] = None

    # file input
    accept: Optional[str] = None
    onLoadHandler: Optional[Any] = None


class GridSubTableType(str, Enum):
    Grid = "GRID"
    Form = "FORM"


class FormPanel(BaseModel):
    table: str
    label: Optional[str] = None
    desc: Optional[str] = None
    baseTable: Optional[str] = None
    keyField: Optional[str] = None
    parent: Optional[str] = None
    field_list: Optional[str] = None
    type: Optional[str] = None
    use_list: bool = False
    id: Optional[str] = None
    actionOn: Optional[List[Dict[str, Any]]] = None
    key: Optional[str] = None
    join_list: Optional[List[List[Any]]] = None
    layout: Optional[Dict[str, Any]] = None
    gridSubTableType: GridSubTableType = GridSubTableType.Grid
    requiredEntry: Optional[Dict[str, Any]] = None
    viewer: Optional[Dict[str, Any]] = None
    loader: Optional[Dict[str, Any]] = None
    documents: Optional[List[Dict[str, Any]]] = None
    subTables: Optional[List[Dict[str, Any]]] = None


class FormSchema(BaseModel):
    stepper_title_fields: Optional[List[str]] = None
    form_panels: List[FormPanel]
    form_fields: List[FormField]


class TableFieldPair(BaseModel):
    dummy_table_name: str
    table_name: str
    field_name: str
    name: Optional[str] = None
    label: Optional[str] = None
    required: Optional[bool] = None
    validators: Optional[List[str]] = None
    validator_fields: Optional[List[Dict[str, Any]]] = None
    validator_messages: Optional[List[Dict[str, Any]]] = None
    default: Optional[Any] = None
    # form field filter
    selectField: Optional[str] = None
    selectFieldValue: Optional[Any] = None
    # table field filter
    selectTableFieldValue: Optional[List[FieldValuePair]] = None


class FormSchemaParams(BaseModel):
    table_field_pair: List[TableFieldPair]

def form_schema(table_name: str,
                form_panels: List[Dict[str, Any]],
                schema: List[Dict[str, Any]],
                main_table: str,
                main_form: Optional[bool] = True,
                except_fields: Optional[List[str]] = None,
                include_fields: Optional[List[str]] = None):
    def get_form_scheme(table_name: str,
                        schema: List[Dict[str, Any]],
                        main_table: str,
                        main_form: Optional[bool] = False,
                        except_fields: Optional[List[str]] = None,
                        include_fields: Optional[List[str]] = None,
                        parent: Optional[str] = None,
                        parent_label: Optional[str] = None):

        if except_fields is None:
            except_fields = list()
        if include_fields is None:
            include_fields = list()

        table_info = sqa.get_table_info(table_name)
        scheme = []
        for s in schema:
            if not s["modifiable"]:
                continue

            if except_fields and s["name"] in except_fields:
                continue
            if include_fields and s["name"] not in include_fields:
                continue

            if "parentTables" in table_info:
                if search_list_of_dict(table_info["parentTables"], "column", s["name"]):
                    if main_form:
                        s["nullable"] = False
                    else:
                        s["modifiable"] = False

            if s["modifiable"]:
                s["displayable"] = False

            if parent is not None:
                name = parent + "." + s["name"]
                # label = parent_label + " " + s["label"]
            else:
                name = s["name"]

            label = s["label"]

            if s["isJoinField"] and s["direction"] == "ONETOMANY":
                t_name = s["remoteTable"]  # s["relations"][0]["table"]

                rel_parent = [obj for obj in form_panels if obj["table"] == table_name]
                # if rel_parent is not use_list then One2One Relationship
                if (((rel_parent and not rel_parent[0]["use_list"]) or not rel_parent) and
                        ((rel_parent and rel_parent[0]["parent"] == main_table) or
                         main_table == table_name) and
                        not any(t["table"] == t_name for t in form_panels)):
                    key = table_name + "." + name
                    join_list = sqa.get_joinlist(key)
                    # join_list = [(table, key, joinTable, alias, nullable, cardinality),..]
                    # key Users.Personal.Emails
                    # key.split(".",1)[-1] Personal.Emails
                    info = sqa.get_table_info(t_name)
                    sub_table_type = "GRID" if s["isUseList"] else "FORM"
                    form_panels.append(dict(table=t_name,
                                            label=info["label"],
                                            desc=info["desc"],
                                            baseTable=info["baseTable"],
                                            keyField=info["key"],
                                            parent=table_name,
                                            type=s["direction"],
                                            use_list=s["isUseList"],
                                            id=key.split(".", 1)[-1],
                                            actionOn=list(),
                                            key=key,
                                            join_list=join_list,
                                            field_list=name,
                                            gridSubTableType=sub_table_type,
                                            viewer=info["viewer"] if "viewer" in info else None,
                                            loader=info["loader"] if "loader" in info else None,
                                            requiredEntry=s["requiredEntry"],
                                            documents=info["documents"] if "documents" in info else None,
                                            subTables=info["subTables"] if "subTables" in info else None
                                            )
                                       )

                schem = get_form_scheme(t_name, s["relations"], main_table,
                                        False,
                                        except_fields=except_fields,
                                        include_fields=include_fields,
                                        parent=name,
                                        parent_label=label)

                for sc in schem:
                    if sc["actionOn"]:
                        form_panels[-1]["actionOn"].append(sc["actionOn"])
                    sche = form_field_schema(sc, sc["name"], sc["field_name"])
                    if sche:
                        scheme.append(sche)
            else:
                if parent is None and s["actionOn"]:
                    form_panels[0]["actionOn"].append(s["actionOn"])
                sche = form_field_schema(s, name, s["name"], label)
                if sche:
                    scheme.append(sche)

        return scheme

    return get_form_scheme(table_name, schema, main_table, main_form,
                           except_fields=except_fields,
                           include_fields=include_fields)


def form_field_schema(scheme: Dict[str, Any],
                      name: str = None,
                      field_name: str = None,
                      label: str = None):
    schema = dict()

    if name is None:
        name = scheme["name"]
    if label is None:
        label = scheme["label"]
    if field_name is None:
        field_name = scheme["name"]

    required = False
    if "nullable" in scheme:
        required = not scheme["nullable"]
    elif "required" in scheme:
        required = scheme["required"]

    use_list = False
    if "isUseList" in scheme:
        use_list = scheme["isUseList"]
    elif "use_list" in scheme:
        use_list = scheme["use_list"]

    if ("isJoinField" in scheme and scheme["isJoinField"]) or\
            ("join" in scheme and scheme["join"]):
        if "selectKey" in scheme and scheme["selectKey"] is not None:
            join_list = sqa.get_joinlist(scheme["table"] + "." + scheme["name"])
            # join_list = [(table, key, joinTable, alias, nullable),..]
            info = sqa.get_table_info(join_list[0][2])
            schema = dict(name=name,
                          table=scheme["table"],
                          field_name=field_name,
                          join=True,
                          join_list=join_list,
                          reprField=info["reprField"] if "reprField" in info else None,
                          use_list=use_list,
                          type="Select",
                          numberType="number",
                          textType=None,
                          currencyCodeField=None,
                          documents=None,
                          length=scheme["length"],
                          decimals=scheme["decimals"],
                          default=scheme["default"],
                          enums=scheme["enums"],
                          enum_getter=scheme["enum_getter"],
                          actionOn=scheme["actionOn"],
                          label=label,
                          alias=scheme["alias"],
                          validators=scheme["validators"],
                          validator_fields=scheme["validator_fields"],
                          validator_messages=scheme["validator_messages"],
                          case=scheme["case"],
                          min=scheme["min"],
                          max=scheme["max"],
                          listFormat=scheme["listFormat"],
                          listMin=scheme["listMin"],
                          listMax=scheme["listMax"],
                          modifiable=scheme["modifiable"],
                          displayable=scheme["displayable"],
                          required=required,
                          requiredIf=scheme["requiredIf"],
                          selectId=scheme["selectId"],
                          selectKey=scheme["selectKey"],
                          selectColumn=scheme["selectColumn"],
                          selectTable=scheme["selectTable"],
                          selectObject=scheme["selectObject"],
                          selectFormat=scheme["selectFormat"],
                          selectField=scheme["selectField"],
                          selectFieldValue=scheme["selectFieldValue"],
                          selectTableFieldValue=scheme["selectTableFieldValue"],
                          selectGetter=scheme["selectGetter"],
                          selectCascade=scheme["selectCascade"])
    else:
        schema = dict(name=name,
                      table=scheme["table"],
                      field_name=field_name,
                      join=False,
                      join_list=None,
                      reprField=None,
                      use_list=False,
                      type=scheme["type"],
                      numberType=scheme["numberType"],
                      textType=scheme["textType"],
                      currencyCodeField=scheme["currencyCodeField"],
                      documents=scheme["documents"],
                      length=scheme["length"],
                      decimals=scheme["decimals"],
                      default=scheme["default"],
                      enums=scheme["enums"],
                      enum_getter=scheme["enum_getter"],
                      actionOn=scheme["actionOn"],
                      label=label,
                      alias=scheme["alias"],
                      validators=scheme["validators"],
                      validator_fields=scheme["validator_fields"],
                      validator_messages=scheme["validator_messages"],
                      case=scheme["case"],
                      min=scheme["min"],
                      max=scheme["max"],
                      listFormat=scheme["listFormat"],
                      listMin=scheme["listMin"],
                      listMax=scheme["listMax"],
                      modifiable=scheme["modifiable"],
                      displayable=scheme["displayable"],
                      required=required,
                      requiredIf=scheme["requiredIf"],
                      selectId=scheme["selectId"],
                      selectKey=scheme["selectKey"],
                      selectColumn=scheme["selectColumn"],
                      selectTable=scheme["selectTable"],
                      selectObject=scheme["selectObject"],
                      selectFormat=scheme["selectFormat"],
                      selectField=scheme["selectField"],
                      selectFieldValue=scheme["selectFieldValue"],
                      selectTableFieldValue=scheme["selectTableFieldValue"],
                      selectGetter=scheme["selectGetter"],
                      selectCascade=scheme["selectCascade"])

    return schema


class GridTable(BaseModel):
    table: str
    label: str
    desc: Optional[str] = None
    use_list: bool = False
    baseTable: Optional[str] = None
    parent: Optional[str] = None
    field_list: Optional[str] = None
    join_list: Optional[List[List[Any]]] = None
    gridSubTableType: GridSubTableType = GridSubTableType.Grid
    viewer: Optional[Dict[str, Any]] = None
    loader: Optional[Dict[str, Any]] = None
    documents: Optional[List[Dict[str, Any]]] = None
    subTables: Optional[List[Dict[str, Any]]] = None
    crud_constraint: Optional[Dict[str, Any]] = None
    crud_options: Optional[Dict[str, Any]] = None
    requiredEntry: Optional[Dict[str, Any]] = None


class GridField(FormField):
    column_label: str
    child_name: str
    sortable: bool = False
    searchable: bool = False
    draggable: bool = True
    visible: bool = False
    sticky: bool = False
    cell_function: Optional[str] = None
    colspan: Optional[int] = None
    grid_width_value: Optional[int] = None


class GridSchema(BaseModel):
    grid_tables: List[GridTable]
    grid_fields: List[GridField]


def grid_schema(schema, table_name, grid_tables, main_table,
                except_fields=[],
                sum_groups=[],
                sum_fields=[],
                parent=None, parent_label=None, parent_child=None):
    try:
        grid_column_header = config["grid"]["column_header"]
    except:
        grid_column_header = "column_label"

    scheme = list()
    for s in schema:
        if not s["displayable"]:
            continue

        if s["name"] in except_fields:
            continue

        # name and child_name are used by the grid filter function
        if parent is not None:
            name = parent + "." + s["name"]
            if parent_label is not None:
                label = parent_label + " " + s["label"]
                if parent_child is None:
                    child_name = name
                else:
                    child_name = parent_child + "." + s["name"]
            else:
                child_name = s["name"]
                if "." in parent:
                    label = parent.rsplit(".", 1)[1] + " " + s["label"]
                else:
                    label = parent + " " + s["label"]
        else:
            name = s["name"]
            label = s["label"]
            if parent_child is None:
                child_name = name
            else:
                child_name = parent_child + "." + name

        if s["isJoinField"]:
            t_name = table_name
            schem = None
            if (table_name == main_table and
                    s["isUseList"] and s["direction"] == "ONETOMANY"):
                t_name = s["remoteTable"]  # s["relations"][0]["table"]
                if not any(t["table"] == t_name for t in grid_tables):
                    join_list = sqa.get_joinlist(table_name + "." + name)
                    # join_list element = (table, "key", "joinTable", "alias", "nullable", "cardinality")
                    if join_list[0][5] != "n:1":  # table of main_table
                        info = sqa.get_table_info(t_name)
                        grid_tables.append(dict(table=t_name,
                                                use_list=True,
                                                label=info["label"],
                                                desc=info["desc"],
                                                parent=table_name,
                                                field_list=name,
                                                join_list=join_list,
                                                baseTable=info["baseTable"],
                                                gridSubTableType="GRID",
                                                viewer=info["viewer"] if "viewer" in info else None,
                                                loader=info["loader"] if "loader" in info else None,
                                                documents=info["documents"] if "documents" in info else None,
                                                subTables=info["subTables"] if "subTables" in info else None,
                                                crud_constraint=info["crud_constraint"] if "crud_constraint" in info else None,
                                                crud_options=info["crud_options"] if "crud_options" in info else None,
                                                requiredEntry=s["requiredEntry"]
                                                )
                                           )
                        continue
            elif table_name == main_table and s["gridSubTable"]:
                t_name = s["remoteTable"]  # s["relations"][0]["table"]
                if not any(t["table"] == t_name for t in grid_tables):
                    join_list = sqa.get_joinlist(table_name + "." + name)
                    info = sqa.get_table_info(t_name)
                    sub_table_type = "GRID" if s["isUseList"] else "FORM"
                    grid_tables.append(dict(table=t_name,
                                            use_list=True,
                                            label=info["label"],
                                            desc=info["desc"],
                                            parent=table_name,
                                            field_list=name,
                                            join_list=join_list,
                                            baseTable=info["baseTable"],
                                            gridSubTableType=sub_table_type,
                                            viewer=info["viewer"] if "viewer" in info else None,
                                            loader=info["loader"] if "loader" in info else None,
                                            documents=info["documents"] if "documents" in info else None,
                                            subTables=info["subTables"] if "subTables" in info else None,
                                            crud_constraint=info["crud_constraint"] if "crud_constraint" in info else None,
                                            crud_options=info["crud_options"] if "crud_options" in info else None,
                                            requiredEntry=s["requiredEntry"]
                                            )
                                       )
                    schem = grid_schema(s["relations"], t_name, grid_tables,
                                        main_table, except_fields,
                                        sum_groups, sum_fields,
                                        name)
            elif s["remoteTable"] != main_table:
                schem = grid_schema(s["relations"], t_name, grid_tables,
                                    main_table, except_fields,
                                    sum_groups, sum_fields,
                                    name, label, child_name)

            if schem is not None:
                for sc in schem:
                    sche = form_field_schema(sc, sc["name"], sc["field_name"])
                    if sche:
                        grid_scheme = sche
                        grid_scheme["column_label"] = sc["column_label"]
                        grid_scheme["child_name"] = sc["child_name"]
                        grid_scheme["modifiable"] = sc["modifiable"]
                        grid_scheme["sortable"] = sc["sortable"]
                        grid_scheme["searchable"] = sc["searchable"]
                        grid_scheme["draggable"] = sc["draggable"]
                        grid_scheme["visible"] = True
                        grid_scheme["table"] = sc["table"]
                        scheme.append(grid_scheme)
        else:
            if sum_groups and name not in sum_groups:
                continue

            if grid_column_header == "label":
                column_label = label
            else:
                column_label = s["columnLabel"]

            sche = form_field_schema(s, name, s["name"], label)
            if sche:
                grid_scheme = sche
                grid_scheme["column_label"] = column_label
                grid_scheme["child_name"] = child_name
                grid_scheme["modifiable"] = s["modifiable"]
                grid_scheme["sortable"] = s["sortable"]
                grid_scheme["searchable"] = s["searchable"]
                grid_scheme["draggable"] = s["draggable"]
                grid_scheme["visible"] = True
                grid_scheme["sticky"] = False
                grid_scheme["table"] = table_name
                if sum_groups and name in sum_groups:
                    grid_scheme["sortable"] = False
                if sum_fields and name in sum_fields:
                    grid_scheme["sticky"] = True
                scheme.append(grid_scheme)

    return scheme

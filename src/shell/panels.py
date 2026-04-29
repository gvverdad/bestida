from src.db import db_session, sqa
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import class_mapper, RelationshipProperty

from src.schemas.model import FormSchema, FormField, FormPanel, GridSubTableType

# run "./shellserver src.shell.panels development.ini" in /home/gvv/Projects/bestida
def run(app=None):
    session = db_session()
    table_name = "WarehouseAreas"

    panels = list()
    fields = list()
    """
    info = sqa.get_table_info(table_name)
    panels.append(dict(table=table_name,
                       label=info["label"],
                       desc=info["desc"],
                       baseTable=info["baseTable"],
                       keyField=info["key"],
                       parent=None,
                       type=None,
                       use_list=False,
                       id=None,
                       actionOn=list(),
                       key=None,
                       joinlist=list(),
                       subTableType="GRID",
                       document=info["document"] if "document" in info else None
                       ))
    """
    get_panels(table_name, panels, fields, table_name, ["versions"])

    for panel in panels:
        print(panel)

    for field in fields:
        print(field)

def get_fields(table_name, fields, key, except_fields=[]):
    table_class = sqa.get_model(table_name)
    mapper = class_mapper(table_class)

    for column in inspect(table_class).columns:
        if column.key in except_fields:
            continue
        if "modifiable" in column.info and not column.info["modifiable"]:
            continue
        if "hidden" in column.info and column.info["hidden"]:
            continue

        name = column.name
        use_list = False
        join=False
        join_list = None
        for fk in column.foreign_keys:
            # name = ItemWarehouse_Id
            fKey = str(fk.column)  # Warehouses.Id
            sufix = ("_%s" % fKey.split(".")[-1])  # _Id
            if sufix in name:
                name = name.replace(sufix, "").strip()  # ItemWarehouse
                prop = mapper.attrs.get(name)
                join=True
                use_list = prop.uselist
                join_list = sqa.get_joinlist(f"{table_class.__table__.name}.{name}")
                break

        if len(key.split(".")) == 1:
            key_string = name
        else:
            key_string = f"{key.split('.', 1)[-1]}.{name}"

        fld_type =  column.type.__class__.__name__
        if "choices" in column.info:
            fld_type = "Enum"
        elif "selectKey" in column.info and column.info["selectKey"] is not None:
            fld_type = "Select"

        fields.append(FormField(
            name=key_string,
            label=column.info["label"] if "label" in column.info else column.key,
            table=table_class.__table__.name,
            type=fld_type,
            listFormat=column.info["listFormat"] if "listFormat" in column.info else False,
            case=column.info["case"] if "case" in column.info else None,
            use_list=use_list,
            join=join,
            join_list=join_list,
            field_name=name
        ))


def get_panels(table_name, panels, fields, key, except_fields=[]):

    get_fields(table_name, fields, key, except_fields)

    table_class = sqa.get_model(table_name)
    relationships = inspect(table_class).relationships
    for rel_name, rel in relationships.items():
        if rel_name in except_fields:
            continue
        if "hidden" in rel.info and rel.info["hidden"]:
            continue
        if rel.direction.name != "ONETOMANY":
            continue
        try:
            rel_col = table_class.__table__.columns[f"{rel_name}_Id"]
            if "modifiable" in rel_col.info and not rel_col.info["modifiable"]:
                continue
        except:
            pass
        key_string = f"{key}.{rel_name}"
        info = sqa.get_table_info(rel.mapper.class_.__tablename__)
        join_list = sqa.get_joinlist(f"{table_class.__table__}.{rel_name}")

        panels.append(FormPanel(table=rel.mapper.class_.__tablename__,
                        label=info["label"],
                        desc=info["desc"],
                        baseTable=info["baseTable"],
                        keyField=info["key"],
                        parent=table_name,
                        type=rel.direction.name,
                        use_list=rel.uselist,
                        # Users.Personal.Address.State after split is Personal.Address.State
                        # remove main table
                        id=key_string.split(".", 1)[-1],
                        actionOn=list(),
                        key=key_string,
                        join_list=join_list,
                        field_list=rel_name,
                        gridSubTableType=GridSubTableType.Grid if rel.uselist else GridSubTableType.Form,
                        requiredEntry=rel.info["requiredEntry"] if "requiredEntry" in rel.info else None,
                        document=info["document"] if "document" in info else None
                        )
                   )
        get_fields(rel.mapper.class_.__tablename__, fields, key_string, except_fields)
        # ONETOONE - dive one level down
        if not rel.uselist:
            get_panels(rel.mapper.class_.__tablename__, panels, fields, key_string, except_fields)

# run from ide
if __name__ == '__main__':
    run()

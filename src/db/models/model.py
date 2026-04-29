import datetime, ast, logging, json, copy

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import mapper as _mapper
from sqlalchemy.orm import class_mapper, object_session
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.elements import Label
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOONE, MANYTOMANY
from sqlalchemy_utils import get_hybrid_properties

from ...utils.misc import search_list_of_dict

log = logging.getLogger(__name__)


Models = {}


def mapper(cls, table=None, *arg, **kw):
    Models[table.name] = dict(table=table, klass=cls)
    return _mapper(cls, table, *arg, **kw)


def sorted_props(class_, except_fields=[], schema_except_fields=[]):

    mapper = class_mapper(class_)

    props = []
    if mapper.with_polymorphic_mappers:
        # polymorphic Base
        for m in mapper._polymorphic_properties:
            if m.key in schema_except_fields:
                continue
            if m.key in except_fields:
                continue
            props.append(m)
    else:
        for m in list(mapper.iterate_properties):
            if m.key in schema_except_fields:
                continue
            if m.key in except_fields:
                continue
            props.append(m)

    def _order_for_prop(prop):
        try:
            if isinstance(prop, ColumnProperty):
                return prop.columns[0]._creation_order
            else:
                return prop._creation_order
        except:  # column_property
            return 99999

    # http://www.sqlalchemy.org/trac/wiki/UsageRecipes/IteratePropsInCreationOrder
    props.sort(key=_order_for_prop)

    return mapper, props


class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__        
    
    #Id = Column(Integer, Sequence("%s_Id_Seq" % cls.__name__), primary_key=True, info=dict(label="RecordId"))
    #Id = Column(Integer, autoincrement=True, primary_key=True, info=dict(label="RecordId"))
    
    def __str__(self):
        return str(vars(self))

    # python function default value is evaluated and stored once when the function is defined.
    # It is not re-checked each time the function is called
    # NOTE: depth is MUTABLE
    # this is a recursive function
    # so call this function with at least depth parameter initialized
    def data_to_dict(self, except_fields=None, depth=1,
                     audit=False, table_class=None,
                     tuple_choice=True, choice_key=False,
                     text_as_string=False, m2m_merge=False, one2m_list=True,
                     ignore_calc_fields=False, dump=False,
                     except_rels=None):

        if except_fields is None:
            except_fields = list()

        if except_rels is None:
            except_rels = list()

        mapper = self.__mapper__
        table_name = self.__table__.name  # Programs
        columns = self.__mapper__.columns.keys()
        relationships = self.__mapper__.relationships.keys()

        audit_relationships = None
        if audit and table_class is not None:
            audit_relationships = inspect(table_class).relationships

        data = dict()
        # columns
        for key in columns:
            if key.startswith("_"):
                continue
            if key in except_fields:
                continue

            name = table_name + "." + key
            if name in except_fields:
                continue

            val = getattr(self, key, None)

            if audit_relationships is not None:
                if key.endswith("_Id"):
                    rel_name = key.replace("_Id", "").strip()
                    if rel_name in audit_relationships:
                        if rel_name in except_rels:
                            continue

                        rel_class = audit_relationships[rel_name].mapper.class_
                        rec = object_session(self).query(rel_class).get(val)
                        if rec is not None:
                            rel = audit_relationships[rel_name]
                            og_except_rels = copy.deepcopy(except_rels)
                            og_except_rels.append(rel_name)  # avoid circular data
                            if rel.uselist:
                                if rel.direction is MANYTOMANY:
                                    if m2m_merge:
                                        # TODO: sort M2M by primary key Id (ie. company_group_table.Id)
                                        # Merge M2M
                                        data[rel_name] = dict()
                                        for vv in rec:
                                            obj = vv.data_to_dict(except_fields=except_fields,
                                                                  depth=1,
                                                                  tuple_choice=tuple_choice,
                                                                  choice_key=choice_key, text_as_string=text_as_string,
                                                                  m2m_merge=m2m_merge, one2m_list=one2m_list,
                                                                  ignore_calc_fields=ignore_calc_fields,
                                                                  dump=dump,
                                                                  except_rels=og_except_rels
                                                                  )
                                            for kk, vvv in obj.items():
                                                if kk not in data[key]:
                                                    data[rel_name][kk] = []
                                                data[rel_name][kk].append(vvv)
                                    else:
                                        data[rel_name] = [vv.data_to_dict(except_fields=except_fields,
                                                                     depth=1,
                                                                     tuple_choice=tuple_choice,
                                                                     choice_key=choice_key,
                                                                     text_as_string=text_as_string,
                                                                     m2m_merge=m2m_merge,
                                                                     one2m_list=one2m_list,
                                                                     ignore_calc_fields=ignore_calc_fields,
                                                                     dump=dump,
                                                                     except_rels=og_except_rels
                                                                     )
                                                     for vv in rec]
                                elif one2m_list:
                                    data[rel_name] = [vv.data_to_dict(except_fields=except_fields,
                                                                      depth=1,
                                                                      tuple_choice=tuple_choice,
                                                                      choice_key=choice_key, text_as_string=text_as_string,
                                                                      m2m_merge=m2m_merge, one2m_list=one2m_list,
                                                                      ignore_calc_fields=ignore_calc_fields,
                                                                      dump=dump,
                                                                      except_rels=og_except_rels
                                                                     )
                                                 for vv in rec]
                            else:
                                data[rel_name] = rec.data_to_dict(except_fields=except_fields,
                                                                  depth=1,
                                                                  tuple_choice=tuple_choice,
                                                                  choice_key=choice_key, text_as_string=text_as_string,
                                                                  m2m_merge=m2m_merge, one2m_list=one2m_list,
                                                                  ignore_calc_fields=ignore_calc_fields,
                                                                  dump=dump,
                                                                  except_rels=og_except_rels
                                                                 )

            col = self.__mapper__.columns[key]
            #if not dump and "hidden" in col.info and col.info["hidden"]:
            #    continue
            if isinstance(val, datetime.datetime):
                # see schemas.datasource.convert_data2 DateTime
                # val is utc and stored as naive datetime
                # val is naive datetime. add Z to look like utc
                data[key] = val.isoformat() + "Z"
            elif isinstance(val, (datetime.date, datetime.time)):
                data[key] = val.isoformat()
            elif col.type.__class__.__name__ == "Integer":
                if val is None:
                    data[key] = 0
                else:
                    data[key] = val
            elif col.type.__class__.__name__ == "BigInteger":
                if val is None:
                    data[key] = 0
                else:
                    data[key] = val
            elif col.type.__class__.__name__ == "Numeric":
                if val is None:
                    data[key] = "0"
                else:
                    data[key] = str(val)
            elif col.type.__class__.__name__ == "Text":
                if "textType" in col.info and col.info["textType"] is not None:
                    try:
                        data[key] = json.loads(val)  # convert to dict if ever
                    except:
                        try:
                            data[key] = ast.literal_eval(val)  # convert to dict if ever
                        except:
                            data[key] = val
                elif ("listFormat" in col.info and col.info["listFormat"]) or \
                        not text_as_string:
                    try:
                        data[key] = json.loads(val)  # convert to dict if ever
                    except:
                        try:
                            data[key] = ast.literal_eval(val)  # convert to dict if ever
                        except:
                            data[key] = val
                else:
                    data[key] = val
            elif "choices" in col.info:
                if not tuple_choice and choice_key:
                    data[key] = val
                elif type(col.info["choices"]) is list:
                    for l in col.info["choices"]:
                        if val == l[0]:
                            if tuple_choice:
                                data[key] = l
                            elif choice_key:
                                # here for clarity only
                                data[key] = l[0]
                            else:
                                data[key] = l[1]
                            break
                else:
                    # must be a function
                    # unpack tuple - kk, vv
                    # *vv for tuple[Any, Any, ...]
                    for kk, *vv in col.info["choices"]():
                        if val == kk:
                            if tuple_choice:
                                data[key] = (kk, vv)
                            elif choice_key:
                                # here for clarity only
                                data[key] = kk
                            else:
                                data[key] = vv
                            break
            else:
                data[key] = val

        # hybrid columns
        if not ignore_calc_fields:
            for k, v in get_hybrid_properties(mapper).items():
                key = v.__name__

                if key in except_fields:
                    continue
                name = table_name + "." + key
                if name in except_fields:
                    continue

                val = getattr(self, key, None)
                if isinstance(val, datetime.datetime):
                    # see schemas.datasource.convert_data2 DateTime
                    # val is utc and stored as naive datetime
                    # val is naive datetime. add Z to look like utc
                    data[key] = val.isoformat() + "Z"  # utc
                elif isinstance(val, (datetime.date, datetime.time)):
                    data[key] = val.isoformat()
                else:
                    data[key] = val

        # relationships
        for key in relationships:
            if key in except_fields:
                continue
            if key in except_rels:
                continue
            name = table_name + "." + key
            if name in except_fields:
                continue

            rel = self.__mapper__.relationships[key]
            if not dump and "hidden" in rel.info and rel.info["hidden"]:
                continue

            level = depth
            # depth overrides
            if "depth" in rel.info:
                # relationship depth
                if depth == 0 or rel.info["depth"] == 0:
                    level = rel.info["depth"]

            # sqlalchemy-continuum transaction/version_parent table
            if table_name == "transaction" and key == "user":
                level = 1
            elif key == "version_parent":
                level += 1

            #fld_list = [f.split(".", 1)[1] for f in field_list if "." in f and f.split(".")[0] == key]
            try:
                name = "{}_Id".format(key)  # CreateOpId to CreateOpId_Id
                col = self.__mapper__.columns[name]
                if dump:
                    continue
                elif "hidden" in col.info and col.info["hidden"]:
                    continue

                if level == 0:
                    if "depth" in col.info:
                        # override depth
                        level = col.info["depth"]
            except:
                # not Many2One
                if dump and "dump" in rel.info and not rel.info["dump"]:
                    continue
                if not dump and "hidden" in rel.info and rel.info["hidden"]:
                    continue
                if dump and "dumpFields" in rel.info:
                    fld_list = rel.info["dumpFields"]

            if level > 0:
                rec = getattr(self, key, None)
                if rec is not None:
                    rel = self.__mapper__.relationships[key]
                    og_except_rels = copy.deepcopy(except_rels)
                    og_except_rels.append(key)  # avoid circular data
                    if rel.uselist:
                        if rel.direction is MANYTOMANY:
                            if m2m_merge:
                                # TODO: sort M2M by primary key Id (ie. company_group_table.Id)
                                # Merge M2M
                                data[key] = dict()
                                for vv in rec:
                                    obj = vv.data_to_dict(except_fields=except_fields,
                                                          depth=level-1,
                                                          audit=audit,
                                                          table_class=table_class,
                                                          tuple_choice=tuple_choice,
                                                          choice_key=choice_key, text_as_string=text_as_string,
                                                          m2m_merge=m2m_merge, one2m_list=one2m_list,
                                                          ignore_calc_fields=ignore_calc_fields,
                                                          dump=dump,
                                                          except_rels=og_except_rels
                                                          )
                                    for kk, vvv in obj.items():
                                        if kk not in data[key]:
                                            data[key][kk] = []
                                        data[key][kk].append(vvv)
                            else:
                                data[key] = [vv.data_to_dict(except_fields=except_fields,
                                                             depth=level-1,
                                                             audit=audit,
                                                             table_class=table_class,
                                                             tuple_choice=tuple_choice,
                                                             choice_key=choice_key,
                                                             text_as_string=text_as_string,
                                                             m2m_merge=m2m_merge,
                                                             one2m_list=one2m_list,
                                                             ignore_calc_fields=ignore_calc_fields,
                                                             dump=dump,
                                                             except_rels=og_except_rels
                                                             )
                                             for vv in rec
                                            ]
                        elif one2m_list:
                            data[key] = [vv.data_to_dict(except_fields=except_fields,
                                                         depth=level-1,
                                                         audit=audit,
                                                         table_class=table_class,
                                                         tuple_choice=tuple_choice,
                                                         choice_key=choice_key, text_as_string=text_as_string,
                                                         m2m_merge=m2m_merge, one2m_list=one2m_list,
                                                         ignore_calc_fields=ignore_calc_fields,
                                                         dump=dump,
                                                         except_rels=og_except_rels
                                                         )
                                         for vv in rec
                                         ]
                    else:
                        data[key] = rec.data_to_dict(except_fields=except_fields,
                                                     depth=level-1,
                                                     audit=audit,
                                                     table_class=table_class,
                                                     tuple_choice=tuple_choice,
                                                     choice_key=choice_key, text_as_string=text_as_string,
                                                     m2m_merge=m2m_merge, one2m_list=one2m_list,
                                                     ignore_calc_fields=ignore_calc_fields,
                                                     dump=dump,
                                                     except_rels=og_except_rels
                                                     )

        return data

    def get_property_by_name(self, name):
        mapper = class_mapper(self.__class__)
        if "." in name:
            col = name.split(".", 1)
            prop = mapper.get_property(col[0])
            if len(col) == 2:
                try:
                    prop = Models[list(prop.remote_side)[0].table.name]["klass"]().get_property_by_name(col[1])
                except:
                    # child table not the association table for Many2Many
                    prop = Models[prop.target.name]["klass"]().get_property_by_name(col[1])
        else:
            prop = mapper.get_property(name)

        return prop

    # python function default value is evaluated and stored once when the function is defined.
    # It is not re-checked each time the function is called
    # NOTE: depth, dup_table_list, and schema_except_fields are MUTABLE
    # this is a recursive function
    # so call this function with at least the MUTABLE parameters initialized
    def schema_to_dict(self, except_fields=[],
                       depth=1,
                       audit=False,
                       table_class=None,
                       remove_duplicate_tables=False,
                       dup_table_list=[],
                       schema_except_fields=[],
                       searchable=None):
        """
            nested table schema to dict for json dumps
        """
        mapper, props = sorted_props(self.__class__, except_fields, schema_except_fields)
        table = mapper.local_table  # sqlalchemy.schema.Table

        audit_relationships = None
        if audit and table_class is not None:
            audit_relationships = inspect(table_class).relationships
            #for audit_name, audit_rel in audit_relationships.items():
            #    related_class = audit_rel.mapper.class_
            #    print("model.Base.schema_to_dict audit_rel:", audit_name, audit_rel, audit_rel.direction.name,
            #          hasattr(related_class, '__versioned__'))

        if remove_duplicate_tables:
            if len(dup_table_list) == 0:
                dup_table_list.append(table.name)

        polymorphicBase = False
        actionOn = None

        if mapper.with_polymorphic_mappers:
            polymorphicBase = True
            actionOn = {}
            actionOn["baseFieldName"] = mapper.polymorphic_on.name
            for p in props:
                if isinstance(p, ColumnProperty):
                    colprop = p.columns[0]
                    if colprop != mapper.polymorphic_on:
                        continue

                    pm = mapper.polymorphic_map
                    for k in pm.keys():
                        if k == mapper.polymorphic_identity:
                            continue
                        actionOn[k] = {}
                        actionOn[k]["onFields"] = []
                        actionOn[k]["offFields"] = []
                        # on fields
                        pmdict = Models[pm[k].local_table.name]["klass"]().schema_to_dict(except_fields=except_fields,
                                                                                          depth=0,
                                                                                          audit=False,
                                                                                          remove_duplicate_tables=False,
                                                                                          dup_table_list=[],
                                                                                          schema_except_fields=[]
                                                                                          )
                        for pmd in pmdict:
                            if pmd["table"] == pm[k].local_table.name and \
                                    pmd["modifiable"] and pmd["displayable"]:
                                actionOn[k]["onFields"].append(pmd["name"])
                        # off fields
                        for kk in mapper.polymorphic_map.keys():
                            if kk == mapper.polymorphic_identity:
                                continue
                            if kk == k:
                                continue
                            pmdict = Models[pm[kk].local_table.name]["klass"]().schema_to_dict(except_fields=except_fields,
                                                                                               depth=0,
                                                                                               audit=False,
                                                                                               remove_duplicate_tables=False,
                                                                                               dup_table_list=[],
                                                                                               schema_except_fields=[])
                            for pmd in pmdict:
                                if pmd["table"] != table.name and \
                                        pmd["modifiable"] and pmd["displayable"]:
                                    actionOn[k]["offFields"].append(pmd["name"])
                    break

        schema = list()
        for p in props:
            col = dict()

            if isinstance(p, ColumnProperty):
                colprop = p.columns[0]
                isFk = False
                audit_name = None
                level = depth

                if isinstance(colprop, Label):  # column_property
                    colprop = p
                    col["type"] = colprop.info["type"] if "type" in colprop.info else "String"
                    col["nullable"] = True
                else:  # Column
                    name = colprop.name
                    col["nullable"] = colprop.nullable

                    if audit_relationships is not None:
                        if p.key.endswith("_Id"):
                            rel_name = p.key.replace("_Id", "").strip()
                            if rel_name in audit_relationships:
                                audit_name = rel_name  # CreateOpId
                                name = rel_name
                                isFk = True

                    if not isFk:
                        for fk in colprop.foreign_keys:
                            fKey = str(fk.column)  # CreateOpId_Id
                            sufix = ("_%s" % fKey.split(".")[-1])
                            # sqlalchemy-continuum transaction table
                            if table.name == "transaction" and p.key == "user_id":
                                name = "user"
                                isFk = True
                                level = 1
                                break
                            elif sufix in name:
                                name = name.replace(sufix, "").strip()  # CreateOpId
                                isFk = True
                                break

                if isFk:
                    if "depth" in colprop.info:
                        if depth == 0 or colprop.info["depth"] == 0:
                            # FK Overrides depth
                            level = colprop.info["depth"]
                    if level < 1:
                        continue

                col["name"] = p.key
                try:
                    col["table"] = table.name  # colprop.table.name if not polymorphicBase else table.name

                    col["type"] = colprop.type.__class__.__name__
                    try:
                        # ColumnDefault() callable
                        col["default"] = colprop.default.arg.__wrapped__()
                    except Exception as err:
                        try:
                            # ColumnDefault() value
                            if "choices" in colprop.info:
                                if type(colprop.info["choices"]) is list:
                                    for l in colprop.info["choices"]:
                                        if colprop.default.arg == l[0]:
                                            col["default"] = l
                                            break
                                else:
                                    # must be a function
                                    # unpack tuple - kk, vv
                                    # *vv for tuple[Any, Any, ...]
                                    for kk, *vv in colprop.info["choices"]():
                                        if colprop.default.arg == kk:
                                            col["default"] = [kk] + list(vv)
                                            break
                            elif callable(colprop.default.arg):
                                col["default"] = None
                            else:
                                col["default"] = colprop.default.arg
                        except:
                            col["default"] = None
                    if isinstance(col["default"], datetime.datetime):
                        col["default"] = col["default"].isoformat() + "Z"  # utc
                    elif isinstance(col["default"], (datetime.date, datetime.time)):
                        col["default"] = col["default"].isoformat()

                except: # column_property
                    pass

                col["numberType"] = colprop.info["numberType"] if "numberType" in colprop.info else "number"
                col["textType"] = colprop.info["textType"] if "textType" in colprop.info else None
                col["currencyCodeField"] = colprop.info["currencyCodeField"] if "currencyCodeField" in colprop.info else None
                col["enums"] = None
                col["enum_getter"] = None
                if "choices_getter" in colprop.info:
                    col["enum_getter"] = colprop.info["choices_getter"]
                col["actionOn"] = None
                if "choices" in colprop.info:
                    col["type"] = "Enum"
                    if type(colprop.info["choices"]) is list:
                        col["enums"] = []
                        for l in colprop.info["choices"]:
                            col["enums"].append(l)  # tuple (k, v)
                    elif col["enum_getter"] is None:  # must be a server function
                        col["enums"] = []
                        for k, v in colprop.info["choices"]():
                            col["enums"].append((k, v))
                    if "actionOn" in colprop.info:
                        try:
                            col["actionOn"] = json.loads(colprop.info["actionOn"]) # convert string to dict
                        except:
                            col["actionOn"] = ast.literal_eval(colprop.info["actionOn"])  # convert string to dict
                elif col["type"] == "Enum":
                    col["enums"] = []
                    for k in colprop.type.enums:
                        # key, value pair
                        col["enums"].append((k, k))
                    if "actionOn" in colprop.info:
                        try:
                            col["actionOn"] = json.loads(colprop.info["actionOn"]) # convert string to dict
                        except:
                            col["actionOn"] = ast.literal_eval(colprop.info["actionOn"])  # convert string to dict
                elif polymorphicBase and colprop == mapper.polymorphic_on:
                    col["type"] = "Enum"
                    col["enums"] = []
                    col["actionOn"] = actionOn
                    pmKeys = mapper.polymorphic_map.keys()
                    if "polymorphic_sort" in colprop.info:
                        pmKeys = colprop.info["polymorphic_sort"]
                    for k in pmKeys:
                        if k == mapper.polymorphic_identity:
                            continue
                        # key, value pair
                        col["enums"].append((k, k))
                elif "actionOn" in colprop.info:
                    try:
                        col["actionOn"] = json.loads(colprop.info["actionOn"])  # convert string to dict
                    except:
                        col["actionOn"] = ast.literal_eval(colprop.info["actionOn"])  # convert string to dict
                if "length" in colprop.info:
                    col["length"] = colprop.info["length"]
                    col["decimals"] = colprop.info["decimals"]
                else:
                    try:
                        if colprop.type.precision is None:
                            col["length"] = 0
                            col["decimals"] = 0
                        else:
                            col["length"] = colprop.type.precision
                            col["decimals"] = colprop.type.scale
                    except:
                        col["decimals"] = 0
                        try:
                            if colprop.type.length is None:
                                col["length"] = 0
                            else:
                                col["length"] = colprop.type.length
                        except:
                            col["length"] = 0

                col["requiredIf"] = None
                if "requiredIf" in colprop.info:
                    col["requiredIf"] = colprop.info["requiredIf"]

                col["listFormat"] = colprop.info["listFormat"] if "listFormat" in colprop.info else False
                col["listMin"] = colprop.info["listMin"] if "listMin" in colprop.info else None
                col["listMax"] = colprop.info["listMax"] if "listMax" in colprop.info else None
                col["isJoinField"] = False
                col["gridSubTable"] = False
                col["label"] = colprop.info["label"] if "label" in colprop.info else p.key
                col["alias"] = colprop.info["alias"] if "alias" in colprop.info else None
                col["columnLabel"] = colprop.info["columnLabel"] if "columnLabel" in colprop.info else col["label"]
                col["validators"] = colprop.info["validators"] if "validators" in colprop.info else None
                col["validator_fields"] = colprop.info["validator_fields"] if "validator_fields" in colprop.info else None
                col["validator_messages"] = colprop.info["validator_messages"] if "validator_messages" in colprop.info else None
                col["case"] = colprop.info["case"] if "case" in colprop.info else None
                col["min"] = colprop.info["min"] if "min" in colprop.info else None
                col["max"] = colprop.info["max"] if "max" in colprop.info else None
                col["sequence"] = 0
                col["hidden"] = colprop.info["hidden"] if "hidden" in colprop.info else False
                col["modifiable"] = colprop.info["modifiable"] if "modifiable" in colprop.info else True
                col["displayable"] = colprop.info["displayable"] if "displayable" in colprop.info else True
                col["sortable"] = colprop.info["sortable"] if "sortable" in colprop.info else True
                col["searchable"] = searchable if searchable is not None else colprop.info["searchable"] if "searchable" in colprop.info else True
                col["draggable"] = colprop.info["draggable"] if "draggable" in colprop.info else True
                col["selectId"] = colprop.info["selectId"] if "selectId" in colprop.info else "Id"
                col["selectKey"] = colprop.info["selectKey"] if "selectKey" in colprop.info else None
                col["selectColumn"] = colprop.info["selectColumn"] if "selectColumn" in colprop.info else None
                col["selectTable"] = colprop.info["selectTable"] if "selectTable" in colprop.info else None
                col["selectObject"] = colprop.info["selectObject"] if "selectObject" in colprop.info else None
                col["selectFormat"] = colprop.info["selectFormat"] if "selectFormat" in colprop.info else None
                col["selectField"] = colprop.info["selectField"] if "selectField" in colprop.info else None
                col["selectFieldValue"] = colprop.info["selectFieldValue"] if "selectFieldValue" in colprop.info else None
                col["selectTableField"] = colprop.info["selectTableField"] if "selectTableField" in colprop.info else None
                col["selectTableFieldValue"] = colprop.info["selectTableFieldValue"] if "selectTableFieldValue" in colprop.info else None
                col["selectGetter"] = colprop.info["selectGetter"] if "selectGetter" in colprop.info else None
                col["selectCascade"] = colprop.info["selectCascade"] if "selectCascade" in colprop.info else None
                col["selectDepth"] = colprop.info["selectDepth"] if "selectDepth" in colprop.info else 1

                if "documents" in colprop.info:
                    col["documents"] = colprop.info["documents"]
                else:
                    col["documents"] = None

                if col["hidden"]:
                    col["modifiable"] = False
                    col["displayable"] = False

                if isFk:
                    col["name"] = name
                    col["type"] = None
                    col["length"] = 0
                    col["decimals"] = 0
                    col["sequence"] = 0
                    col["isJoinField"] = True
                    col["gridSubTable"] = colprop.info["gridSubTable"] if "gridSubTable" in colprop.info else False
                    # RelationshipProperty - Many2One only
                    if polymorphicBase:
                        for mp in mapper._polymorphic_properties:
                            # Program_Id name is Program
                            # Get the RelationshipProperty
                            if mp.key == name:
                                p = mp
                                break
                    elif audit_name is not None:
                        p = audit_relationships[audit_name]
                    else:
                        p = self.__mapper__.relationships[name]

                    col["direction"] = p.direction.name
                    col["isUseList"] = p.uselist
                    col["primaryJoin"] = str(p.primaryjoin).replace('"', "").strip()  # prop.primaryjoin.__str__
                    try:
                        # don't include sqlalchemy_continuum version tables
                        if list(p.remote_side)[0].table.name.endswith("_version") and \
                                not table.name.endswith("_version") and\
                                col["name"] == "versions":
                            continue
                        t_name = list(p.remote_side)[0].table.name
                        if remove_duplicate_tables:
                            if p.direction is MANYTOONE:
                                if t_name in dup_table_list:
                                    continue
                                else:
                                    dup_table_list.append(t_name)
                        col["remoteTable"] = t_name
                        col["requiredEntry"] = None
                        schema_except_fields = colprop.info["exceptSchemaFields"] \
                            if "exceptSchemaFields" in colprop.info else []
                        col["relations"] = Models[list(p.remote_side)[0].table.name]["klass"]().\
                            schema_to_dict(except_fields=except_fields, depth=level - 1,
                                           remove_duplicate_tables=remove_duplicate_tables,
                                           dup_table_list=dup_table_list,
                                           schema_except_fields=schema_except_fields,
                                           searchable=False if audit else None
                                           )
                    except:
                        # child table not the association table for Many2Many
                        try:
                            # don't include sqlalchemy_continuum version tables
                            if p.target.name.endswith("_version") and \
                                    not table.name.endswith("_version") and\
                                    col["name"] == "versions":
                                continue
                            t_name = p.target.name
                            if remove_duplicate_tables:
                                if p.direction is MANYTOONE:
                                    if t_name in dup_table_list:
                                        continue
                                    else:
                                        dup_table_list.append(t_name)
                            col["remoteTable"] = t_name
                            col["requiredEntry"] = None
                            col["relations"] = Models[p.target.name]["klass"]().\
                                schema_to_dict(except_fields=except_fields, depth=level - 1,
                                               remove_duplicate_tables=remove_duplicate_tables,
                                               dup_table_list=dup_table_list,
                                               schema_except_fields=schema_except_fields,
                                               searchable=False if audit else None
                                               )
                        except:
                            continue
                schema.append(col)
            # RelationshipProperty - One2One, One2Many only
            # check if p.key is already defined in current schema list
            elif not any(d["name"] == p.key for d in schema):
                info = {}
                if p.info:
                    info = p.info

                level = depth
                if "depth" in info:
                    if depth == 0 or info["depth"] == 0:
                        # Overrides depth
                        level = info["depth"]

                if audit:
                    if p.key == "version_parent":
                        continue
                    level = 1

                if level > 0:
                    col["name"] = p.key
                    col["table"] = table.name
                    col["type"] = None
                    col["numberType"] = None
                    col["textType"] = None
                    col["currencyCodeField"] = None
                    col["actionOn"] = None
                    col["requiredIf"] = None
                    col["default"] = None
                    col["enums"] = None
                    col["enum_getter"] = None
                    col["length"] = 0
                    col["decimals"] = 0
                    col["listFormat"] = info["listFormat"] if "listFormat" in info else False
                    col["listMin"] = info["listMin"] if "listMin" in info else None
                    col["listMax"] = info["listMax"] if "listMax" in info else None
                    col["label"] = info["label"] if "label" in info else p.key
                    col["alias"] = info["alias"] if "alias" in info else None
                    col["columnLabel"] = info["columnLabel"] if "columnLabel" in info else col["label"]
                    col["validators"] = info["validators"] if "validators" in info else None
                    col["validator_fields"] = info["validator_fields"] if "validator_fields" in info else None
                    col["validator_messages"] = info["validator_messages"] if "validator_messages" in info else None
                    col["case"] = info["case"] if "case" in info else None
                    col["min"] = info["min"] if "min" in info else None
                    col["max"] = info["max"] if "max" in info else None
                    col["sequence"] = 0
                    col["nullable"] = info["nullable"] if "nullable" in info else False  # colprop.nullable
                    col["hidden"] = info["hidden"] if "hidden" in info else False
                    col["modifiable"] = info["modifiable"] if "modifiable" in info else True
                    col["displayable"] = info["displayable"] if "displayable" in info else True
                    col["sortable"] = info["sortable"] if "sortable" in info else True
                    col["searchable"] = searchable if searchable is not None else info["searchable"] if "searchable" in info else True
                    col["draggable"] = info["draggable"] if "draggable" in info else True
                    col["selectId"] = info["selectId"] if "selectId" in info else "Id"
                    col["selectKey"] = info["selectKey"] if "selectKey" in info else None
                    col["selectColumn"] = info["selectColumn"] if "selectColumn" in info else None
                    col["selectTable"] = info["selectTable"] if "selectTable" in info else None
                    col["selectObject"] = info["selectObject"] if "selectObject" in info else None
                    col["selectFormat"] = info["selectFormat"] if "selectFormat" in info else None
                    col["selectField"] = info["selectField"] if "selectField" in info else None
                    col["selectFieldValue"] = info["selectFieldValue"] if "selectFieldValue" in info else None
                    col["selectTableField"] = info["selectTableField"] if "selectTableField" in info else None
                    col["selectTableFieldValue"] = info["selectTableFieldValue"] if "selectTableFieldValue" in info else None
                    col["selectGetter"] = info["selectGetter"] if "selectGetter" in info else None
                    col["selectCascade"] = info["selectCascade"] if "selectCascade" in info else None
                    col["selectDepth"] = info["selectDepth"] if "selectDepth" in info else 1

                    if "documents" in info:
                        try:
                            col["documents"] = json.loads(info["documents"])  # convert string to dict
                        except:
                            col["documents"] = ast.literal_eval(info["documents"])  # convert string to dict
                    else:
                        col["documents"] = None

                    if col["hidden"]:
                        col["modifiable"] = False
                        col["displayable"] = False

                    col["isJoinField"] = True
                    col["gridSubTable"] = info["gridSubTable"] if "gridSubTable" in info else False
                    col["direction"] = p.direction.name
                    col["isUseList"] = p.uselist
                    col["primaryJoin"] = str(p.primaryjoin).replace('"', "").strip()  # prop.primaryjoin.__str__
                    try:
                        # don't include sqlalchemy_continuum version tables
                        if list(p.remote_side)[0].table.name.endswith("_version") and \
                                not table.name.endswith("_version") and \
                                col["name"] == "versions":
                            continue

                        col["remoteTable"] = list(p.remote_side)[0].table.name
                        if p.direction is ONETOMANY:
                            col["requiredEntry"] = p.info["requiredEntry"] if "requiredEntry" in p.info else None
                        else:
                            col["requiredEntry"] = None

                        schema_except_fields = info["exceptSchemaFields"] \
                            if "exceptSchemaFields" in info else []
                        col["relations"] = Models[list(p.remote_side)[0].table.name]["klass"]().\
                            schema_to_dict(except_fields=except_fields, depth=level - 1,
                                           remove_duplicate_tables=remove_duplicate_tables,
                                           dup_table_list=[],
                                           schema_except_fields=schema_except_fields,
                                           searchable=False if audit else None
                                           )
                    except:
                        try:
                            # don't include sqlalchemy_continuum version tables
                            if p.target.name.endswith("_version") and\
                                    not table.name.endswith("_version") and\
                                    col["name"] == "versions":
                                continue
                            # child table not the association table for Many2Many
                            col["remoteTable"] = p.target.name
                            if p.direction is ONETOMANY:
                                col["requiredEntry"] = p.info["requiredEntry"] if "requiredEntry" in p.info else None
                            else:
                                col["requiredEntry"] = None
                            col["relations"] = Models[p.target.name]["klass"]().\
                                schema_to_dict(except_fields=except_fields, depth=level - 1,
                                               remove_duplicate_tables=remove_duplicate_tables,
                                               dup_table_list=[],
                                               schema_except_fields=schema_except_fields,
                                               searchable=False if audit else None
                                               )
                        except Exception as err:
                            log.warning(f"Base.schema_to_dict relations error: {str(err)}")
                            continue
                    schema.append(col)

        # hybrids
        info = self.get_table_info()
        if "hybrids" in info:
            for k, v in get_hybrid_properties(mapper).items():
                key = v.__name__

                h_schema = search_list_of_dict(info["hybrids"], "name", key)
                if h_schema is None:
                    continue

                if key in except_fields:
                    continue
                else:
                    name = table.name + "." + key
                    if name in except_fields:
                        continue

                col = dict()
                col["name"] = key
                col["table"] = table.name
                col["type"] = h_schema["type"] if "type" in h_schema else "String"
                col["numberType"] = h_schema["numberType"] if "numberType" in h_schema else "number"
                col["textType"] = h_schema["textType"] if "textType" in h_schema else None
                col["currencyCodeField"] = h_schema["currencyCodeField"] if "currencyCodeField" in h_schema else None
                col["label"] = h_schema["label"] if "label" in h_schema else key
                col["columnLabel"] = h_schema["columnLabel"] if "columnLabel" in h_schema else col["label"]
                col["displayable"] = h_schema["displayable"] if "displayable" in h_schema else True
                col["sortable"] = h_schema["sortable"] if "sortable" in h_schema else False
                col["searchable"] = searchable if searchable is not None else h_schema["searchable"] if "searchable" in h_schema else False
                col["draggable"] = h_schema["draggable"] if "draggable" in h_schema else True
                col["length"] = h_schema["length"] if "length" in h_schema else 0
                col["decimals"] = h_schema["decimals"] if "decimals" in h_schema else 0
                col["modifiable"] = False
                col["isJoinField"] = False
                col["actionOn"] = None
                col["requiredIf"] = None
                col["default"] = None
                col["enums"] = None
                col["enum_getter"] = None
                col["alias"] = None
                col["validators"] = None
                col["validator_fields"] = None
                col["validator_messages"] = None
                col["listFormat"] = False
                col["listMin"] = None
                col["listMax"] = None
                col["case"] = None
                col["min"] = None
                col["max"] = None
                col["sequence"] = 0
                col["nullable"] = False
                col["hidden"] = False
                col["selectId"] = None
                col["selectKey"] = None
                col["selectColumn"] = None
                col["selectTable"] = None
                col["selectObject"] = None
                col["selectFormat"] = None
                col["selectField"] = None
                col["selectFieldValue"] = None
                col["selectTableField"] = None
                col["selectTableFieldValue"] = None
                col["selectGetter"] = None
                col["selectCascade"] = None
                col["selectDepth"] = 1
                col["documents"] = None
                col["direction"] = None
                col["isUseList"] = False
                col["primaryJoin"] = None
                schema.append(col)

        return schema

    def is_poly_base(self):
        mapper = class_mapper(self.__class__)
        polymorphic_base = False
        if mapper.with_polymorphic_mappers:
            polymorphic_base = True
        return polymorphic_base

    def get_poly_base_on_name(self):
        mapper = class_mapper(self.__class__)
        return mapper.polymorphic_on.name

    def get_poly_base_on_obj(self, value):
        mapper = class_mapper(self.__class__)
        return Models[mapper.polymorphic_map[value].local_table.name]["klass"]()

    def get_joinlist(self, except_fields=[], depth=1, schema_except_fields=[]):
        """
            get nested join path
        """
        mapper, props = sorted_props(self.__class__, except_fields, schema_except_fields)
        table = mapper.local_table  # sqlalchemy.schema.Table

        join_list = []
        for p in props:
            if isinstance(p, ColumnProperty):
                continue
            col = dict()
            col["table"] = table.name
            col["key"] = p.key
            col["type"] = p.direction.name
            col["nullable"] = any(c.nullable for c in p.local_columns)

            if p.direction is ONETOMANY:
                if p.uselist:
                    col["cardinality"] = "1:n"
                else:
                    col["cardinality"] = "1:1"
            elif p.direction is MANYTOONE:
                col["cardinality"] = "n:1"
            elif p.direction is MANYTOMANY:
                col["cardinality"] = "n:n"

            if p.direction is MANYTOMANY:
                # child table not the association table for Many2Many
                if not isinstance(p.target, Table):
                    continue
                # don't include sqlalchemy_continuum version tables
                if p.target.name.endswith("_version") and\
                        not table.name.endswith("_version") and \
                        col["key"] == "versions":
                    continue
                col["joinTable"] = p.target.name
            else:
                # don't include sqlalchemy_continuum version tables
                if list(p.remote_side)[0].table.name.endswith("_version") and\
                        not table.name.endswith("_version") and\
                        col["key"] == "versions":
                    continue
                col["joinTable"] = list(p.remote_side)[0].table.name
            col["alias"] = table.name + "_" + p.key
            col["useList"] = p.uselist
            col["joins"] = []

            if depth > 0:
                try:
                    # don't include sqlalchemy_continuum version tables
                    if list(p.remote_side)[0].table.name == table.name + "_version" and col["key"] == "versions":
                        continue
                    col["joinTable"] = list(p.remote_side)[0].table.name
                    col["joins"] = Models[list(p.remote_side)[0].table.name]["klass"]().get_joinlist(except_fields,
                                                                                                    depth - 1)
                except:
                    # don't include sqlalchemy_continuum version tables
                    if p.target.name == table.name + "_version" and col["key"] == "versions":
                        continue
                    # child table not the association table for Many2Many
                    col["joinTable"] = p.target.name
                    col["joins"] = Models[p.target.name]["klass"]().get_joinlist(except_fields, depth - 1)
            join_list.append(col)

        return join_list

    def get_table_info(self):
        mapper = class_mapper(self.__class__)
        table = mapper.local_table  # sqlalchemy.schema.Table
        if table.info:
            info = table.info
            if "label" not in info:
                info["label"] = table.name
            if "desc" not in info:
                info["desc"] = info["label"]
            if "key" not in info:
                info["key"] = None
        else:
            info = dict()
            info["label"] = table.name
            info["desc"] = table.name
            info["key"] = None

        info["name"] = table.name
        info["mapper"] = mapper.class_.__name__
        info["primaryKey"] = [col.name for col in mapper.primary_key]
        info["baseTable"] = None
        info["polymorphic_id"] = mapper.polymorphic_identity
        # get polymorphic Base
        if mapper.polymorphic_identity is not None:
            if not self.is_poly_base():
                for key, map in mapper.polymorphic_map.items():
                    if key == mapper.polymorphic_identity:
                        continue
                    if key == "Base":
                        info["baseTable"] = map.local_table.name
                        break

        return info


Model = declarative_base(cls=Base, mapper=mapper)

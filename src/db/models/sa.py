import logging
from sqlalchemy import (Table, Column, Integer, MetaData)
from sqlalchemy.orm import aliased, class_mapper
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.expression import column
from sqlalchemy_continuum import version_class
from sqlalchemy_utils import get_hybrid_properties, get_mapper
from pyparsing import ParseException

from ...utils.misc import search_list_of_dict, get_timestamp

from .where import WhereExpression, iWhereExpression

from .model import Models

log = logging.getLogger(__name__)


class SAException(Exception):
    """
        SAException error
    """       

    
class SQA(object):

    def get_model(self, name):
        # returns <class 'sqlalchemy.ext.declarative.api.DeclarativeMeta'>        
        try:
            return Models[name]["klass"]
        except:
            raise SAException('SQA.get_model: table {} not found in Models'.format(name))
                
    def instrumented_attr(self, table_name, col_name, alias=None):
        if alias is None:
            alias = {}

        # returns <class 'sqlalchemy.orm.attributes.InstrumentedAttribute'>
        try:
            return getattr(self.get_model(table_name), col_name)
        except:
            try:
                # must be alias
                return getattr(alias[table_name], col_name)
            except:
                # must be hybrid
                for k, v in get_hybrid_properties(get_mapper(self.get_model(table_name))).items():
                    if k == col_name:
                        return v

                raise SAException(f"SQA.instrumentedAttr: table: {table_name} column: {col_name} not found in Models or alias")

    def get_column(self, name):
        if "." in name:
            # Countries.ModifiedOpId.UserId
            tf = name.split(".")
            table = None
            for i, n in enumerate(tf):
                if i == 0:
                    table = n
                else:
                    try:
                        col = self.instrumented_attr(table, n)
                    except:
                        raise SAException('SQA.get_column: {} : {}.{} not found'.format(name, table, n))
                    # <class 'sqlalchemy.orm.attributes.InstrumentedAttribute'>
                    try:
                        p = col.property
                        if p and isinstance(p, RelationshipProperty):
                            if p.direction.name == "MANYTOMANY":
                                # use child table not association table
                                table = p.target.name
                            else:
                                table = list(p.remote_side)[0].table.name
                        else:
                            break
                    except:
                        # must be hybrid_property
                        pass
        else:
            col = column(name)
            # <class 'sqlalchemy.sql.elements.ColumnClause'>
        return col

    def get_joinlist(self, name):
        """
            get_joinlist("Parents.One21.CreateOpId.Personal.LastName")
        """
        flds = name.split(".")
        level = max(1, len(flds) - 2)  # -2 = First Table entry and last field entry
        joins = []
        join_list = []
        for i, n in enumerate(flds):
            if i == 0:
                join_list = self.get_model(flds[i])().get_joinlist(depth=level)
                # Emails.EmailType  level:1
                # joinlist: [
                # {'table': 'Emails', 'key': 'EmailType', 'joinTable': 'EmailTypes', 'alias': 'Emails_EmailType', 'useList': False,
                #       'joins': [{'table': 'EmailTypes', 'key': 'Company', 'joinTable': 'Companies', 'alias': 'EmailTypes_Company', 'useList': False, 'joins': []},
                #                 {'table': 'EmailTypes', 'key': 'CreateOpId', 'joinTable': 'Users', 'alias': 'EmailTypes_CreateOpId', 'useList': False, 'joins': []},
                #                 {'table': 'EmailTypes', 'key': 'ModifiedOpId', 'joinTable': 'Users', 'alias': 'EmailTypes_ModifiedOpId', 'useList': False, 'joins': []}
                #                ]},
                #  {'table': 'Emails', 'key': 'CreateOpId', 'joinTable': 'Users', 'alias': 'Emails_CreateOpId', 'useList': False,
                #       'joins': [{'table': 'Users', 'key': 'InactiveOpId', 'joinTable': 'Users', 'alias': 'Users_InactiveOpId', 'useList': False, 'joins': []},
                #                 {'table': 'Users', 'key': 'Company', 'joinTable': 'Companies', 'alias': 'Users_Company', 'useList': False, 'joins': []},
                #                 {'table': 'Users', 'key': 'Groups', 'joinTable': 'Groups', 'alias': 'Users_Groups', 'useList': True, 'joins': []},
                #                 {'table': 'Users', 'key': 'StartMenu', 'joinTable': 'Menus', 'alias': 'Users_StartMenu', 'useList': False, 'joins': []},
                #                 {'table': 'Users', 'key': 'Personal', 'joinTable': 'UserPersons', 'alias': 'Users_Personal', 'useList': False, 'joins': []},
                #                 {'table': 'Users', 'key': 'CreateOpId', 'joinTable': 'Users', 'alias': 'Users_CreateOpId', 'useList': False, 'joins': []},
                #                 {'table': 'Users', 'key': 'ModifiedOpId', 'joinTable': 'Users', 'alias': 'Users_ModifiedOpId', 'useList': False, 'joins': []}
                #                ]},
                #  {'table': 'Emails', 'key': 'ModifiedOpId', 'joinTable': 'Users', 'alias': 'Emails_ModifiedOpId', 'useList': False,
                #       'joins': [{'table': 'Users', 'key': 'InactiveOpId', 'joinTable': 'Users', 'alias': 'Users_InactiveOpId', 'useList': False, 'joins': []},
                #                 {'table': 'Users', 'key': 'Company', 'joinTable': 'Companies', 'alias': 'Users_Company', 'useList': False, 'joins': []},
                #                 {'table': 'Users', 'key': 'Groups', 'joinTable': 'Groups', 'alias': 'Users_Groups', 'useList': True, 'joins': []},
                #                 {'table': 'Users', 'key': 'StartMenu', 'joinTable': 'Menus', 'alias': 'Users_StartMenu', 'useList': False, 'joins': []},
                #                 {'table': 'Users', 'key': 'Personal', 'joinTable': 'UserPersons', 'alias': 'Users_Personal', 'useList': False, 'joins': []},
                #                 {'table': 'Users', 'key': 'CreateOpId', 'joinTable': 'Users', 'alias': 'Users_CreateOpId', 'useList': False, 'joins': []},
                #                 {'table': 'Users', 'key': 'ModifiedOpId', 'joinTable': 'Users', 'alias': 'Users_ModifiedOpId', 'useList': False, 'joins': []}
                #                ]}
                #  ]
            else:  
                try:
                    join = search_list_of_dict(join_list, "key", n)
                    joins.append((join["table"], join["key"], 
                                  join["joinTable"], join["alias"],
                                  join["nullable"],
                                  join["cardinality"]))
                    join_list = join["joins"]
                except:
                    pass
        # joins: [('Emails', 'EmailType', 'EmailTypes', 'Emails_EmailType')]
        return joins
    
    def get_table_info(self, table_name):
        """
        get table attributes
        :param table_name: db table name NOT table class name
                            ie. Programs NOT Program
        :return: dict of table attributes
                {'name': 'Programs', 'mapper': 'Program', 'primaryKey': ['Id'], 'label': 'Programs',
                'desc': 'Programs', 'companyField': None, 'keyPaths': None, 'baseTable': None}
        """
        try:
            return self.get_model(table_name)().get_table_info()
        except:
            raise SAException('SQA.get_table_info: table {} not found in Models'.format(table_name))
        
    def get_schema(self, table_name, depth=1, audit=False, remove_duplicate_tables=False):
        if audit:
            table_class = self.get_model(table_name)
            version_table = version_class(table_class)
            version_name = version_table.__table__.name
            return self.get_model(version_name)().schema_to_dict(except_fields=[],
                                                                 depth=depth,
                                                                 audit=audit,
                                                                 table_class=table_class,
                                                                 remove_duplicate_tables=remove_duplicate_tables,
                                                                 dup_table_list=[],
                                                                 schema_except_fields=[]
                                                                 )
        else:
            return self.get_model(table_name)().schema_to_dict(except_fields=[],
                                                               depth=depth,
                                                               audit=audit,
                                                               table_class=None,
                                                               remove_duplicate_tables=remove_duplicate_tables,
                                                               dup_table_list=[],
                                                               schema_except_fields=[]
                                                               )

    def set_alias(self, table_name):
        return aliased(self.get_model(table_name))

    def sort_asc(self, table_name, field_name):
        tab = table_name.strip()
        col = field_name.strip()

        return self.instrumented_attr(tab, col)

    def sort_desc(self, table_name, field_name):
        tab = table_name.strip()
        col = field_name.strip()

        return self.instrumented_attr(tab, col).desc()

    def where(self, where_string, case_sensitive=False, table_name=None, alias=None):
        if alias is None:
            alias = {}

        if case_sensitive:
            # case sensitive where
            _filter = WhereExpression(table_name, alias)
        else:
            # case insensitive where
            _filter = iWhereExpression(table_name, alias)
        try:
            return _filter(where_string)
        except ParseException as err:
            raise SAException("SQA.where: Parse error: {} - {}".format(where_string, err))

    def validate(self, table_name, fields, level=1):
        # TODO
        schema = self.get_schema(table_name, level)

    def copy_data(self, to_obj, from_obj, except_fields=[]):
        primary_key = [col.name for col in to_obj.__mapper__.primary_key]
        table_name = to_obj.__table__.name  # Users
        columns = to_obj.__mapper__.columns.keys()
        relationships = to_obj.__mapper__.relationships.keys()

        for key in columns:
            if key.startswith("_"):
                continue
            if key in except_fields:
                continue
            if key in primary_key:
                continue
            col = to_obj.__mapper__.columns[key]
            # no foreign keys  ie:  Company_Id
            if len(col.foreign_keys) > 0:
                continue

            try:
                setattr(to_obj, key, getattr(from_obj, key))
            except Exception as err:
                log.warning(f"sqa.copy_data column {table_name} {key} {str(err)}")

        # relationships
        for key in relationships:
            if key in except_fields:
                continue
            rel = to_obj.__mapper__.relationships[key]

            if rel.direction.name == "MANYTOONE":
                try:
                    setattr(to_obj, key, getattr(from_obj, key))
                except Exception as err:
                    log.warning(f"sqa.copy_data relationship {table_name} {key} {str(err)}")

        return to_obj

    def clone(self, obj, except_fields=[]):
        return self.copy_data(type(obj)(), obj, except_fields)

    def temp_table(self, columns=[]):
        from ...db import engine
        # TODO
        temp = Table(f"temp_table_{get_timestamp()}",
                     MetaData(),
                     Column("Id", Integer, autoincrement=True, primary_key=True, nullable=False),
                     prefixes=['TEMPORARY']
                     )

        for col in columns:
            temp.append_column(col)

        connection = engine.connect()
        temp.create(connection)

        return connection, temp

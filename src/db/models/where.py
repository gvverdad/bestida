'''
Created on Sep 5, 2011

@author: gvv
'''
import logging

from sqlalchemy import func
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.expression import column, and_, or_, not_, literal
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.sqltypes import String, Text, Enum
from sqlalchemy_utils import get_hybrid_properties, get_mapper

from ...utils.exprparser import ExprParser

log = logging.getLogger(__name__)


# case sensitive where                                
class WhereExpression(ExprParser):
    def __init__(self, table_name=None, alias=None):
        if alias is None:
            alias = {}

        self.table_name = table_name
        self.alias = alias
        super(WhereExpression, self).__init__()
    
    def eval_eq(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if isinstance(val, type(None)):
            return col.is_(val)
        try:
            return col.op("=")(val)
        except:
            # must be hybrid_property
            return col == val

    def eval_ne(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if isinstance(val, type(None)):
            return col.isnot(val)
        try:
            return col.op("!=")(val)
        except:
            # must be hybrid_property
            return col != val

    def eval_gt(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        try:
            return col.op(">")(val)
        except:
            # must be hybrid_property
            return col > val

    def eval_ge(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        try:
            return col.op(">=")(val)
        except:
            # must be hybrid_property
            return col >= val

    def eval_lt(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        try:
            return col.op("<")(val)
        except:
            # must be hybrid_property
            return col < val

    def eval_le(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        try:
            return col.op("<=")(val)
        except:
            # must be hybrid_property
            return col <= val

    def eval_startswith(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        return col.startswith(val)

    def eval_endswith(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        return col.endswith(val)

    def eval_match(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        return col.match(val)

    def eval_contains(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        try:
            return col.contains(val)
        except:
            # must be hybrid_property sql string expression
            # Use + or func.concat() to safely construct SQL string expressions in SQLAlchemy
            # Avoid f"{x} {y}" inside .expression — it doesn't translate to SQL
            raise ValueError("eval_contains on hybrid_properties expression")

    def eval_between(self, arg):
        col = self.eval(arg[0])
        val1 = self.eval(arg[1])
        val2 = self.eval(arg[2])
        return col.between(val1, val2)

    def eval_in(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        return col.in_(val)
    
    def eval_and(self, arg):
        return and_(self.eval(arg[0]), self.eval(arg[1]))

    def eval_or(self, arg):
        return or_(self.eval(arg[0]), self.eval(arg[1]))
    
    def eval_not(self, arg):
        return not_(self.eval(arg[0]))
        
    def eval_string(self, arg):
        return literal(str(arg[0]))
    
    def eval_integer(self, arg):
        return literal(int(arg[0]))

    def eval_float(self, arg):
        return literal(float(arg[0]))
            
    def eval_variable(self, arg):
        from .model import Models

        name = arg[0]
        if self.table_name is not None and "." not in name:
            name = self.table_name + "." + name
        # if nested name - always include the tablename
        if "." in name:
            # Countries.ModifiedOpId.UserId
            tf = name.split(".")
            table = None
            for i, n in enumerate(tf):
                if i == 0:
                    table = n
                else:
                    try:
                        col = getattr(Models[table]["klass"], n)
                    except:
                        # must be alias
                        try:
                            col = getattr(self.alias.get(table), n)
                        except:
                            try:
                                found = False
                                for k, v in get_hybrid_properties(get_mapper(Models[table]["klass"])).items():
                                    if k == n:
                                        col = v
                                        found = True
                                        break
                                if not found:
                                    raise ValueError('WhereExpression.evalVariable: hybrid not found %s.%s : %s)' % (table, n, name))
                            except:
                                raise ValueError('WhereExpression.evalVariable: table %s not found in Models or alias (%s : %s)' % (table, name, n))
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
                    
    def eval_expr(self, arg):
        return self.eval(arg[0])
                                                            
    def __call__(self, where_string):
        return super(WhereExpression, self).parse(where_string)


# case insensitive where
class iWhereExpression(WhereExpression):
    def __init__(self, table_name=None, alias=None):
        if alias is None:
            alias = {}
        super(iWhereExpression, self).__init__(table_name, alias)
        
    def eval_eq(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if isinstance(val, type(None)):
            return col.is_(val)
        elif arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and \
                isinstance(col.property.columns[0].type, (String, Text)) and\
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).op("=")(func.lower(val))
        else:
            try:
                return col.op("=")(val)
            except:
                # must be hybrid_property
                return col == val

    def eval_ne(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if isinstance(val, type(None)):
            return col.isnot(val)
        elif arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and \
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).op("!=")(func.lower(val))
        else:
            try:
                return col.op("!=")(val)
            except:
                # must be hybrid_property
                return col != val

    def eval_gt(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and \
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).op(">")(func.lower(val))
        else:
            try:
                return col.op(">")(val)
            except:
                # must be hybrid_property
                return col > val

    def eval_ge(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and \
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).op(">=")(func.lower(val))
        else:
            try:
                return col.op(">=")(val)
            except:
                # must be hybrid_property
                return col >= val

    def eval_lt(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and \
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).op("<")(func.lower(val))
        else:
            try:
                return col.op("<")(val)
            except:
                # must be hybrid_property
                return col < val

    def eval_le(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and \
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).op("<=")(func.lower(val))
        else:
            try:
                return col.op("<=")(val)
            except:
                # must be hybrid_property
                return col <= val

    def eval_startswith(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and \
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).startswith(func.lower(val))
        else:
            return col.startswith(val)

    def eval_endswith(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and \
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).endswith(func.lower(val))
        else:
            return col.endswith(val)

    def eval_match(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and\
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).match(func.lower(val))
        else:
            return self.eval(col).match(val)

    def eval_contains(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and \
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).contains(func.lower(val))
        else:
            try:
                return col.contains(val)
            except:
                # must be hybrid_property sql string expression
                # Use + or func.concat() to safely construct SQL string expressions in SQLAlchemy
                # Avoid f"{x} {y}" inside .expression — it doesn't translate to SQL
                raise ValueError("eval_contains on hybrid_properties expression")

    def eval_between(self, arg):
        col = self.eval(arg[0])
        val1 = self.eval(arg[1])
        val2 = self.eval(arg[2])
        if arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and \
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).between(func.lower(val1), func.lower(val2))
        else:
            return col.between(val1, val2)

    def eval_in(self, arg):
        col = self.eval(arg[0])
        val = self.eval(arg[1])
        if arg[1].getName() == "String" and isinstance(col, InstrumentedAttribute) and\
                isinstance(col.property.columns[0].type, (String, Text)) and \
                not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).in_(func.lower(val))
        elif arg[1].getName() == "List" and isinstance(col, InstrumentedAttribute) and \
            isinstance(col.property.columns[0].type, (String, Text)) and \
            not isinstance(col.property.columns[0].type, Enum):
            return func.lower(col).in_([func.lower(x) for x in val])
        else:
            return col.in_(val)

    def __call__(self, where_string):
        return super(iWhereExpression, self).parse(where_string)

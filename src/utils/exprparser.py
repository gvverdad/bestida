import logging
import dateutil.parser
from pyparsing import (Word, oneOf, Forward, Combine, delimitedList, 
                       Optional, nums, Literal, Group, CaselessLiteral, 
                       Keyword, alphanums, ParseException, 
                       quotedString, restOfLine, removeQuotes)

log = logging.getLogger(__name__)


class Parser(object):    
    def __init__(self):
        _sign = Word("+-", exact=1)
        _E = CaselessLiteral("E")
        _realnum = Group(Combine(Optional(_sign) + (Word(nums) + "." + Optional(Word(nums)) |
                                                         ("." + Word(nums)) ) + 
                  Optional(_E + Optional(_sign) + Word(nums)))).setName("float").setResultsName("Float")
        _intnum = Group(Combine(Optional(_sign) + Word(nums) +
                 Optional(_E + Optional("+") + Word(nums)))).setName("integer").setResultsName("Integer")
        _number = _realnum | _intnum

        # ISO 8601 date format 
        _dateformat = Group(Combine(Word(nums, exact=4) + "-" + Word(nums, exact=2) + "-" +
                              Word(nums, exact=2))).setName("date").setResultsName("Date")
        # ISO 8601 time format                              
        _timeformat = Group(Combine(Word(nums, exact=2) + ":" + Word(nums, exact=2) +
                              Optional(":" + Word(nums) +
                                       Optional("." + Word(nums))))).setName("time").setResultsName("Time")
        # ISO 8601 datetime format
        _datetimeformat = Group(Combine(Word(nums, exact=4) + "-" + Word(nums, exact=2) + "-" +
                                  Word(nums, exact=2) + oneOf(["T", " "], caseless=False) +
                         Word(nums, exact=2) + ":" + Word(nums, exact=2) +
                         Optional(":" + Word(nums) +
                                  Optional("." + Word(nums))))).setName("datetime").setResultsName("DateTime")
        _dates = _datetimeformat | _timeformat | _dateformat

        _none = Group(oneOf(["null", "none"], caseless=True)).setName("Null").setResultsName("Null")
        _true = Group(oneOf(["true", "yes"], caseless=True)).setName("True").setResultsName("True")
        _false = Group(oneOf(["false", "no"], caseless=True)).setName("False").setResultsName("False")
        _string = Group(quotedString.copy().setParseAction(removeQuotes)).setName("string").setResultsName("String")
        _variable = Group(Word(alphanums + "_.")).setName("variable").setResultsName("Variable")

        _value = _dates | _number | _string | _none | _true | _false | _variable        
        _listValue = Group(delimitedList(_value)).setName("list").setResultsName("List")        
        
        _lparen = Literal("(").setName("left parenthesis").suppress()
        _rparen = Literal(")").setName("right parenthesis").suppress()
        _listSeparator = Literal(",").setName("list separator").suppress()
                
        _eq = oneOf(["==", "="], caseless=True).suppress()
        _ne = oneOf(["!=", "<>"], caseless=True).suppress()
        _lt = Literal("<").suppress()
        _le = Literal("<=").suppress()
        _gt = Literal(">").suppress()
        _ge = Literal(">=").suppress()
        eq = Group(_variable + _eq + _value).setResultsName("Eq")
        ne = Group(_variable + _ne + _value).setResultsName("Ne")
        gt = Group(_variable + _gt + _value).setResultsName("Gt")
        ge = Group(_variable + _ge + _value).setResultsName("Ge")                        
        lt = Group(_variable + _lt + _value).setResultsName("Lt")
        le = Group(_variable + _le + _value).setResultsName("Le")                                
        expr_ = eq | ne | gt | ge | lt | le

        _between = Keyword("between", caseless=True).suppress()
        between = Group(_variable + _between + _lparen + _value + _listSeparator + _value + _rparen).setResultsName("Between")        
        _in = Keyword("in", caseless=True).suppress()
        in_ = Group(_variable + _in + _lparen + _listValue + _rparen).setResultsName("In")        
        _contains = Keyword("contains", caseless=True).suppress()
        contains = Group(_variable + _contains + _lparen + _value + _rparen).setResultsName("Contains")        
        _match = Keyword("match", caseless=True).suppress()
        match = Group(_variable + _match + _lparen + _value + _rparen).setResultsName("Match")                
        _endswith = Keyword("endswith", caseless=True).suppress()
        endswith = Group(_variable + _endswith + _lparen + _value + _rparen).setResultsName("Endswith")        
        _startswith = Keyword("startswith", caseless=True).suppress()
        startswith = Group(_variable + _startswith + _lparen + _value + _rparen).setResultsName("Startswith")                                                
        func_ = between | in_ | contains | match | endswith | startswith 

        expression = expr_ | func_

        _and = oneOf(["and ", "&"], caseless=True).suppress()
        _or = oneOf(["or ", "|"], caseless=True).suppress()
        _not = oneOf(["not ", "~"], caseless=True).suppress()

        Or = Forward()
        group = (Group(_lparen + Or + _rparen).setResultsName("Group") | expression)
        
        Not = Forward()
        Not << (Group(_not + Not).setResultsName("Not") | group)

        And = Forward()
        And << (Group(Not + _and + And).setResultsName("And") | Not)
        
        Or << (Group(And + _or + Or).setResultsName("Or") | And)
        
        self.Expr = Or.setResultsName('Expr')
        self.Expr.ignore("#" + restOfLine)   
                    
    def parse(self, exprString):
        try:
            return self.Expr.parseString(exprString)                
        except ParseException as err:
            raise ParseException(err)


class Variable(object):
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return "Variable(" + self.name + ")"  


class BinaryOp(object):
    """
        Binary Operator withStoreHistory
    """      
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class Eq(BinaryOp):
    def __init__(self, lhs, rhs):
        super(Eq, self).__init__(lhs, rhs)

    def __repr__(self):
        return "Eq(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class Ne(BinaryOp):
    def __init__(self, lhs, rhs):
        super(Ne, self).__init__(lhs, rhs)
        
    def __repr__(self):
        return "Ne(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class Gt(BinaryOp):
    def __init__(self, lhs, rhs):
        super(Gt, self).__init__(lhs, rhs)
        
    def __repr__(self):
        return "Gt(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class Ge(BinaryOp):
    def __init__(self, lhs, rhs):
        super(Ge, self).__init__(lhs, rhs)
        
    def __repr__(self):
        return "Ge(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class Lt(BinaryOp):
    def __init__(self, lhs, rhs):
        super(Lt, self).__init__(lhs, rhs)
        
    def __repr__(self):
        return "Lt(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class Le(BinaryOp):
    def __init__(self, lhs, rhs):
        super(Le, self).__init__(lhs, rhs)
                
    def __repr__(self):
        return "Le(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class Startswith(BinaryOp):
    def __init__(self, lhs, rhs):
        super(Startswith, self).__init__(lhs, rhs)
                
    def __repr__(self):
        return "Startswith(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class Endswith(BinaryOp):
    def __init__(self, lhs, rhs):
        super(Endswith, self).__init__(lhs, rhs)
                
    def __repr__(self):
        return "Endswith(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class Match(BinaryOp):
    def __init__(self, lhs, rhs):
        super(Match, self).__init__(lhs, rhs)

    def __repr__(self):
        return "Match(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class Contains(BinaryOp):
    def __init__(self, lhs, rhs):
        super(Contains, self).__init__(lhs, rhs)
                
    def __repr__(self):
        return "Contains(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class Between(object):
    def __init__(self, lhs, rFrom, rTo):
        self.lhs = lhs
        self.rFrom = rFrom
        self.rTo = rTo
        
    def __repr__(self):
        return "Between(" + str(self.lhs) + ", " + str(self.rFrom) + ", " + str(self.rTo) + ")"


class In(BinaryOp):
    def __init__(self, lhs, rhs):
        super(In, self).__init__(lhs, rhs)
                
    def __repr__(self):
        return "In(" + str(self.lhs) + ", " + str(self.rhs) + ")"


class And(object):
    def __init__(self, *terms):
        self.terms = terms

    def __repr__(self):
        return "And" + str(self.terms)


class Or(object):
    def __init__(self, *terms):
        self.terms = terms

    def __repr__(self):
        return "Or" + str(self.terms)


class Not(object):
    def __init__(self, term):
        self.term = term

    def __repr__(self):
        return "Not(" + str(self.term) + ")"


class Expr(object):
    def __init__(self, source, expr):
        self.source = source
        self.expr = expr
        
    def __repr__(self):
        return "Expr(" + str(self.expr) + ")"
        
        
class ExprParser(Parser):
    def __init__(self):
        super(ExprParser, self).__init__()
    
    def eval_eq(self, arg):
        return Eq(self.eval(arg[0]), self.eval(arg[1]))

    def eval_ne(self, arg):
        return Ne(self.eval(arg[0]), self.eval(arg[1]))

    def eval_gt(self, arg):
        return Gt(self.eval(arg[0]), self.eval(arg[1]))

    def eval_ge(self, arg):
        return Ge(self.eval(arg[0]), self.eval(arg[1]))

    def eval_lt(self, arg):
        return Lt(self.eval(arg[0]), self.eval(arg[1]))

    def eval_le(self, arg):
        return Le(self.eval(arg[0]), self.eval(arg[1]))
    
    def eval_startswith(self, arg):
        return Startswith(self.eval(arg[0]), self.eval(arg[1])) 

    def eval_endswith(self, arg):
        return Endswith(self.eval(arg[0]), self.eval(arg[1])) 

    def eval_match(self, arg):
        return Match(self.eval(arg[0]), self.eval(arg[1])) 

    def eval_contains(self, arg):
        return Contains(self.eval(arg[0]), self.eval(arg[1])) 

    def eval_between(self, arg):
        return Between(self.eval(arg[0]), self.eval(arg[1]), self.eval(arg[2])) 

    def eval_in(self, arg):
        return In(self.eval(arg[0]), self.eval(arg[1])) 
    
    def eval_and(self, arg):
        return And(self.eval(arg[0]), self.eval(arg[1]))

    def eval_or(self, arg):
        return Or(self.eval(arg[0]), self.eval(arg[1]))
    
    def eval_not(self, arg):
        return Not(self.eval(arg[0]))
    
    def eval_group(self, arg):
        return self.eval(arg[0])
    
    def eval_variable(self, arg):
        return Variable(arg[0])
    
    def eval_string(self, arg):
        return str(arg[0])

    def eval_integer(self, arg):
        return int(arg[0])

    def eval_float(self, arg):
        return float(arg[0])

    def eval_date(self, arg):
        # ISO 8601 date format
        return dateutil.parser.parse(arg[0]).date()

    def eval_time(self, arg):
        return dateutil.parser.parse(arg[0]).time()

    def eval_datetime(self, arg):
        # ISO 8601 datetime format
        return dateutil.parser.parse(arg[0])

    def eval_list(self, arg):
        return [self.eval(e) for e in arg]       
        
    def eval_null(self, arg):
        return None
    
    def eval_true(self, arg):
        return True

    def eval_false(self, arg):
        return False
                    
    def eval_expr(self, arg):
        return Expr(arg, self.eval(arg[0]))
        
    def eval(self, arg):
        return getattr(self, "eval_{}".format(arg.getName().lower()))(arg)
    
    def parse(self, expr_string):
        return self.eval(super(ExprParser, self).parse(expr_string))
                                
    def __call__(self, expr_string):
        return self.parse(expr_string)


if __name__ == '__main__':
    exprParser = ExprParser()     
           
    def test(expr_string):
        try: 
            expr = exprParser(expr_string)
            print(expr_string, ":", expr)
        except ParseException as err:
            print("Parsing failed:")
            print(expr_string)
            print("%s^" % (' '*(err.col-1)))
            print(err.msg)
                              
    test("UserId == 'gvv'")         
    test("UserId =gvv")        
    test("UserId  eq gvv")        
    test("UserId EQ gvv")            
    test("UserId != gvv")
    test("UserId <> gvv")
    test("UserId ne gvv")                
    test('UserId "gvv"')
    test('UserId< "gvv"')        
    test('UserId < "gvv"')
    test('UserId lt "gvv"')        
    test('UserId <"gvv"')                 
    test("UserId <= 120")
    test("UserId le 120")        
    test("User3Id=-10")        
    test("UserId>120.10")
    test("UserId gt 120.10")        
    test("User_Id >= .10")
    test("User_Id ge .10")
    test("User.Id ge .10")                  
    test("Date = 1961-10-11")
    test("Date = 19-6110-11")        
    test("Time = 10:20")
    test("DateTime = 1961-10-11 10:20")
    test("DateTime = 1961-10-11T10:20:15.123")
    test("UserId startswith ('g')")
    test('UserId endswith("g") and (UserId = 10 or UserId > 5)')
    test('UserId endswith("g") & (UserId = 10 | UserId > 5)')        
    test('(UserId endswith("g") and UserId = 10) or UserId > 5')
    test('((UserId endswith("g") and UserId = 10) or (UserId > 5 and UserId < 10))')                
    test('(UserId endswith("g") and (UserId = 10 or UserId > 5))')
    test('not (UserId endswith("g") and (UserId = 10 or UserId > 5))')
    test('~ (UserId endswith("g") and (UserId = 10 or UserId > 5))')                
    test('UserId in ("g","e","o","r","g","e")')
    test('UserId between("gvv","zzz")')
    test('UserId = NULL ')
    test('UserId = None ')
    test('UserId = True ')
    test('UserId = no ')
                  
    test('UserId endswith')
    test('UserId beginswith("gvv"')
    test('UserId startswith("gvv"')                
    test('UserId in()')
    test('UserId between("gvv")')

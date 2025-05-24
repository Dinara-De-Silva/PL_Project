from enum import Enum
from tokenizer import Token, tokenizer



# Define token type constants
KEYWORD = 'KEYWORD'
IDENTIFIER = 'IDENTIFIER'
INTEGER = 'INTEGER'
OPERATOR = 'OPERATOR'
STRING = 'STRING' 
OPEN_BRACKET='('
CLOSE_BRACKET=')'
COMMA=','
SEMICOLON=';'
END_OF_TOKENS='END_OF_TOKENS'



class NodeType(Enum):
    IDENTIFIER='<IDENTIFIER>'
    INTEGER='<INTEGER>'
    STRING='<STRING>'
    LET = 'let'
    LAMBDA = 'lambda'
    WHERE = 'where'
    TAU = 'tau'
    AUG = 'aug'
    ARROW = '->'
    OR = 'or'
    AND = '&'
    NOT = 'not'
    GR = 'gr'
    LS = 'ls'
    GE = 'ge'
    LE = 'le'
    EQ = 'eq'
    NE = 'ne'
    PLUS = '+'
    MINUS = '-'
    NEG = 'neg'
    MUL = '*'
    DIV = '/'
    SQR = '**'
    AT = '@'
    GAMMA = 'gamma'
    TRUE = 'true'
    FALSE = 'false'
    NIL = 'nil'
    DUMMY = 'dummy'
    WITHIN = 'within'
    AND_OP = 'and'
    REC = 'rec'
    EQUAL = '='
    FCN_FORM = 'fcn_form'
    BRACES = '()'
    COMMA = ','


class Node:
    def __init__(self,node_type:NodeType, value,children_count):
        self.node_type=node_type
        self.value=value
        self.children_count=children_count


class parser:
    def __init__(self, token_list):
        self.token_list = token_list
        self.string_ast=[]
        self.ast = []
    #==========================printing part========================
    def convert_ast_to_string_ast(self):
        dots = ""
        stack = []

        while self.ast:
            if not stack:
                if self.ast[-1].children_count == 0:
                    self.add_strings(dots, self.ast.pop())
                else:
                    node = self.ast.pop()
                    stack.append(node)
            else:
                if self.ast[-1].children_count > 0:
                    node = self.ast.pop()
                    stack.append(node)
                    dots += "."
                else:
                    stack.append(self.ast.pop())
                    dots += "."
                    while stack[-1].children_count == 0:
                        self.add_strings(dots, stack.pop())
                        if not stack:
                            break
                        dots = dots[:-1]
                        node = stack.pop()
                        node.children_count -= 1
                        stack.append(node)

        # Reverse the list
        self.string_ast.reverse()
        return self.string_ast

    def add_strings(self, dots, node):
        if node.node_type in [NodeType.IDENTIFIER, NodeType.INTEGER, NodeType.STRING, NodeType.TRUE,
                         NodeType.FALSE, NodeType.NIL, NodeType.DUMMY]:
            self.string_ast.append(dots + "<" + node.node_type.name.upper() + ":" + node.value + ">")
        elif node.node_type == NodeType.FCN_FORM:
            self.string_ast.append(dots + "function_form")
        else:
            self.string_ast.append(dots + node.value)
            # ===============over==============================
            # 
            # 
            #  
    def print_ast(self):
        for node in self.ast:
            print(f"Node Type: {node.node_type}, Value: {node.value}, Children Count: {node.children_count}")


    def parse(self):
        self.token_list.append(Token(END_OF_TOKENS,'EOT'))
        self.E()
        if self.token_list[0].get_type() == END_OF_TOKENS:
            print("Parsing completed successfully.")
            return self.ast
        else:
            print("error in parsing tokens.")
            # do error handling
            return None
        
    #  E	->’let’ D ’in’ E 	=> ’let’
	#       -> ’fn’ Vb+ ’.’ E 	=> ’lambda’
	#       -> Ew;  
    def E(self):
        if self.token_list: #never be emty cus EOT is added 
            token=self.token_list[0]
            print('inside E block next token is ',token.get_value())
            if token.get_type()==KEYWORD and token.get_value()=='let':
                print('inside let block')
                self.token_list.pop(0) #remove let
                self.D()
                if self.token_list[0].get_value() !='in':
                    print('error inside block E let, expected in, but got',self.token_list[0].value)
                # else ekak onimada?
                self.token_list.pop(0) #remove in
                self.E()
                self.ast.append(Node(NodeType.LET,'let',2))
            elif token.get_type()==KEYWORD and token.get_value()=='fn':
                print('inside lambda block')
                self.token_list.pop(0) #remove fn
                n=0
                while self.token_list and (self.token_list[0].get_type()==IDENTIFIER or self.token_list[0].get_type()=='('):
                    # print('inside lambda while')
                    n+=1
                    self.Vb()
                if self.token_list[0].get_value() !='.':
                    print('error inside block E lambda, expected ., but got',self.token_list[0].value)
                # else if needed
                print('popping .')
                self.token_list.pop(0)
                self.E()
                self.ast.append(Node(NodeType.LAMBDA,'lambda',n+1))
            else:
                print('else eket awa let ---> Ew')
                self.Ew()
            print('going out from E block')
        else:
            print('token list is empty')
            return None
    
    # Ew    ->T ’where’ Dr  => ’where’
    #       ->T;
    def Ew(self):
        print('inside Ew block')
        self.T()
        if self.token_list[0].get_type() == KEYWORD and self.token_list[0].get_value() == 'where':
            print('inside Ew  eke where block')
            self.token_list.pop(0) #pop where
            self.Dr()
            self.ast.append(Node(NodeType.WHERE,'where',2))  
        print('going out from Ew block')


    #T  ->Ta (’,’ Ta )+     => ’tau’
    #   ->Ta
    def T(self):
        print('inside T block')
        self.Ta()
        n=1
        while self.token_list[0].get_type() == COMMA:
            self.token_list.pop(0) #pop ,
            self.Ta()
            n+=1
        if n>1:
            self.ast.append(Node(NodeType.TAU,'tau',n))
        print('going out from T block')

    #Ta     ->Ta ’aug’ Tc       => ’aug’
    #       ->Tc
    #since there's left recursion we can convert the grammar like this
    #      Ta -> Tc (’aug’ Tc )*
    def Ta(self):
        print('inside Ta block')
        self.Tc()
        while self.token_list[0].get_value() == 'aug':
            print('inside Ta  eke while  aug block')
            self.token_list.pop(0)
            self.Tc()
            self.ast.append(Node(NodeType.AUG,'aug',2))

    #Tc     -> B ’->’ Tc ’|’ Tc         => ’->’
    #       -> B ;
    def Tc(self):
        print('inside Tc block')
        self.B()
        if self.token_list[0].get_value() == '->':
            print('inside Tc  eke -> block')
            self.token_list.pop(0)
            self.Tc()
            if self.token_list[0].get_value() != '|':
                print('error expected | but got',self.token_list[0].get_value())
            self.token_list.pop(0)
            self.Tc()
            self.ast.append(Node(NodeType.ARROW,'->',3))

#   B   -> B ’or’ Bt       => ’or’
#       -> Bt
#convert as follow
#   B   -> Bt ('or' Bt)*
    def B(self):
        print('inside b block')
        self.Bt()
        while self.token_list[0].get_value()=='or':
            self.token_list.pop(0)
            self.Bt()
            self.ast.append(Node(NodeType.OR,'or',2))

#   Bt  -> Bt ’&’ Bs     => ’&’
#       -> Bs
#convert as follow
#   Bt   -> Bs ('&' Bs)*
    def Bt(self):
        print('inside bt block')
        self.Bs()
        while self.token_list[0].get_value()=='&':
            self.token_list.pop(0)
            self.Bs()
            self.ast.append(Node(NodeType.AND,'&',2))
    
#   Bs  -> ’not’ Bp     => ’not’
#       -> Bp
    def Bs(self):
        print('inside bs block')
        if self.token_list[0].get_value()=='not':
            print('inside not')
            self.token_list.pop(0)
            self.Bp()
            self.ast.append(Node(NodeType.NOT,'not',1))
        else:
            self.Bp()

#Bp  -> A (’gr’ | ’>’ ) A    => ’gr’
#    -> A (’ge’ | ’>=’) A    => ’ge’
#    -> A (’ls’ | ’<’ ) A    => ’ls’
#    -> A (’le’ | ’<=’) A    => ’le’
#    -> A ’eq’ A             => ’eq’
#    -> A ’ne’ A             => ’ne
#    -> A

    def Bp(self):
        print('inside Bp')
        self.A()
        token=self.token_list[0].get_value()
        if token in ['gr','>','ge','>=','ls','<','le','<=','eq','ne']:
            self.token_list.pop(0)
            self.A()
            if token in ['gr','>']:
                self.ast.append(Node(NodeType.GR,'gr',2))
            elif token in ['ge','>=']:
                self.ast.append(Node(NodeType.GE,'ge',2))
            elif token in ['ls','<']:
                self.ast.append(Node(NodeType.LS,'ls',2))
            elif token in ['le','<=']:
                self.ast.append(Node(NodeType.LE,'le',2))
            elif token=='eq':
                self.ast.append(Node(NodeType.EQ,'eq',2))
            elif token=='ne':
                self.ast.append(Node(NodeType.NE,'ne',2))

# ================================================Arithmetic Expressions=======================

# A ->   A  ’+’ At      => ’+’
#   ->   A  ’-’ At      => ’-’
#   ->      ’+’ At
#   ->      ’-’ At      =>’neg’
#   ->          At
    def A(self):
        print('inside A block')
        if self.token_list[0].get_value()=='+':
            self.token_list.pop(0)
            print('inside A block popping +')
            self.At()
        elif self.token_list[0].get_value()=='-':
            self.token_list.pop(0)
            print('inside A block popping -')
            self.At()
            self.ast.append(Node(NodeType.NEG,'neg',1))
        else:
            self.At()
        while self.token_list[0].get_value() in ['+','-']:
            if self.token_list[0].get_value()=='+':
                self.token_list.pop(0)
                self.At()
                self.ast.append(Node(NodeType.PLUS,'+',2))
            else:
                self.token_list.pop(0)
                self.At()
                self.ast.append(Node(NodeType.MINUS,'-',2))

# At -> At ’*’ Af    => ’*’
#    -> At ’/’ Af    => ’/’
#    -> Af ;  
    def At(self):
        print('inside At')
        self.Af()
        while self.token_list[0].get_value() in ['*','/']:
            if self.token_list[0].get_value()=='*':
                self.token_list.pop(0)
                self.Af()
                self.ast.append(Node(NodeType.MUL,'*',2))
            else:
                self.token_list.pop(0)
                self.Af()
                self.ast.append(Node(NodeType.DIV,'/',2)) 
        print('going out from At block')      

#   Af  -> Ap ’**’ Af    => ’**’
#       -> Ap
#convert as
#   Af  -> Ap (’**’ Af)*
    def Af(self):
        print('inside Af')
        self.Ap()
        while self.token_list[0].get_value()=='**':
            self.token_list.pop(0)
            self.Af()
            self.ast.append(Node(NodeType.SQR,'**',2))
        print('going out from Af block')

# Ap    -> Ap ’@’ ’<IDENTIFIER>’ R      => ’@’
#       -> R
#convert as,
# Ap    -> R ( ’@’ ’<IDENTIFIER>’ R)*
    def Ap(self):
        print('inside Ap')
        self.R()
        while self.token_list[0].get_value()=='@':
            self.token_list.pop(0) # pop @
            if self.token_list[0].get_type()!=IDENTIFIER:
                print('error ! expected an identifier. but god this',self.token_list[0].get_value(),self.token_list[0].get_type())
                return
            self.ast.append(Node(NodeType.IDENTIFIER,self.token_list[0].get_value(),0))
            self.token_list.pop(0)
            self.R()
            self.ast.append(Node(NodeType.AT,'@',3))
        print('going out from Ap block')

#==============================Rators and Rands==============================================

# R -> R Rn  =>’gamma'
#   -> Rn
# conver as
# R -> Rn+
    def R(self):
        print('inside R block')
        self.Rn()
        while self.token_list[0].get_type() in [IDENTIFIER,STRING,INTEGER] or self.token_list[0].get_value() in ['true','false','nil','(','dummy']:
            self.Rn()
            self.ast.append(Node(NodeType.GAMMA,'gamma',2))
            print('inside R block while appending gamma')
        print('going out from R block')
        
# Rn    -> ’<IDENTIFIER>’
#       -> ’<INTEGER>’
#       -> ’<STRING>’
#       -> ’true’           => ’true’
#       -> ’false’          => ’false’
#       -> ’nil’            => ’nil’
#       -> ’(’ E ’)’
#       -> ’dummy’          => ’dummy’ ;
    def Rn(self):
        print('inside Rn')
        token_type=self.token_list[0].get_type()
        token_value=self.token_list[0].get_value()
        self.token_list.pop(0)
        if token_type==IDENTIFIER:
            self.ast.append(Node(NodeType.IDENTIFIER,token_value,0))
            print('inside idenfier block poping and append ast ', token_value)
        elif token_type==INTEGER:
            self.ast.append(Node(NodeType.INTEGER,token_value,0))
            print('inside int block poping and append ast ', token_value)
        elif token_type==STRING:
            self.ast.append(Node(NodeType.STRING,token_value,0))
            print('inside str block poping and append ast ', token_value)
        elif token_value=='true':
            self.ast.append(Node(NodeType.TRUE,'true',0))
            print('inside true block poping and append ast ', token_value)
        elif token_value=='false':
            self.ast.append(Node(NodeType.TRUE,'false',0))
            print('inside false block poping and append ast ', token_value)
        elif token_value=='nil':
            self.ast.append(Node(NodeType.NIL,'nil',0))
            print('inside nil block poping and append ast ', token_value)
        elif token_value=='(':
            print('inside ( block rule Rn        -> ( E )')
            self.E()
            if self.token_list[0].get_value()!=')':
                print('expected a closing bracket, but got',self.token_list[0].get_value())
                return
            self.token_list.pop(0)
        elif token_value=='dummy':
            print('inside dummy block poping and append ast ', token_value)
            self.ast.append(Node(NodeType.DUMMY,'dummy',0))
        else:
            print('error ekak bn Rn eke. else eke inne')
        print('going out from Rn block')

#=======================Definitions==============================================================
#  D    -> Da ’within’ D    => 'within'
#       -> Da
    def D(self):
        print('inside D block')
        self.Da()
        while self.token_list[0].get_value()=='within':
            self.token_list.pop(0)
            self.D()
            self.ast.append(Node(NodeType.WITHIN,'within',2))

#   Da  -> Dr ( ’and’ Dr )+     => 'and'
#       -> Dr
    def Da(self):
        print('inside Da block')
        self.Dr()
        n=1
        while self.token_list[0].get_value()=='and':
            self.token_list.pop(0)
            self.Dr()
            n+=1
        if n>1:
            self.ast.append(Node(NodeType.AND_OP,'and',n))
    
# Dr  -> 'rec' Db   => 'rec'
#     -> Db
    def Dr(self):
        print('inside Dr block')
        if self.token_list[0].get_value()=='rec':
            self.token_list.pop(0)
            self.Db()
            self.ast.append(Node(NodeType.REC,'rec',1))
        else:
            self.Db()

# Db    -> Vl ’=’ E                     => ’=’
#       -> ’<IDENTIFIER>’ Vb+ ’=’ E     => 'fcn_form'
#       -> ’(’ D ’)’ 
# --------------------------------------------------------
# Vl -> '<IDENTIFIER>' list ','    => ',' ?  
# --------------------------------------------------------
# Vb    -> ’<IDENTIFIER>’
#       -> ’(’ Vl ’)’
#       -> ’(’ ’)’
# --------------------------------------------------------
# Db    -> '<IDENTIFIER>' list ','  ’=’ E                     => ’=’
#       -> ’<IDENTIFIER>’ [’<IDENTIFIER>’ |’(’ '<IDENTIFIER>' list ',' ’)’ | ’(’ ’)’ ]+ ’=’ E     => 'fcn_form'
#       -> ’(’ D ’)’ 



    def Db(self):
        print('inside Db block')
        # Db -> ( D )
        if self.token_list[0].get_value()=='('and self.token_list[0].get_type()=='(':
            self.token_list.pop(0) #pop (
            self.D()
            if self.token_list[0].get_value()!=')':
                print('expected a closing bracket, but got',self.token_list[0].get_value())
                return
            self.token_list.pop(0) #pop )
# Db    -> Vl ’=’ E                     => ’=’
#       -> ’<IDENTIFIER>’ Vb+ ’=’ E     => 'fcn_form'

# --------------------------------------------------------
# Db    -> '<IDENTIFIER>' list ','  ’=’ E                     => ’=’
#       -> ’<IDENTIFIER>’ (’<IDENTIFIER>’ |’(’ Vl ’)’ | ’(’ ’)’ )+ ’=’ E     => 'fcn_form'
#       -> ’<IDENTIFIER>’ [’<IDENTIFIER>’ |’(’ '<IDENTIFIER>' list ',' ’)’ | ’(’ ’)’ ]+ ’=’ E     => 'fcn_form'
        elif self.token_list[0].get_type()==IDENTIFIER:
            # Db -> <IDENTIFIER> Vb+ = E
            if self.token_list[1].get_value()=='='or self.token_list[1].get_value()==',':
                self.Vl()
                if self.token_list[0].get_value()!='=':
                    print('error inside Db block, expected = but got',self.token_list[0].get_value())
                    return
                self.token_list.pop(0) # pop =
                self.E()
                self.ast.append(Node(NodeType.EQUAL,'=',2))
            else:
                self.ast.append(Node(NodeType.IDENTIFIER,self.token_list[0].get_value(),0)) 
                self.token_list.pop(0) # pop identifier
                n=0
                while self.token_list[0].get_type()==IDENTIFIER or self.token_list[0].get_value()=='(':
                    n+=1
                    self.Vb()
                if self.token_list[0].get_value()!='=':
                    print('error inside Db block, expected = but got',self.token_list[0].get_value())
                    return
                self.token_list.pop(0) # pop =
                self.E()
                self.ast.append(Node(NodeType.FCN_FORM,'fcn_form',n+2))
        else:
            print('error inside Db')

            # if self.token_list[1].get_type()==IDENTIFIER or self.token_list[1].get_value()=='(':
            #     self.ast.append(Node(NodeType.IDENTIFIER,self.token_list[0].get_value(),0)) 
            #     self.token_list.pop(0) # pop identifier
            #     n=0
            #     while self.token_list[0].get_type()==IDENTIFIER or self.token_list[0].get_value()=='(':
            #         n+=1
            #         self.Vb()
            #     if self.token_list[0].get_value()!='=':
            #         print('error inside Db block, expected = but got',self.token_list[0].get_value())
            #         return
            #     self.token_list.pop(0) # pop =
            #     self.E()
            #     self.ast.append(Node(NodeType.FCN_FORM,'fcn_form',n+2))
            # Db -> Vl = E
            # else:
            #     self.Vl()
            #     if self.token_list[0].get_value()!='=':
            #         print('error inside Db block, expected = but got',self.token_list[0].get_value())
            #         return
            #     self.token_list.pop(0)
            #     self.E()
            #     self.ast.append(Node(NodeType.EQUAL,'=',2))

# Vb    -> ’<IDENTIFIER>’
#       -> ’(’ Vl ’)’
#       -> ’(’ ’)’
    def Vb(self):
        print('inside Vb block')
        if self.token_list[0].get_type()==IDENTIFIER:
            self.ast.append(Node(NodeType.IDENTIFIER,self.token_list[0].get_value(),0))
            print('popping identifier',self.token_list[0].get_value())
            self.token_list.pop(0)
        elif self.token_list[0].get_value()=='('and self.token_list[0].get_type()=='(':
            if self.token_list[1].get_value()==')' and self.token_list[1].get_type()==')':
                self.token_list.pop(0) # pop (
                self.token_list.pop(0) # pop )
                self.ast.append(Node(NodeType.BRACES,'()',0))
            elif self.token_list[1].get_type()==IDENTIFIER:
                self.token_list.pop(0) # pop (
                self.Vl()
                if self.token_list[0].get_value()!=')':
                    print('expected a closing bracket, but got',self.token_list[0].get_value())
                    return
                self.token_list.pop(0) # pop )
    
    # Vl -> '<IDENTIFIER>' list ','    => ',' ?            
    def Vl(self):
        print('inside Vl block')
        self.ast.append(Node(NodeType.IDENTIFIER,self.token_list[0].get_value(),0))
        print('popping identifier',self.token_list[0].get_value())
        self.token_list.pop(0) 
        n=1
        while self.token_list[0].get_type()==',' and self.token_list[0].get_value()==',':
            print('inside Vl  eke while block popping ,',self.token_list[0].get_value())
            self.token_list.pop(0)     # pop ,
            if self.token_list[0].get_type()!=IDENTIFIER:
                print('error inside Vl block, expected an identifier but got',self.token_list[0].get_value())
                return
            self.ast.append(Node(NodeType.IDENTIFIER,self.token_list[0].get_value(),0))
            print('inside vl while popping identifier',self.token_list[0].get_value())
            self.token_list.pop(0)
            n+=1
        if n>1:
            self.ast.append(Node(NodeType.COMMA,',',n))
        print('comma enne methanin=================')


# =========================testing part========================
# code="(print (x, sqr x, x* sqr x, sqr x ** 2) where sqr x = x**2) where x=3" 
# #meka waradiyt enne, comma ekk enawa, Vl eke awla
# code="let add ( x,y) = x+y in print ( add (3,4))"   # meka hari
# code = " let c=3 within f x=x+c in print ( f 3 )"
# code="let rec r s = s eq '' '' -> '' '' | conc (r (stern s)) (stem s) within p s = not isstring s -> ''error'' | s eq r s in print (p ''1234'' , p ''abcba'' )"
# code="let add x y = x+y in print (2 @ add 3 @ add 4)"
code="""
let rec rev s =
    s eq '''' -> ''''
    | (rev (stern s)) @ conc (stem s)
within 
    pairs (s1,s2) = 
        not (isstring s1 & isstring s2)
        -> '' both args not strings''
        | p (rev s1 , rev s2 )
        where rec p (s1,s2)=
        s1 eq '''' & s2 eq ''''
        ->nil
        |(stern s1 eq '''' & stern s2 ne '''') or 
        (stern s1 ne '''' & stern s2 eq '''')
        -> ''unequal length strings''
        |(p (stern s1, stern s2)
        aug ((stem s1) @ conc (stem s2)))
in print (pairs (''abc'', ''def''))
"""
code="""
let Sum(A) = Psum (A,Order A ) 
where rec Psum (T,N) = N eq 0 -> 0 
| Psum(T,N-1)+T N 
in Print ( Sum (1,2,3,4,5) ) """
list=tokenizer(code)
for t in list:
    print(t.get_type(),t.get_value())

parser=parser(list)
parser.parse()
print('=============================')
parser.print_ast()
print('=============================')
ast=parser.convert_ast_to_string_ast()
for t in ast:
    print(t)
    # need functions for build ast


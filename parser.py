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
            print('inside E block')
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



    def Ta(self):
        pass
    def D(self):
        pass
    def Dr(self):
        pass
    def Vb(self):
        pass

# =========================testing part========================
code="kk"
list=tokenizer(code)
for t in list:
    print(t.get_type(),t.get_value())

parser=parser(list)
parser.parse()

    # need functions for build ast


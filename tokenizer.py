import re

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def get_type(self):
        return self.type

    def get_value(self):
        return self.value

# Define token type constants
KEYWORD = 'KEYWORD'
IDENTIFIER = 'IDENTIFIER'
INTEGER = 'INTEGER'
OPERATOR = 'OPERATOR'
STRING = 'STRING'
SPACES = 'SPACES'  
COMMENT = 'COMMENT' 
PUNCTUATION = 'PUNCTUATION'

token_types = {
    COMMENT: r'//.*',
    KEYWORD: r'\b(let|in|fn|where|aug|or|not|gr|ge|ls|le|eq|ne|true|false|nil|dummy|within|and|rec)\b',
    IDENTIFIER: r'[a-zA-Z][a-zA-Z0-9_]*',
    INTEGER: r'\d+',
    OPERATOR: r'[+\-*<>&.@/:=~|$!#%^_\[\]{}"\'?]+',
    STRING: r"'''(?:\\t|\\n|\\\\|\\'|\\\"|[();, a-zA-Z0-9+\-*/<>&.@/:=˜|$!#%ˆ_\[\]{}\"`?])*'''",
    SPACES: r'\s+',
    PUNCTUATION: r'[();,]'
}

# Combine into named regex groups
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_types.items())
compiled_regex = re.compile(token_regex)

def tokenizer(code):
    tokens = []
    pos = 0
    length = len(code)

    while pos < length:
        match = compiled_regex.match(code, pos) #scanning tokens
        if not match:
            raise SyntaxError(f"Unrecognized token at position {pos}: {code[pos]!r}")
        
        kind = match.lastgroup
        value = match.group()

        if kind not in ['SPACES', 'COMMENT']: #screening unwanted tokens
            if kind == 'PUNCTUATION':
                kind = value  
            tokens.append(Token(kind, value))

        pos = match.end()

    return tokens

code="""
//its a comment//
Print((fn f. f 2) (fn x. x eq 1 -> 1 | x+2))
"""
for t in tokenizer(code):
    print(t.get_type(), t.get_value())
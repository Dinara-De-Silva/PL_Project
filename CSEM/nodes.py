class Symbol:
    """Base class for all symbols in the CSE Machine."""
    
    def __init__(self, data):
        self.data = data

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

class Rand(Symbol):
    """Base class for operand symbols."""
    
    def __init__(self, data):
        super().__init__(data)

class Rator(Symbol):
    """Base class for operator symbols."""
    
    def __init__(self, data):
        super().__init__(data)

class B(Symbol):
    """Beta node for conditional expressions."""
    
    def __init__(self):
        super().__init__("b")
        self.symbols = []

class Beta(Symbol):
    """Beta symbol for conditional branching."""
    
    def __init__(self):
        super().__init__("beta")

class Bool(Rand):
    """Boolean value symbol."""
    
    def __init__(self, data):
        super().__init__(data)

class Bop(Rator):
    """Binary operator symbol."""
    
    def __init__(self, data):
        super().__init__(data)

class Delta(Symbol):
    """Delta symbol for control structures."""
    
    def __init__(self, index):
        super().__init__("delta")
        self.index = index
        self.symbols = []

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index

class Dummy(Rand):
    """Dummy symbol for placeholder values."""
    
    def __init__(self):
        super().__init__("dummy")

class E(Symbol):
    """Environment symbol for variable bindings."""
    
    def __init__(self, index):
        super().__init__("e")
        self.index = index
        self.parent = None
        self.is_removed = False
        self.values = {}

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self):
        return self.parent

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index

    def set_is_removed(self, is_removed):
        self.is_removed = is_removed

    def get_is_removed(self):
        return self.is_removed

    def lookup(self, identifier):
        """Look up an identifier in the environment or its parents."""
        for key in self.values:
            if key.get_data() == identifier.get_data():
                return self.values[key]
        return self.parent.lookup(identifier) if self.parent else Symbol(identifier.get_data())

class Err(Symbol):
    """Error symbol for invalid operations."""
    
    def __init__(self):
        super().__init__("")

class Eta(Symbol):
    """Eta symbol for recursive function handling."""
    
    def __init__(self):
        super().__init__("eta")
        self.index = None
        self.environment = None
        self.identifier = None
        self.lambda_expr = None

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index

    def set_environment(self, environment):
        self.environment = environment

    def get_environment(self):
        return self.environment

    def set_identifier(self, identifier):
        self.identifier = identifier

    def set_lambda(self, lambda_expr):
        self.lambda_expr = lambda_expr

    def get_lambda(self):
        return self.lambda_expr

class Gamma(Symbol):
    """Gamma symbol for function application."""
    
    def __init__(self):
        super().__init__("gamma")

class Id(Rand):
    """Identifier symbol."""
    
    def __init__(self, data):
        super().__init__(data)

class Int(Rand):
    """Integer value symbol."""
    
    def __init__(self, data):
        super().__init__(data)

class Lambda(Symbol):
    """Lambda expression symbol."""
    
    def __init__(self, index):
        super().__init__("lambda")
        self.index = index
        self.environment = None
        self.identifiers = []
        self.delta = None

    def set_environment(self, environment):
        self.environment = environment

    def get_environment(self):
        return self.environment

    def set_delta(self, delta):
        self.delta = delta

    def get_delta(self):
        return self.delta

    def get_index(self):
        return self.index

class Str(Rand):
    """String value symbol."""
    
    def __init__(self, data):
        super().__init__(data)

class Tau(Symbol):
    """Tau symbol for tuple creation."""
    
    def __init__(self, n):
        super().__init__("tau")
        self.n = n

    def set_n(self, n):
        self.n = n

    def get_n(self):
        return self.n

class Tup(Rand):
    """Tuple symbol for grouped values."""
    
    def __init__(self):
        super().__init__("tup")
        self.symbols = []

class Uop(Rator):
    """Unary operator symbol."""
    
    def __init__(self, data):
        super().__init__(data)

class Ystar(Symbol):
    """Ystar symbol for recursion."""
    
    def __init__(self):
        super().__init__("<Y*>")
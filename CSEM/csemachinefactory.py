from .nodes import *
from .csemachine import CSEMachine

class CSEMachineFactory:
    """Factory class to create and configure a CSE Machine from an AST."""
    
    def __init__(self):
        """Initialize the factory with an initial environment and counters."""
        self.initial_environment = E(index=0)
        self.lambda_counter = 1  # Counter for Lambda indices
        self.delta_counter = 0   # Counter for Delta indices

    def create_symbol(self, node):
        """Create a symbol based on the node's data."""
        data = node.get_data()
        
        # Unary operators
        if data in ("not", "neg"):
            return Uop(data)
        
        # Binary operators
        if data in ("+", "-", "*", "/", "**", "&", "or", "eq", "ne", "ls", "le", "gr", "ge", "aug"):
            return Bop(data)
        
        # Special symbols
        if data == "gamma":
            return Gamma()
        if data == "tau":
            return Tau(len(node.get_children()))
        if data == "<Y*>":
            return Ystar()
        
        # Literals and identifiers
        if data.startswith("<IDENTIFIER:"):
            return Id(data[12:-1])
        if data.startswith("<INTEGER:"):
            return Int(data[9:-1])
        if data.startswith("<STRING:"):
            return Str(data[9:-2])
        if data.startswith("<NIL"):
            return Tup()
        if data.startswith("<TRUE_VALUE:t"):
            return Bool("true")
        if data.startswith("<TRUE_VALUE:f"):
            return Bool("false")
        if data.startswith("<dummy>"):
            return Dummy()
        
        # Handle unknown node types
        print(f"Error: Unrecognized node data: {data}")
        return Err()

    def create_beta(self, node):
        """Create a Beta node with pre-order traversal symbols."""
        beta = B()
        beta.symbols = self.traverse_pre_order(node)
        return beta

    def create_lambda(self, node):
        """Create a Lambda node with identifiers and delta."""
        lambda_expr = Lambda(index=self.lambda_counter)
        self.lambda_counter += 1
        lambda_expr.set_delta(self.create_delta(node.get_children()[1]))
        
        # Handle single or multiple identifiers
        identifier_node = node.get_children()[0]
        if identifier_node.get_data() == ",":
            for identifier in identifier_node.get_children():
                lambda_expr.identifiers.append(Id(identifier.get_data()[12:-1]))
        else:
            lambda_expr.identifiers.append(Id(identifier_node.get_data()[12:-1]))
        return lambda_expr

    def traverse_pre_order(self, node):
        """Perform pre-order traversal of the AST to generate symbols."""
        symbols = []
        data = node.get_data()
        
        if data == "lambda":
            symbols.append(self.create_lambda(node))
        elif data == "->":
            symbols.append(self.create_delta(node.get_children()[1]))
            symbols.append(self.create_delta(node.get_children()[2]))
            symbols.append(Beta())
            symbols.append(self.create_beta(node.get_children()[0]))
        else:
            symbols.append(self.create_symbol(node))
            for child in node.get_children():
                symbols.extend(self.traverse_pre_order(child))
        return symbols

    def create_delta(self, node):
        """Create a Delta node with pre-order traversal symbols."""
        delta = Delta(index=self.delta_counter)
        self.delta_counter += 1
        delta.symbols = self.traverse_pre_order(node)
        return delta

    def initialize_control(self, ast):
        """Initialize the control structure with the AST root."""
        return [self.initial_environment, self.create_delta(ast.get_root())]

    def initialize_stack(self):
        """Initialize the stack with the initial environment."""
        return [self.initial_environment]

    def initialize_environment(self):
        """Initialize the environment with the initial environment."""
        return [self.initial_environment]

    def create_cse_machine(self, ast):
        """Create and return a configured CSEMachine instance."""
        control = self.initialize_control(ast)
        stack = self.initialize_stack()
        environment = self.initialize_environment()
        return CSEMachine(control, stack, environment)
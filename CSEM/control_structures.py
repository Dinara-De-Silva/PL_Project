from .nodes import *
from .csemachine import CSEMachine

class ControlStructures:
    """
    This class generates control structures based on the given standardized abstract syntax tree (AST) of a program.
    """

    def __init__(self):
        self.env0 = E(0)    
        self.lambda_index = 1  # Counter to track lambda symbols
        self.delta_index = 0   # Counter to track delta expressions

    def map_ast_node_to_symbol(self, node):
        data = node.get_data()
        # Unary operators
        if data in ("not", "neg"):
            return Uop(data)
        # Binary operators
        elif data in ("+", "-", "*", "/", "**", "&", "or", "eq", "ne", "ls", "le", "gr", "ge", "aug"):
            return Bop(data)
        # Special symbols
        elif data == "gamma":
            return Gamma()
        elif data == "tau":
            return Tau(len(node.get_children()))
        elif data == "<Y*>":
            return Ystar()
        # Identifiers and constants
        elif data.startswith("<IDENTIFIER:"):
            return Id(data[12:-1])
        elif data.startswith("<INTEGER:"):
            return Int(data[9:-1])
        elif data.startswith("<STRING:"):
            return Str(data[9:-2])
        elif data.startswith("<NIL"):
            return Tup()
        elif data.startswith("<TRUE_VALUE:t"):
            return Bool("true")
        elif data.startswith("<TRUE_VALUE:f"):
            return Bool("false")
        elif data.startswith("<dummy>"):
            return Dummy()
        # Error fallback
        else:
            print("Error: Unrecognized node data:", data)
            return Err()

    def create_B(self, node):
        """
        Creates a B symbol that holds the condition of conditional expessions.
        """
        b_structure = B()
        b_structure.symbols = self.pre_order_traverse(node)
        return b_structure

    def create_lambda(self, node):
        """
        Handles the creation of a new control structure and setting the lambda index and identifiers.
        """
        lambda_structure = Lambda(self.lambda_index)
        self.lambda_index += 1

        lambda_structure.set_delta(self.create_delta(node.get_children()[1]))

        param_node = node.get_children()[0]
        if param_node.get_data() == ",":
            # Multiple parameters
            for child in param_node.get_children():
                identifier_name = child.get_data()[12:-1]
                lambda_structure.identifiers.append(Id(identifier_name))
        else:
            # Single parameter
            identifier_name = param_node.get_data()[12:-1]
            lambda_structure.identifiers.append(Id(identifier_name))

        return lambda_structure

    def pre_order_traverse(self, node):
        symbols = []
        if node.get_data() == "lambda":
            # Handling Lambda encounters
            symbols.append(self.create_lambda(node))
        elif node.get_data() == "->":
            # Handling conditional expressions (->)
            symbols.append(self.create_delta(node.get_children()[1]))
            symbols.append(self.create_delta(node.get_children()[2]))
            symbols.append(Beta())
            symbols.append(self.create_B(node.get_children()[0]))
        else:
            # Standard nodes
            symbols.append(self.map_ast_node_to_symbol(node))
            for child in node.get_children():
                symbols.extend(self.pre_order_traverse(child))
        return symbols

    def create_delta(self, node):
        delta_structure = Delta(self.delta_index)
        self.delta_index += 1
        delta_structure.symbols = self.pre_order_traverse(node)
        return delta_structure

    def create_control_structure(self, ast):
        root_delta = self.create_delta(ast.get_root())
        return [self.env0, root_delta]

    def create_stack(self):
        return [self.env0]

    def create_environment(self):
        return [self.env0]

    def create_cse_machine(self, ast):
        """
        Creates and returns a new CSE machine instance initialized with the control,
        stack, and environment structures.
        """
        control = self.create_control_structure(ast)
        stack = self.create_stack()
        environment = self.create_environment()
        return CSEMachine(control, stack, environment)
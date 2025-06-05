from .nodes import *
from .csemachine import CSEMachine

class ControlStructures:
    def __init__(self):
        self.e0 = E(0)
        self.i = 1 # Index for lambda expressions
        self.j = 0 # Index for delta expressions

    def get_symbol(self, node):
        data = node.get_data()
        if data in ("not", "neg"):
            return Uop(data)  # Unary operator symbol
        elif data in ("+", "-", "*", "/", "**", "&", "or", "eq", "ne", "ls", "le", "gr", "ge", "aug"):
            return Bop(data)  # Binary operator symbol
        elif data == "gamma":
            return Gamma()  # Gamma symbol
        elif data == "tau":
            return Tau(len(node.get_children()))  # Tau symbol with the number of children
        elif data == "<Y*>":
            return Ystar()  # Y* symbol
        else:
            if data.startswith("<IDENTIFIER:"):
                return Id(data[12:-1])  # Identifier symbol
            elif data.startswith("<INTEGER:"):
                return Int(data[9:-1])  # Integer symbol
            elif data.startswith("<STRING:"):
                return Str(data[9:-2])  # String symbol
            elif data.startswith("<NIL"):
                return Tup()  # Tuple symbol
            elif data.startswith("<TRUE_VALUE:t"):
                return Bool("true")  # Boolean true symbol
            elif data.startswith("<TRUE_VALUE:f"):
                return Bool("false")  # Boolean false symbol
            elif data.startswith("<dummy>"):
                return Dummy()  # Dummy symbol
            else:
                print("Err node:", data)
                return Err()  # Error symbol

    def create_B(self, node):
        b = B()
        b.symbols = self.get_pre_order_traverse(node)
        return b

    def create_lambda(self, node):
        lambda_expr = Lambda(self.i)
        self.i += 1
        lambda_expr.set_delta(self.create_delta(node.get_children()[1]))
        if node.get_children()[0].get_data() == ",":
            for identifier in node.get_children()[0].get_children():
                lambda_expr.identifiers.append(Id(identifier.get_data()[12:-1]))
        else:
            lambda_expr.identifiers.append(Id(node.get_children()[0].get_data()[12:-1]))
        return lambda_expr

    def get_pre_order_traverse(self, node):
        symbols = []
        if node.get_data() == "lambda":
            symbols.append(self.create_lambda(node))  # Lambda expression symbol
        elif node.get_data() == "->":
            symbols.append(self.create_delta(node.get_children()[1]))  # Delta symbol
            symbols.append(self.create_delta(node.get_children()[2]))  # Delta symbol
            symbols.append(Beta())  # Beta symbol
            symbols.append(self.create_B(node.get_children()[0]))  # B symbol
        else:
            symbols.append(self.get_symbol(node))
            
            for child in node.get_children():
                symbols.extend(self.get_pre_order_traverse(child))
        return symbols

    def create_delta(self, node):
        delta = Delta(self.j)
        self.j += 1
        delta.symbols = self.get_pre_order_traverse(node)
        return delta

    def create_control(self, ast):
        control = [self.e0, self.create_delta(ast.get_root())]
        return control

    def create_stack(self):
        return [self.e0]

    def create_environment(self):
        return [self.e0]
    

    # def print_symbol(self,symbol, indent=0):
    #     indent_str = '  ' * indent
    #     # Print basic data
    #     print(f"{indent_str}{symbol.__class__.__name__}: {symbol.get_data()}")

    #     # Print details for specific symbol types
    #     if isinstance(symbol, Delta):
    #         print(f"{indent_str}  Index: {symbol.get_index()}")
    #         print(f"{indent_str}  Symbols:")
    #         for s in symbol.symbols:
    #             self.print_symbol(s, indent + 2)
    #     elif isinstance(symbol, Lambda):
    #         print(f"{indent_str}  Index: {symbol.get_index()}")
    #         print(f"{indent_str}  Identifiers: {[id.get_data() for id in symbol.identifiers]}")
    #         print(f"{indent_str}  Delta:")
    #         self.print_symbol(symbol.get_delta(), indent + 2)
    #     elif isinstance(symbol, E):
    #         print(f"{indent_str}  Index: {symbol.get_index()}")
    #     elif isinstance(symbol, Id):
    #         print(f"{indent_str}  (Identifier)")
    #     elif isinstance(symbol, Bop):
    #         print(f"{indent_str}  (Binary Operator)")
    # # Add more elifs for other symbol types if needed
    # def print_control(self, control):
    #     for symbol in control:
    #         self.print_symbol(symbol)

    def create_cse_machine(self, ast):
        control = self.create_control(ast)
        # self.print_control(control)
        stack = self.create_stack()
        environment = self.create_environment()
        return CSEMachine(control, stack, environment)

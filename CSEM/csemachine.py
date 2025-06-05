from .nodes import *

class CSEMachine:
    """Control-Stack-Environment Machine for evaluating ASTs."""
    
    def __init__(self, control, stack, environment):
        """Initialize the CSE Machine with control, stack, and environment."""
        self.control = control
        self.stack = stack
        self.environment = environment
        self.environment_counter = 1  # Counter for environment indices

    def execute(self):
        """Execute the CSE Machine until the control structure is empty."""
        current_environment = self.environment[0]
        
        while self.control:
            current_symbol = self.control.pop()
            
            if isinstance(current_symbol, Id):
                self.stack.insert(0, current_environment.lookup(current_symbol))
            
            elif isinstance(current_symbol, Lambda):
                current_symbol.set_environment(current_environment.get_index())
                self.stack.insert(0, current_symbol)
            
            elif isinstance(current_symbol, Gamma):
                self.handle_gamma(current_environment)
            
            elif isinstance(current_symbol, E):
                self.handle_environment(current_symbol)
                current_environment = self.find_active_environment()
            
            elif isinstance(current_symbol, Rator):
                self.handle_operator(current_symbol)
            
            elif isinstance(current_symbol, Beta):
                self.handle_beta()
            
            elif isinstance(current_symbol, Tau):
                self.handle_tau(current_symbol)
            
            elif isinstance(current_symbol, Delta):
                self.control.extend(current_symbol.symbols)
            
            elif isinstance(current_symbol, B):
                self.control.extend(current_symbol.symbols)
            
            else:
                self.stack.insert(0, current_symbol)

    def handle_gamma(self, current_environment):
        """Handle Gamma symbol operations."""
        next_symbol = self.stack.pop(0)
        
        if isinstance(next_symbol, Lambda):
            self.apply_lambda(next_symbol, current_environment)
        elif isinstance(next_symbol, Tup):
            self.apply_tuple(next_symbol)
        elif isinstance(next_symbol, Ystar):
            self.apply_ystar(next_symbol)
        elif isinstance(next_symbol, Eta):
            self.apply_eta(next_symbol)
        else:
            self.apply_built_in_function(next_symbol)

    def apply_lambda(self, lambda_expr, current_environment):
        """Apply a Lambda expression."""
        new_env = E(self.environment_counter)
        self.environment_counter += 1
        
        if len(lambda_expr.identifiers) == 1:
            new_env.values[lambda_expr.identifiers[0]] = self.stack.pop(0)
        else:
            tup = self.stack.pop(0)
            for i, identifier in enumerate(lambda_expr.identifiers):
                new_env.values[identifier] = tup.symbols[i]
        
        for env in self.environment:
            if env.get_index() == lambda_expr.get_environment():
                new_env.set_parent(env)
                break
        
        self.control.append(new_env)
        self.control.append(lambda_expr.get_delta())
        self.stack.insert(0, new_env)
        self.environment.append(new_env)

    def apply_tuple(self, tup):
        """Apply tuple indexing operation."""
        index = int(self.stack.pop(0).get_data())
        self.stack.insert(0, tup.symbols[index - 1])

    def apply_ystar(self, ystar):
        """Apply Ystar for recursive function handling."""
        lambda_expr = self.stack.pop(0)
        eta = Eta()
        eta.set_index(lambda_expr.get_index())
        eta.set_environment(lambda_expr.get_environment())
        eta.set_identifier(lambda_expr.identifiers[0])
        eta.set_lambda(lambda_expr)
        self.stack.insert(0, eta)

    def apply_eta(self, eta):
        """Apply Eta for recursive function application."""
        lambda_expr = eta.get_lambda()
        self.control.append(Gamma())
        self.control.append(Gamma())
        self.stack.insert(0, eta)
        self.stack.insert(0, lambda_expr)

    def apply_built_in_function(self, symbol):
        """Apply built-in functions like Print, Stem, Stern, etc."""
        data = symbol.get_data()
        
        if data == "Print":
            pass  # Placeholder for Print function
        elif data == "Stem":
            s = self.stack.pop(0)
            s.set_data(s.get_data()[0])
            self.stack.insert(0, s)
        elif data == "Stern":
            s = self.stack.pop(0)
            s.set_data(s.get_data()[1:])
            self.stack.insert(0, s)
        elif data == "Conc":
            s1 = self.stack.pop(0)
            s2 = self.stack.pop(0)
            s1.set_data(s1.get_data() + s2.get_data())
            self.stack.insert(0, s1)
        elif data == "Order":
            tup = self.stack.pop(0)
            self.stack.insert(0, Int(str(len(tup.symbols))))
        elif data in ("Isinteger", "Isstring", "Istuple", "Isdummy", "Istruthvalue", "Isfunction"):
            self.apply_type_check(data)
        elif data in ("Null", "Itos"):
            pass  # Placeholder for Null and Itos functions

    def apply_type_check(self, function):
        """Apply type checking functions."""
        type_checks = {
            "Isinteger": Int,
            "Isstring": Str,
            "Istuple": Tup,
            "Isdummy": Dummy,
            "Istruthvalue": Bool,
            "Isfunction": Lambda
        }
        self.stack.insert(0, Bool(str(isinstance(self.stack[0], type_checks[function])).lower()))
        self.stack.pop(1)

    def handle_environment(self, env):
        """Handle environment cleanup."""
        self.stack.pop(1)
        self.environment[env.get_index()].set_is_removed(True)

    def find_active_environment(self):
        """Find the most recent non-removed environment."""
        for env in reversed(self.environment):
            if not env.get_is_removed():
                return env
        return self.environment[0]

    def handle_operator(self, operator):
        """Handle unary and binary operators."""
        if isinstance(operator, Uop):
            rand = self.stack.pop(0)
            self.stack.insert(0, self.apply_unary_operation(operator, rand))
        elif isinstance(operator, Bop):
            rand1 = self.stack.pop(0)
            rand2 = self.stack.pop(0)
            self.stack.insert(0, self.apply_binary_operation(operator, rand1, rand2))

    def handle_beta(self):
        """Handle conditional (Beta) expressions."""
        condition = self.stack.pop(0).get_data()
        if condition == "true":
            self.control.pop()
        else:
            self.control.pop(-2)

    def handle_tau(self, tau):
        """Handle tuple creation (Tau)."""
        tup = Tup()
        for _ in range(tau.get_n()):
            tup.symbols.append(self.stack.pop(0))
        self.stack.insert(0, tup)

    def write_stack_to_file(self, file_path):
        """Write the stack contents to a file."""
        with open(file_path, 'a') as file:
            for symbol in self.stack:
                file.write(symbol.get_data())
                if isinstance(symbol, (Lambda, Delta, E, Eta)):
                    file.write(str(symbol.get_index()))
                file.write(",")
            file.write("\n")

    def write_control_to_file(self, file_path):
        """Write the control structure contents to a file."""
        with open(file_path, 'a') as file:
            for symbol in self.control:
                file.write(symbol.get_data())
                if isinstance(symbol, (Lambda, Delta, E, Eta)):
                    file.write(str(symbol.get_index()))
                file.write(",")
            file.write("\n")

    @staticmethod
    def clear_file(file_path):
        """Clear the contents of a file."""
        open(file_path, 'w').close()

    def print_environment(self):
        """Print the environment hierarchy."""
        for env in self.environment:
            print(f"e{env.get_index()} --> ", end="")
            if env.get_index() != 0:
                print(f"e{env.get_parent().get_index()}")
            else:
                print()

    def convert_string_to_bool(self, data):
        """Convert string representation to boolean."""
        return data == "true"

    def apply_unary_operation(self, operator, operand):
        """Apply a unary operation."""
        if operator.get_data() == "neg":
            return Int(str(-int(operand.get_data())))
        if operator.get_data() == "not":
            return Bool(str(not self.convert_string_to_bool(operand.get_data())).lower())
        return Err()

    def apply_binary_operation(self, operator, operand1, operand2):
        """Apply a binary operation."""
        op = operator.get_data()
        if op in ("+", "-", "*", "/", "**"):
            val1 = int(operand1.get_data())
            val2 = int(operand2.get_data())
            operations = {
                "+": lambda x, y: x + y,
                "-": lambda x, y: x - y,
                "*": lambda x, y: x * y,
                "/": lambda x, y: int(x / y),
                "**": lambda x, y: x ** y
            }
            return Int(str(operations[op](val1, val2)))
        
        if op in ("&", "or", "eq", "ne", "ls", "le", "gr", "ge"):
            val1 = operand1.get_data()
            val2 = operand2.get_data()
            if op in ("&", "or"):
                val1 = self.convert_string_to_bool(val1)
                val2 = self.convert_string_to_bool(val2)
            operations = {
                "&": lambda x, y: x and y,
                "or": lambda x, y: x or y,
                "eq": lambda x, y: x == y,
                "ne": lambda x, y: x != y,
                "ls": lambda x, y: int(x) < int(y),
                "le": lambda x, y: int(x) <= int(y),
                "gr": lambda x, y: int(x) > int(y),
                "ge": lambda x, y: int(x) >= int(y)
            }
            return Bool(str(operations[op](val1, val2)).lower())
        
        if op == "aug":
            result = operand1 if isinstance(operand1, Tup) else Tup()
            if isinstance(operand2, Tup):
                result.symbols.extend(operand2.symbols)
            else:
                result.symbols.append(operand2)
            return result
        
        return Err()

    def format_tuple(self, tup):
        """Format a tuple for output."""
        result = "("
        for symbol in tup.symbols:
            result += (self.format_tuple(symbol) if isinstance(symbol, Tup) else symbol.get_data()) + ", "
        return result[:-2] + ")"

    def get_result(self):
        """Execute the machine and return the final result."""
        self.execute()
        result = self.stack[0]
        return self.format_tuple(result) if isinstance(result, Tup) else result.get_data()
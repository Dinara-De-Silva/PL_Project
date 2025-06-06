from .nodes import *

class CSEMachine:
    def __init__(self, control, stack, environment):
        self.control = control
        self.stack = stack
        self.environments = environment

    def execute(self):
        """Main execution loop of the CSE machine."""
        current_env = self.environments[0]
        new_env_index = 1

        while self.control:
            symbol = self.control.pop()

            # Identifier: push value from current environment
            if isinstance(symbol, Id):
                self.stack.insert(0, current_env.lookup(symbol))

            # Lambda: push Lambda and set its environment index
            elif isinstance(symbol, Lambda):
                symbol.set_environment(current_env.get_index())
                self.stack.insert(0, symbol)

            # Gamma application: apply to Lambda, Tup, Ystar, Eta, or built-in function
            elif isinstance(symbol, Gamma):
                next_symbol = self.stack.pop(0)
                if isinstance(next_symbol, Lambda):
                    
                    lambda_expr = next_symbol
                    new_env = E(new_env_index)
                    new_env_index += 1
                    
                    if len(lambda_expr.identifiers) == 1:
                        arg = self.stack.pop(0)
                        new_env.values[lambda_expr.identifiers[0]] = arg
                    else:
                        tup = self.stack.pop(0)
                        for i, ident in enumerate(lambda_expr.identifiers):
                            new_env.values[ident] = tup.symbols[i]
                    
                    for env in self.environments:
                        if env.get_index() == lambda_expr.get_environment():
                            new_env.set_parent(env)
                    current_env = new_env
                    self.control.append(new_env)
                    self.control.append(lambda_expr.get_delta())
                    self.stack.insert(0, new_env)
                    self.environments.append(new_env)

                elif isinstance(next_symbol, Tup):
                    # Tuple projection
                    index = int(self.stack.pop(0).get_data())
                    self.stack.insert(0, next_symbol.symbols[index - 1])

                elif isinstance(next_symbol, Ystar):
                    # Y* (recursive function)
                    lambda_expr = self.stack.pop(0)
                    eta = Eta()
                    eta.set_index(lambda_expr.get_index())
                    eta.set_environment(lambda_expr.get_environment())
                    eta.set_identifier(lambda_expr.identifiers[0])
                    eta.set_lambda(lambda_expr)
                    self.stack.insert(0, eta)

                elif isinstance(next_symbol, Eta):
                    # Eta reduction
                    eta = next_symbol
                    lambda_expr = eta.get_lambda()
                    self.control.extend([Gamma(), Gamma()])
                    self.stack.insert(0, eta)
                    self.stack.insert(0, lambda_expr)

                else:
                    # Built-in functions
                    self.handle_builtin(next_symbol)

            # End of environment 
            elif isinstance(symbol, E):
                self.stack.pop(1)
                self.environments[symbol.get_index()].set_is_removed(True)
               
                for env in reversed(self.environments):
                    if not env.get_is_removed():
                        current_env = env
                        break

            # Rator: unary or binary operation
            elif isinstance(symbol, Rator):
                if isinstance(symbol, Uop):
                    operand = self.stack.pop(0)
                    self.stack.insert(0, self.apply_unary(symbol, operand))
                elif isinstance(symbol, Bop):
                    operand1 = self.stack.pop(0)
                    operand2 = self.stack.pop(0)
                    self.stack.insert(0, self.apply_binary(symbol, operand1, operand2))

            # Conditional (Beta)
            elif isinstance(symbol, Beta):
                condition = self.stack.pop(0).get_data()
                if condition == "true":
                    self.control.pop()  # Remove false branch
                else:
                    self.control.pop(-2)  # Remove true branch

            # Tau: build tuple
            elif isinstance(symbol, Tau):
                new_tuple = Tup()
                for _ in range(symbol.get_n()):
                    new_tuple.symbols.append(self.stack.pop(0))
                self.stack.insert(0, new_tuple)

            # Delta/B: push symbols of block
            elif isinstance(symbol, (Delta, B)):
                self.control.extend(symbol.symbols)

            else:
                # Push constants or other values
                self.stack.insert(0, symbol)

    def handle_builtin(self, func_symbol):
        """Handle built-in function applications."""
        func_name = func_symbol.get_data()
        if func_name == "Stem":
            s = self.stack.pop(0).get_data()[0]
            self.stack.insert(0, Str(s))
        elif func_name == "Stern":
            s = self.stack.pop(0).get_data()[1:]
            self.stack.insert(0, Str(s))
        elif func_name == "Conc":
            s1 = self.stack.pop(0).get_data()
            s2 = self.stack.pop(0).get_data()
            self.control.pop()  
            self.stack.insert(0, Str(s1 + s2))
        elif func_name == "Order":
            tup = self.stack.pop(0)
            self.stack.insert(0, Int(str(len(tup.symbols))))
        elif func_name == "Isinteger":
            result = isinstance(self.stack[0], Int)
            self.stack[0] = Bool(str(result).lower())
        elif func_name == "Isstring":
            result = isinstance(self.stack[0], Str)
            self.stack[0] = Bool(str(result).lower())
        elif func_name == "Istuple":
            result = isinstance(self.stack[0], Tup)
            self.stack[0] = Bool(str(result).lower())
        elif func_name == "Isdummy":
            result = isinstance(self.stack[0], Dummy)
            self.stack[0] = Bool(str(result).lower())
        elif func_name == "Istruthvalue":
            result = isinstance(self.stack[0], Bool)
            self.stack[0] = Bool(str(result).lower())
        elif func_name == "Isfunction":
            result = isinstance(self.stack[0], Lambda)
            self.stack[0] = Bool(str(result).lower())
        # TODO: Implement Null and Itos if needed

    def apply_unary(self, rator, operand):
        """Apply unary operators: neg, not."""
        if rator.get_data() == "neg":
            return Int(str(-int(operand.get_data())))
        elif rator.get_data() == "not":
            val = operand.get_data() == "true"
            return Bool(str(not val).lower())
        else:
            return Err()

    def apply_binary(self, rator, operand1, operand2):
        """Apply binary operators: arithmetic, boolean, comparison, etc."""
        data = rator.get_data()
        if data in {"+", "-", "*", "/", "**"}:
            v1, v2 = int(operand1.get_data()), int(operand2.get_data())
            if data == "+": return Int(str(v1 + v2))
            if data == "-": return Int(str(v1 - v2))
            if data == "*": return Int(str(v1 * v2))
            if data == "/": return Int(str(v1 // v2))
            if data == "**": return Int(str(v1 ** v2))
        elif data in {"&", "or"}:
            v1 = operand1.get_data() == "true"
            v2 = operand2.get_data() == "true"
            if data == "&": return Bool(str(v1 and v2).lower())
            if data == "or": return Bool(str(v1 or v2).lower())
        elif data in {"eq", "ne", "ls", "le", "gr", "ge"}:
            v1, v2 = operand1.get_data(), operand2.get_data()
            if data == "eq": return Bool(str(v1 == v2).lower())
            if data == "ne": return Bool(str(v1 != v2).lower())
            v1, v2 = int(v1), int(v2)
            if data == "ls": return Bool(str(v1 < v2).lower())
            if data == "le": return Bool(str(v1 <= v2).lower())
            if data == "gr": return Bool(str(v1 > v2).lower())
            if data == "ge": return Bool(str(v1 >= v2).lower())
        elif data == "aug":
            if isinstance(operand2, Tup):
                operand1.symbols.extend(operand2.symbols)
            else:
                operand1.symbols.append(operand2)
            return operand1
        return Err()

    def tuple_to_string(self, tup):
        """Recursively convert a tuple to a string representation."""
        items = []
        for item in tup.symbols:
            if isinstance(item, Tup):
                items.append(self.tuple_to_string(item))
            else:
                items.append(item.get_data())
        return f"({', '.join(items)})"

    def get_result(self):
        """Run the CSE machine and return the final result as a string."""
        self.execute()
        top = self.stack[0]
        if isinstance(top, Tup):
            return self.tuple_to_string(top)
        return top.get_data()

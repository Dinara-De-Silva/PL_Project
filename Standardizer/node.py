class ASTNode:
    def __init__(self):
        self.data = None
        self.depth = 0
        self.parent = None
        self.children = []
        self.is_standardized = False

    # Basic accessors and mutators
    def set_data(self, node_data):
        self.data = node_data

    def get_data(self):
        return self.data

    def get_arity(self):
        return len(self.children)

    def get_children(self):
        return self.children

    def add_child(self, child_node):
        """Add a child node and set its parent reference."""
        self.children.append(child_node)
        child_node.set_parent(self)

    def set_depth(self, node_depth):
        self.depth = node_depth

    def get_depth(self):
        return self.depth

    def set_parent(self, parent_node):
        self.parent = parent_node

    def get_parent(self):
        return self.parent

    def standardize(self):
        """
        Standardize this node while recursively standardizing all children first.
        """
        if self.is_standardized:
            return

        # First standardize all children
        for child in self.children:
            child.standardize()

        # Apply standardization rules based on node type
        if self.data == "let":
            self._standardize_let()
        elif self.data == "where":
            self._standardize_where()
        elif self.data == "function_form":
            self._standardize_function_form()
        elif self.data == "lambda":
            self._standardize_lambda()
        elif self.data == "within":
            self._standardize_within()
        elif self.data == "@":
            self._standardize_at_operator()
        elif self.data == "and":
            self._standardize_simultaneous_def()
        elif self.data == "rec":
            self._standardize_recursive_def()

        self.is_standardized = True

    def _standardize_let(self):
        """
        Standardize LET node:
              LET              GAMMA
            /     \           /     \
           EQUAL   P   ->   LAMBDA   E
          /   \             /    \
         X     E           X      P 
        """
    
        expr = self.children[0].children[1]
        expr.set_parent(self)
        expr.set_depth(self.depth + 1)
        
        p_node = self.children[1]
        p_node.set_parent(self.children[0])
        p_node.set_depth(self.depth + 2)
        
        self.children[1] = expr
        self.children[0].set_data("lambda")
        self.children[0].children[1] = p_node
        self.set_data("gamma")

    def _standardize_where(self):
        """
        Standardize WHERE node:
              WHERE               GAMMA
              /   \             /     \
             P    EQUAL   ->  LAMBDA   E
                  /   \       /   \
                 X     E     X     P
        """
        self.children[0], self.children[1] = self.children[1], self.children[0]
        self.set_data("let")
        self.standardize()

    def _standardize_function_form(self):
        """
        Standardize FCN_FORM node:
              FCN_FORM                EQUAL
              /   |   \              /    \
             P    V+   E    ->      P     +LAMBDA
                                          /     \
                                          V     .E
        """
        expr = self.children[-1]
        current_lambda = NodeFactory.create_node_with_parent(
            "lambda", self.depth + 1, self, [], True)

        self.children.insert(1, current_lambda)

        i = 2
        while self.children[i] != expr:
            var = self.children[i]
            self.children.pop(i)
            var.set_depth(current_lambda.depth + 1)
            var.set_parent(current_lambda)
            current_lambda.children.append(var)

            if len(self.children) > 3:
                current_lambda = NodeFactory.create_node_with_parent(
                    "lambda", current_lambda.depth + 1, 
                    current_lambda, [], True)
                current_lambda.get_parent().children.append(current_lambda)

        current_lambda.children.append(expr)
        self.children.pop(2)
        self.set_data("=")

    def _standardize_lambda(self):
        """
        Standardize LAMBDA node with multiple variables:
            LAMBDA        ++LAMBDA
             /   \   ->   /    \
            V++   E      V     .E
        """
        if len(self.children) > 2:
            expr = self.children[-1]
            current_lambda = NodeFactory.create_node_with_parent(
                "lambda", self.depth + 1, self, [], True)
            self.children.insert(1, current_lambda)

            i = 2
            while self.children[i] != expr:
                var = self.children[i]
                self.children.pop(i)
                var.set_depth(current_lambda.depth + 1)
                var.set_parent(current_lambda)
                current_lambda.children.append(var)

                if len(self.children) > 3:
                    current_lambda = NodeFactory.create_node_with_parent(
                        "lambda", current_lambda.depth + 1, 
                        current_lambda, [], True)
                    current_lambda.get_parent().children.append(current_lambda)

            current_lambda.children.append(expr)
            self.children.pop(2)

    def _standardize_within(self):
        """
        Standardize WITHIN node:
                  WITHIN                  EQUAL
                 /      \                /     \
               EQUAL   EQUAL    ->      X2     GAMMA
              /    \   /    \                  /    \
             X1    E1 X2    E2               LAMBDA  E1
                                            /    \
                                           X1    E2
        """
        x1, e1 = self.children[0].children
        x2, e2 = self.children[1].children
        
        gamma = NodeFactory.create_node_with_parent(
            "gamma", self.depth + 1, self, [], True)
        lambda_node = NodeFactory.create_node_with_parent(
            "lambda", self.depth + 2, gamma, [], True)
        
        x1.set_depth(x1.get_depth() + 1)
        x1.set_parent(lambda_node)
        x2.set_depth(x1.get_depth() - 1)
        x2.set_parent(self)
        e1.set_depth(e1.get_depth())
        e1.set_parent(gamma)
        e2.set_depth(e2.get_depth() + 1)
        e2.set_parent(lambda_node)
        
        lambda_node.children.extend([x1, e2])
        gamma.children.extend([lambda_node, e1])
        self.children = [x2, gamma]
        self.set_data("=")

    def _standardize_at_operator(self):
        """
        Standardize @ node:
                AT              GAMMA
              / | \    ->       /    \
             E1 N E2          GAMMA   E2
                             /    \
                            N     E1
        """
        e1, n, e2 = self.children
        gamma = NodeFactory.create_node_with_parent(
            "gamma", self.depth + 1, self, [], True)
        
        e1.set_depth(e1.get_depth() + 1)
        e1.set_parent(gamma)
        n.set_depth(n.get_depth() + 1)
        n.set_parent(gamma)
        
        gamma.children.extend([n, e1])
        self.children = [gamma, e2]
        self.set_data("gamma")

    def _standardize_simultaneous_def(self):
        """
        Standardize AND node:
                SIMULTDEF            EQUAL
                    |               /     \
                  EQUAL++  ->     COMMA   TAU
                  /   \             |      |
                 X     E           X++    E++
        """
        comma = NodeFactory.create_node_with_parent(
            ",", self.depth + 1, self, [], True)
        tau = NodeFactory.create_node_with_parent(
            "tau", self.depth + 1, self, [], True)

        for equal_node in self.children:
            x, e = equal_node.children
            x.set_parent(comma)
            e.set_parent(tau)
            comma.children.append(x)
            tau.children.append(e)

        self.children = [comma, tau]
        self.set_data("=")

    def _standardize_recursive_def(self):
        """
        Standardize REC node:
               REC                 EQUAL
                |                 /     \
              EQUAL     ->       X     GAMMA
             /     \                   /    \
            X       E                YSTAR  LAMBDA
                                            /     \
                                            X      E
        """
        x, e = self.children[0].children
        x_copy = NodeFactory.create_node_with_parent(
            x.get_data(), self.depth + 1, self, x.children, True)
        gamma = NodeFactory.create_node_with_parent(
            "gamma", self.depth + 1, self, [], True)
        ystar = NodeFactory.create_node_with_parent(
            "<Y*>", self.depth + 2, gamma, [], True)
        lambda_node = NodeFactory.create_node_with_parent(
            "lambda", self.depth + 2, gamma, [], True)

        x.set_depth(lambda_node.depth + 1)
        x.set_parent(lambda_node)
        e.set_depth(lambda_node.depth + 1)
        e.set_parent(lambda_node)
        
        lambda_node.children.extend([x, e])
        gamma.children.extend([ystar, lambda_node])
        self.children = [x_copy, gamma]
        self.set_data("=")


class NodeFactory:
    
    @staticmethod
    def create_node(node_data, depth):
        """Create a basic node with given data and depth."""
        node = ASTNode()
        node.set_data(node_data)
        node.set_depth(depth)
        return node

    @staticmethod
    def create_node_with_parent(node_data, depth, parent, children, is_standardized):
        """
        Create a node with all relationships pre-configured.
        
        Args:
            node_data: Content of the node
            depth: Depth in the tree
            parent: Parent node reference
            children: List of child nodes
            is_standardized: Standardization status
            
        Returns:
            ASTNode: Configured node instance
        """
        node = ASTNode()
        node.set_data(node_data)
        node.set_depth(depth)
        node.set_parent(parent)
        node.children = children
        node.is_standardized = is_standardized
        return node
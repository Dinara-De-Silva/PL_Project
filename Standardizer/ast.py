class AbstractSyntaxTree:
    def __init__(self, root=None):
        self.root = root

    def set_root(self, root_node):
        self.root = root_node

    def get_root(self):
        return self.root

    def standardize(self):
        """
        Standardize the AST by applying standardization rules to all nodes.
        Only standardizes if the root hasn't been standardized yet.
        """
        if not self.root.is_standardized:
            self.root.standardize()

    def _traverse_pre_order(self, node, indent_level):
        """
        Recursively traverse the AST in pre-order and print with indentation.
        
        Args:
            node: Current node being processed
            indent_level: Current indentation level for pretty printing
        """
        print("." * indent_level + str(node.get_data()))
        for child in node.get_children():
            self._traverse_pre_order(child, indent_level + 1)

    def print_st(self):
        """Print the AST structure using pre-order traversal."""
        self._traverse_pre_order(self.get_root(), 0)
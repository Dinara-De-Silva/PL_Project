from .node import NodeFactory
from .ast import AbstractSyntaxTree

class ASTBuilder:
    def __init__(self):
        pass

    def build_ast(self, parse_data):
        """
        Construct an AST from the parser's output data.
        
        Args:
            parse_data: List of strings representing the parsed structure
            
        Returns:
            AbstractSyntaxTree: The constructed AST
        """
        # Create root node from first element
        root = NodeFactory.create_node(parse_data[0], 0)
        previous_node = root
        current_depth = 0

        for item in parse_data[1:]:
            # Compute depth by counting leading dots
            depth = len(item) - len(item.lstrip('.'))
            # Extract the actual label for the node
            label = item[depth:]

            current_node = NodeFactory.create_node(label, depth)


            if current_depth < depth:
                # Current node is child of previous node
                previous_node.add_child(current_node)
            else:
                # Find appropriate parent at current depth
                while previous_node.get_depth() != depth:
                    previous_node = previous_node.get_parent()
                previous_node.get_parent().add_child(current_node)

            previous_node = current_node
            current_depth = depth

        return AbstractSyntaxTree(root)
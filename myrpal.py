import argparse
from Parser.parser import Parser
from Lexer.tokenizer import tokenizer
from Standerizer.ast_builder import ASTBuilder
from CSEM.csemachine import CSEMachine
from CSEM.control_structures import ControlStructures
import traceback

def main():
    parser = argparse.ArgumentParser(description='Process some RPAL files.')
    parser.add_argument('file_name', type=str, help='The RPAL program input file')
    parser.add_argument('-ast', action='store_true', help='Print the abstract syntax tree')
    
    args = parser.parse_args()

    input_file = open(args.file_name, "r")
    input_text = input_file.read()
    input_file.close()
    
    # Tokenize the input text
    tokens = tokenizer(input_text)

    try:
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        if ast_nodes is None:
            return
        
        # Abstract Syntax Tree 
        string_ast = parser.print_ast()
        if args.ast:
            for string in string_ast:
                print(string)
            return
        
        # Standardized Tree 
        ast_factory = ASTBuilder()
        ast = ast_factory.build_ast(string_ast)
        ast.standardize()
       
        # Interpret the ST using CSE Machine
        cse_machine_factory = ControlStructures()
        cse_machine = cse_machine_factory.create_cse_machine(ast)
        
        # Print the final output
        print("Output of the above program is:")
        print(cse_machine.get_result().replace("\\n", "\n"))
        

    except Exception as e:
        print(e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
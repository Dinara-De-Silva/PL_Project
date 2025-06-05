PYTHON = python3

# Run the RPAL processor
run:
	@$(PYTHON) myrpal.py $(FILE)

# Print the Abstract Syntax Tree (AST)
ast:
	@$(PYTHON) myrpal.py $(FILE) -ast

# Print the Standardized AST
sast:
	@$(PYTHON) myrpal.py $(FILE) -sast

# Clean up generated files
clean:
	@rm -rf __pycache__ *.pyc

# Prevent conflicts with filenames
.PHONY: run ast sast clean

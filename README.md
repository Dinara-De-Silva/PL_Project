# RPAL Interpreter

## CS3513 – Programming Languages  
**Group Name**: AST  
**Group Members**:  
- De Silva A.D.D.T.
- Gunarathna H.R.A.

---

## 📌 Project Overview

This project is an interpreter for the **RPAL (Right-reference Pedagogic Language)**, a functional language used for educational purposes. The interpreter is implemented in **Python** from scratch.

It consists of the following core components:
- **Lexical Analyzer (Lexer)**: Converts source code into tokens.
- **Parser**: Builds the Abstract Syntax Tree (AST).
- **Standardizer**: Converts AST to a Standardized Tree (ST).
- **CSE Machine**: Evaluates the ST to produce the final output.

---

## 🛠️ Technologies Used

- **Language**: Python  
- **IDE**: Visual Studio Code  
- **Version Control**: Git & GitHub  

---

## 📂 Project Structure
├── Lexer                        # Performs lexical analysis and token generation  
│   └── lexer.py  
├── Parser                       # Parses tokens to build the Abstract Syntax Tree (AST)  
│   └── parser.py  
├── Standardizer                 # Converts AST into a Standardized Tree (ST)  
│   ├── ast_builder.py  
│   ├── ast.py  
│   └── node.py  
├── CSEM                         # Implements the Control Stack Environment (CSE) machine to evaluate the ST  
│   ├── control_structure.py  
│   ├── csemachine.py  
│   └── nodes.py  
├── myrpal.py                    # Main entry point; processes arguments and orchestrates execution  



## 🔧 Project Setup

Follow the steps below to set up and run the project on your local machine.

### 1️⃣ Prerequisites

- Python 3.x installed  
- Git installed (optional, for cloning the repository)

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/Dinara-De-Silva/PL_Project.git
cd PL_Project
```
###3️⃣ Run the Interpreter
You can run the interpreter with an RPAL source file as input:
#### For normal execution (prints output)
```bash
python myrpal.py file_name
```

#### For AST only output
```bash
python myrpal.py file_name -ast
```





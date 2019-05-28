# Compilers Project
_C(-ish) compiler made for a Compilers course by Jonathan Meyer & Sergio Fenoll._

This document contains an overview of the project structure, as well as an overview of the implemented features and instruction on how to build the project itself.

As of the time of writing, the 21st of April 2019, a number of the mandatory requirements haven't been fully implemented yet. During the week of the 22nd of April, we will continue work on the compiler and we expect to finish a large part of these requirements by the day of the evaluation.

## Project structure
**`parser/`:**

This folder contains the files generated by the ANTLR. These files are provided in case one cannot/does not wish to generate the ANTLR grammar themselves.

**`AST/AST.py`:**

This file contains all the different nodes our AST can contain. Instead of treating each AST node purely as a container that links to its parent and children and with basic information, each different kind of node contains specific information. This is especially helpful when doing operations on the nodes themselves (i.e. optimisations or code generation) since a node with more topical information can do more without requiring information from adjacent nodes.

**`AST/STT.py`:**

In this file, the structure of Symbol Tables is defined. We decided to store our Symbol Tables in a tree structure that mimics the different scopes. Anytime a new scope is opened, a new symbol table is generated and linked as necessary. `STTNodes` consist of some information required for e.g. dotfile generation as well as a python `dict` that maps identifiers to `STTEntries`. These entries contain information about the symbols.

**`AST/ASTBuilder.py`:**

This is our implementation of the ANTLR Listener that we utilise to create the AST.

## Implemented features

### LLVM:
- Types: `char`, `float`, `int`
- Reserved words: `if` `else`, `return`, `while`, `for`, `break`, `continue`
- Functions:
  - Function definitions
- Local and global variables
- Operations:
  - Arithmetic operators: `+`, `-`, `*`, `/`, `%`
  - Comparison operators: `>`, `<`, `!=`, `==`, `>=`, `<=`
  - Logical operators: `&&`, `||`
  - Assignment operators: `=`, `+=`, `-=`, `*=`, `/=`
- Arrays:
  - 1-dimensional arrays
  - Array initialization (using initializer lists `{}`)
  - Array access
- Comments
  - Line comments `//`
  - Block comments `/* */`
    
### Error analysis:
- Typechecking (warning/errors for unsupported operand types)

### Optimisations:
- Unreachable/dead code:
  - No code after return
  - No code after break/continue
- Constant folding and propagation
- No declarations/assignments for unused variables

### Testfiles:

- additiveOperationsTest, multiplicativeOperationsTest --> operations
- declarationsTest, variableScope --> variables, scopes
- ifElseTest --> if-else
- full --> all of the implemented features

## Requirements & Build process

Requirements:
- `antlr4`
- `antlr4-python3-runtime`
- `graphviz`
- `python3 (v3.6 or higher)`

The shell script `build` will generate the ANTLR grammar using the `C.g4` file, afterwards it will parse a default C file and output a dotfile visualization of the generated AST and STT as well as the LLVM code using `c2llvm.py`. Finally, the dotfiles are generated using `graphviz` and the images will be found in the root directory as `ast.png` and `stt.png` respectively.

You can execute this shell script file by typing `./build` in the root directory of the project.

The shell script `test` will parse all the C files in the directory `testfiles/`, output dotfiles and LLVM code for each file and generate the images of each tree.

You can execute this shell script by typing `./test` in the root directory of the project.

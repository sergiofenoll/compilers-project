# compilers-project
C(-ish) compiler made for a Compilers course

## Implemented features (LLVM):
- Types: char, float, int
- Reserved words: if-elseif-else, return
- Local and global variables
- Comments
- Operations:
    - Binary operators (+, -, *, /)
    - Comparison operators (>, <, !=, ==, >=, <=)
- Functions:
    - Function definitions
- Arrays:
    - Access?
    
## Error analysis:
- Typechecking

## Optimisations:
- Unreachable/dead code:
    - No code after return
    - No code after break/continue
    - No code for unused variables

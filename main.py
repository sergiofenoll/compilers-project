import sys
import AST.AST as AST
import AST.STT as STT
from AST.ASTBuilderListener import ASTBuilder
from antlr4 import *
from parser.CLexer import CLexer
from parser.CParser import CParser


def optimise_ast(ast):

    # Applies the following optimisations where possible:
    #   - Remove code that comes after return, break or continue
    #   - Remove declarations for unused variables
    #   - Fold constants
    #   - Remove useless code: arithmetic expressions that evaluate to known values

    stack = list()
    queue = list()
    queue.append(ast)

    while queue:
        node = queue.pop(0)
        stack.append(node)
        for child in node.children[::-1]:
            queue.append(child)
    
    while stack:
        node = stack.pop()
        node.optimise()


def generate_llvm_ir(ast, output):
    stack = list()
    parent_stack = list()
    stack.append(ast)
    while stack:
        node = stack.pop()
        prefix = node.generateLLVMIRPrefix()
        output.write(prefix)
        parent_stack.append(node)
        for child in node.children[::-1]:
            stack.append(child)
        while parent_stack:
            last_parent = parent_stack[-1]
            if not last_parent.children or last_parent.children[-1] == node:
                node = parent_stack.pop()
                postfix = node.generateLLVMIRPostfix()
                output.write(postfix)
            else:
                break


def type_checking(ast):
    stack = list()
    stack.append(ast)

    while stack:
        node = stack.pop()
        for child in node.children:
            stack.append(child)


def main(argv):
    file_input = FileStream(argv[1])
    lexer = CLexer(file_input)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)

    tree = parser.compilationUnit()

    stt = STT.STTNode()
    ast = AST.ASTBaseNode("Root", stt)

    builder = ASTBuilder(ast)
    walker = ParseTreeWalker()
    walker.walk(builder, tree)

    type_checking(ast)
    optimise_ast(ast)
    ast.generateDot(open("ast.dot", "w"))
    stt.generateDot(open("stt.dot", "w"))
    generate_llvm_ir(ast, open("ir.ll", "w"))

    print("")


if __name__ == '__main__':
    main(sys.argv)

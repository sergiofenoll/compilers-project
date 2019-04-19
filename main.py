import sys
import AST.AST as AST
import AST.STT as STT
import textwrap
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


def generateLLVMIR(ast, filename = None):

    filename = filename or "LLVMIR.ll"
    with open(filename, "w") as outf:
        stack = list()
        stack.append(ast)
        parentstack = list()
        while stack:
            node = stack.pop()
            prefix = node.generateLLVMIRPrefix()
            outf.write(prefix)
            if len(node.children):
                parentstack.append(node)
                for child in node.children[::-1]:
                    stack.append(child)
            while len(parentstack):
                if parentstack[-1].children[-1] == node:
                    node = parentstack.pop()
                    postfix = node.generateLLVMIRPostfix()
                    outf.write(postfix)
                else:
                    break

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
    optimise_ast(ast)
    generateLLVMIR(ast)

    ast.generateDot(open("ast.dot", "w"))
    stt.generateDot(open("stt.dot", "w"))


if __name__ == '__main__':
    main(sys.argv)

import sys
import AST.AST as AST
import AST.STT as STT
import textwrap
from AST.ASTBuilderListener import ASTBuilder
from antlr4 import *
from parser.CLexer import CLexer
from parser.CParser import CParser


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

    ast.generateDot(open("ast.dot", "w"))
    stt.generateDot(open("stt.dot", "w"))

    #


if __name__ == '__main__':
    main(sys.argv)

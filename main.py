import sys
from antlr4 import *
from parser.CLexer import CLexer
from parser.CParser import CParser
from parser.CVisitor import CVisitor

def main(argv):
    input = FileStream(argv[1])
    lexer = CLexer(input)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)
    tree = parser.compilationUnit()

    for child in tree.children:
        print(type(child))

if __name__ == '__main__':
    main(sys.argv)

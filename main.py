import sys
from antlr4 import *
from parser.CLexer import CLexer
from parser.CParser import CParser
from parser.CListener import CListener

def main(argv):
    input = FileStream(argv[1])
    lexer = CLexer(input)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)
    tree = parser.compilationUnit()

if __name__ == '__main__':
    main(sys.argv)

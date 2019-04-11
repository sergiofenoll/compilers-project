import sys
from antlr4 import *
from cLexer import cLexer
from cParser import cParser
from cListener import cListener

def main(argv):
    input = FileStream(argv[1])
    lexer = cLexer(input)
    stream = CommonTokenStream(lexer)
    parser = cParser(stream)
    tree = parser.program()

if __name__ == '__main__':
    main(sys.argv)

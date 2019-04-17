import sys
import AST.AST as AST
import AST.STT as STT
import textwrap
from AST.ASTBuilderListener import ASTBuilder
from antlr4 import *
from parser.CLexer import CLexer
from parser.CParser import CParser

def main(argv):
    input = FileStream(argv[1])
    lexer = CLexer(input)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)
    tree = parser.compilationUnit()
    stt = STT.STTNode()
    ast = AST.ASTBaseNode("Root", stt)

    builder = ASTBuilder(ast)
    walker = ParseTreeWalker()
    walker.walk(builder, tree)

    ptv = ParseTreeVisualizer(stt)
    print(ptv.gendot())


class ParseTreeVisualizer():
    def __init__(self, ast):
        self.ast = ast
        self.ncount = 1
        self.dot_header = [textwrap.dedent("""\
        digraph astgraph {
          node [shape=none, fontsize=12, fontname="Courier", height=.1];
          ranksep=.3;
          edge [arrowsize=.5]
        """)]
        self.dot_body = []
        self.dot_footer = ['}']

    def bfs(self, node):
        ncount = 1
        queue = []
        queue.append(node)
        s = '  node{} [label="{}"]\n'.format(ncount, node.name)
        self.dot_body.append(s)
        node._num = ncount
        ncount += 1

        while queue:
            node = queue.pop(0)
            for child_node in node.children:
                s = '  node{} [label="{}"]\n'.format(ncount, child_node.name)
                self.dot_body.append(s)
                child_node._num = ncount
                ncount += 1
                s = '  node{} -> node{}\n'.format(node._num, child_node._num)
                self.dot_body.append(s)
                queue.append(child_node)

    def gendot(self):
        self.bfs(self.ast)
        return ''.join(self.dot_header + self.dot_body + self.dot_footer)

if __name__ == '__main__':
    main(sys.argv)

import parser.CParser as CParser
import AST


def makeASTNode(parseTree):

    # Returns the appropriate ASTNode for a given context

    idx = parseTree.getRuleIndex()
    rule = CParser.ruleNames[idx]

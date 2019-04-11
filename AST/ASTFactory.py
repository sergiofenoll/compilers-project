import parser.CParser as CParser
import AST


def makeASTNode(ctx):

    # Returns the appropriate ASTNode for a given context

    idx = ctx.getRuleIndex()
    rule = CParser.ruleNames[idx]

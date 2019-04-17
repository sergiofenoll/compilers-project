import AST.AST as AST
from parser.CParser import CParser
from parser.CListener import CListener


class ASTBuilder(CListener):
    def __init__(self, root):
        self.tree = root
        self.current_node = root

    def enterIdentifier(self, ctx:CParser.IdentifierContext):
        node = AST.ASTIdentifierNode(ctx.Identifier())
        node.parent = self.current_node
        self.current_node.children.append(node)

    def enterConstant(self, ctx:CParser.ConstantContext):
        node = AST.ASTConstantNode(ctx.Constant())
        node.parent = self.current_node
        self.current_node.children.append(node)

    def enterStringLiteral(self, ctx:CParser.StringLiteralContext):
        node = AST.ASTStringLiteralNode(ctx.StringLiteral())
        node.parent = self.current_node
        self.current_node.children.append(node)

    def enterAssignment(self, ctx:CParser.AssignmentContext):
        node = AST.ASTBinaryOpNode("Assignment")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitAssignment(self, ctx:CParser.AssignmentContext):
        self.current_node = self.current_node.parent

    def enterArrayAccess(self, ctx:CParser.ArrayAccessContext):
        node = AST.ASTArrayAccessNode()
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitArrayAccess(self, ctx:CParser.ArrayAccessContext):
        self.current_node = self.current_node.parent

    def enterFunctionCall(self, ctx:CParser.FunctionCallContext):
        node = AST.ASTFunctionCallNode()
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitFunctionCall(self, ctx:CParser.FunctionCallContext):
        self.current_node = self.current_node.parent

    def enterPostfixIncrement(self, ctx:CParser.PostfixIncrementContext):
        node = AST.ASTPostfixIncrementNode()
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitPostfixIncrement(self, ctx:CParser.PostfixIncrementContext):
        self.current_node = self.current_node.parent

    def enterPostfixDecrement(self, ctx:CParser.PostfixDecrementContext):
        node = AST.ASTPostfixDecrementNode()
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitPostfixDecrement(self, ctx:CParser.PostfixDecrementContext):
        self.current_node = self.current_node.parent

    def enterPrefixIncrement(self, ctx:CParser.PrefixIncrementContext):
        node = AST.ASTPrefixIncrementNode()
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitPrefixIncrement(self, ctx:CParser.PrefixIncrementContext):
        self.current_node = self.current_node.parent

    def enterPrefixDecrement(self, ctx:CParser.PrefixDecrementContext):
        node = AST.ASTPrefixDecrementNode()
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitPrefixDecrement(self, ctx:CParser.PrefixDecrementContext):
        self.current_node = self.current_node.parent

    def enterUnary(self, ctx:CParser.UnaryContext):
        operator = str(ctx.children[0])  # First token
        if operator == "+":
            op_type = "UnaryPlus"
        elif operator == "-":
            op_type = "UnaryMinus"
        elif operator == "!":
            op_type = "LogicalNegation"
        elif operator == "*":
            op_type = "Indirection"
        else:
            op_type = "UnknownUnary"
        node = AST.ASTUnaryOpNode(op_type)
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitUnary(self, ctx:CParser.UnaryContext):
        self.current_node = self.current_node.parent

    def enterCast(self, ctx:CParser.CastContext):
        node = AST.ASTUnaryOpNode("Cast")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitCast(self, ctx:CParser.CastContext):
        self.current_node = self.current_node.parent

    def enterMultiplication(self, ctx:CParser.MultiplicationContext):
        node = AST.ASTBinaryOpNode("Multiplication")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitMultiplication(self, ctx:CParser.MultiplicationContext):
        self.current_node = self.current_node.parent

    def enterDivision(self, ctx:CParser.DivisionContext):
        node = AST.ASTBinaryOpNode("Division")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitDivision(self, ctx:CParser.DivisionContext):
        self.current_node = self.current_node.parent

    def enterModulo(self, ctx:CParser.ModuloContext):
        node = AST.ASTBinaryOpNode("Modulo")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitModulo(self, ctx:CParser.ModuloContext):
        self.current_node = self.current_node.parent

    def enterAddition(self, ctx:CParser.AdditionContext):
        node = AST.ASTBinaryOpNode("Addition")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitAddition(self, ctx:CParser.AdditionContext):
        self.current_node = self.current_node.parent

    def enterSubtraction(self, ctx:CParser.SubtractionContext):
        node = AST.ASTBinaryOpNode("Subtraction")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitSubtraction(self, ctx:CParser.SubtractionContext):
        self.current_node = self.current_node.parent

    def enterSmallerThan(self, ctx:CParser.SmallerThanContext):
        node = AST.ASTBinaryOpNode("SmallerThan")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitSmallerThan(self, ctx:CParser.SmallerThanContext):
        self.current_node = self.current_node.parent

    def enterLargerThan(self, ctx:CParser.LargerThanContext):
        node = AST.ASTBinaryOpNode("LargerThan")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitLargerThan(self, ctx:CParser.LargerThanContext):
        self.current_node = self.current_node.parent

    def enterSmallerThanOrEqual(self, ctx:CParser.SmallerThanOrEqualContext):
        node = AST.ASTBinaryOpNode("SmallerThanOrEqual")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitSmallerThanOrEqual(self, ctx:CParser.SmallerThanOrEqualContext):
        self.current_node = self.current_node.parent

    def enterLargerThanOrEqual(self, ctx:CParser.LargerThanOrEqualContext):
        node = AST.ASTBinaryOpNode("LargerThanOrEqual")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitLargerThanOrEqual(self, ctx:CParser.LargerThanOrEqualContext):
        self.current_node = self.current_node.parent

    def enterEquals(self, ctx:CParser.EqualsContext):
        node = AST.ASTBinaryOpNode("Equals")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitEquals(self, ctx:CParser.EqualsContext):
        self.current_node = self.current_node.parent

    def enterNotEquals(self, ctx:CParser.NotEqualsContext):
        node = AST.ASTBinaryOpNode("NotEquals")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitNotEquals(self, ctx:CParser.NotEqualsContext):
        self.current_node = self.current_node.parent

    def enterLogicalAnd(self, ctx:CParser.LogicalAndContext):
        node = AST.ASTBinaryOpNode("LogicalAnd")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitLogicalAnd(self, ctx:CParser.LogicalAndContext):
        self.current_node = self.current_node.parent

    def enterLogicalOr(self, ctx:CParser.LogicalOrContext):
        node = AST.ASTBinaryOpNode("LogicalOr")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitLogicalOr(self, ctx:CParser.LogicalOrContext):
        self.current_node = self.current_node.parent

    def enterConditional(self, ctx:CParser.ConditionalContext):
        node = AST.ASTIfStmtNode("Conditional")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitConditional(self, ctx:CParser.ConditionalContext):
        self.current_node = self.current_node.parent

    def enterExpressionList(self, ctx:CParser.ExpressionListContext):
        node = AST.ASTExprListNode("ExpressionList")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitExpressionList(self, ctx:CParser.ExpressionListContext):
        self.current_node = self.current_node.parent

    def enterTypeSpecifier(self, ctx:CParser.TypeSpecifierContext):
        tspec = str(ctx.children[0])
        node = AST.ASTTypeSpecifierNode(tspec)
        node.parent = self.current_node
        self.current_node.children.append(node)

    def enterDirectDeclarator(self, ctx:CParser.DirectDeclaratorContext):
        if ctx.Identifier():
            node = AST.ASTIdentifierNode(ctx.Identifier())
            node.parent = self.current_node
            self.current_node.children.append(node)

    def enterPointer(self, ctx:CParser.PointerContext):
        pass

    def exitPointer(self, ctx:CParser.PointerContext):
        pass

    def enterLabeledStatement(self, ctx:CParser.LabeledStatementContext):
        label = ctx.Identifier() or ctx.Case() or ctx.Default()
        node = AST.ASTLabelStmtNode(label)
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitLabeledStatement(self, ctx:CParser.LabeledStatementContext):
        self.current_node = self.current_node.parent

    def enterSelectionStatement(self, ctx:CParser.SelectionStatementContext):
        node = AST.ASTBaseNode("")
        if ctx.If():
            node = AST.ASTIfStmtNode("If")
        elif ctx.Switch():
            node = AST.ASTSwitchStmtNode("Switch")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitSelectionStatement(self, ctx:CParser.SelectionStatementContext):
        self.current_node = self.current_node.parent

    def enterParameterTypeList(self, ctx:CParser.ParameterTypeListContext):
        node = AST.ASTBaseNode("Arguments")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitParameterTypeList(self, ctx:CParser.ParameterTypeListContext):
        self.current_node = self.current_node.parent

    def enterIterationStatement(self, ctx:CParser.IterationStatementContext):
        if ctx.For():
            node = AST.ASTForStmtNode("For")
            node.parent = self.current_node
            self.current_node.children.append(node)
            self.current_node = node
        elif ctx.While():
            pass

    def exitIterationStatement(self, ctx:CParser.IterationStatementContext):
        self.current_node = self.current_node.parent

    def enterJumpStatement(self, ctx:CParser.JumpStatementContext):
        jump = ctx.Goto() or ctx.Continue() or ctx.Break() or ctx.Return()
        node = AST.ASTJumpStmtNode(jump)
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitJumpStatement(self, ctx:CParser.JumpStatementContext):
        self.current_node = self.current_node.parent

    def enterCompoundStatement(self, ctx:CParser.CompoundStatementContext):
        node = AST.ASTCompoundStmtNode("CompoundStatement")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitCompoundStatement(self, ctx:CParser.CompoundStatementContext):
        self.current_node = self.current_node.parent

    def enterDeclaration(self, ctx:CParser.DeclarationContext):
        node = AST.ASTDeclarationNode("Declaration")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitDeclaration(self, ctx:CParser.DeclarationContext):
        self.current_node = self.current_node.parent

    def enterFunctionDefinition(self, ctx:CParser.FunctionDefinitionContext):
        node = AST.ASTFunctionDefinitionNode("FunctionDefinition")
        node.parent = self.current_node
        self.current_node.children.append(node)
        self.current_node = node

    def exitFunctionDefinition(self, ctx:CParser.FunctionDefinitionContext):
        self.current_node = self.current_node.parent
